#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>
#include <mpi.h>
#include <sys/resource.h>

# define version 1

int maxwords = 50000;
int maxlines;
int nwords;
int nlines;
int err, *count, nthreads = 1;
double tstart, ttotal;
FILE *fd;
char **word, **line;
char *key_array;
long key_array_size;
int filenumber;
char newword[15], hostname[256],filename[256];

/* myclock: (Calculates the time)
--------------------------------------------*/

double myclock() {
	static time_t t_start = 0;  // Save and subtract off each time

	struct timespec ts;
	clock_gettime(CLOCK_REALTIME, &ts);
	if( t_start == 0 ) t_start = ts.tv_sec;

	return (double) (ts.tv_sec - t_start) + ts.tv_nsec * 1.0e-9;
}

/* init_list: (Initaite word list and lines)
--------------------------------------------*/
void init_list(void *rank)
{
	// Malloc space for the word list and lines
	int i;
	int myID =  *((int*) rank);
	word = (char **) malloc( maxwords * sizeof( char * ) );
	count = (int *) malloc( maxwords * sizeof( int ) );
	for( i = 0; i < maxwords; i++ ) {
		word[i] = malloc( 10 );
		count[i] = 0;
	}

	line = (char **) malloc( maxlines * sizeof( char * ) );
	for( i = 0; i < maxlines; i++ ) {
		line[i] = malloc( 2001 );
	}

    key_array_size = 1000*maxlines;
 	key_array = malloc(sizeof(char)*key_array_size); 
 	key_array[0] = '\0';
}


/* read_dict_words: (Read Dictianary words)
--------------------------------------------*/
void read_dict_words()
{
// Read in the dictionary words
	fd = fopen("625/keywords.txt", "r" );
	nwords = -1;
	do {
		err = fscanf( fd, "%[^\n]\n", word[++nwords] );
	} while( err != EOF && nwords < maxwords );
	fclose( fd );

	//printf( "Read in %d words\n", nwords);
}


/* read_lines: (Read wiki lines)
--------------------------------------------*/
void read_lines()
{
// Read in the lines from the data file
	double nchars = 0;
	fd = fopen( "625/wiki_dump.txt", "r" );
	nlines = -1;
	do {
		err = fscanf( fd, "%[^\n]\n", line[++nlines] );
		if( line[nlines] != NULL ) nchars += (double) strlen( line[nlines] );
	} while( err != EOF && nlines < maxlines);
	fclose( fd );

	//printf( "Read in %d lines averaging %.0lf chars/line\n", nlines, nchars / nlines);
}

/* reset_file: (create an output file)
--------------------------------------------*/
void *reset_file()
{
	snprintf(filename,250,"wiki-mpi-%d.out", filenumber);
	fd = fopen(filename, "w" );
	fclose( fd );
}

/* count_words: (count the words)
--------------------------------------------*/
void *count_words(void *rank)
{
	int i,k;
	int myID =  *((int*) rank);
	int startPos = ((long) myID) * (nwords / nthreads);
	int endPos = startPos + (nwords / nthreads);

	for( i = startPos; i < endPos; i++ ) {
		for( k = 0; k < nlines; k++ ) {
			if( strstr( line[k], word[i] ) != NULL ) 
			{
				if (count[i] == 0)
				{
					snprintf(newword,8,"%s:",word[i]);
					strcat(key_array,newword);
				}
				count[i]++; 
				snprintf(newword,8,"%d,",k);
				strcat(key_array,newword);
			}
		}
		//if (i % 1000 == 0) printf("Loop %d of %d done\n", i, nwords);
		if (count[i] != 0)
		{
			snprintf(newword,5,"\n");
			strcat(key_array,newword);
  		}
	}

	//printf("%s\n",key_array);
}


/* dump_words: (write the output on file)
--------------------------------------------*/
void *dump_words()
{
	fd = fopen(filename, "a" );
	int results =fputs(key_array,fd);
	fclose( fd );
}


/*--------------------------------------------------
						Main 
--------------------------------------------------*/

int main(int argc, char* argv[]) 
{

	int i, rc;
	int numtasks, rank;
	double tstart_init, tend_int, tstart_count, tend_count, tend_reduce;
  	struct rusage ru;

	MPI_Status Status;
	maxlines = 100000; // Default Value
	filenumber = rand() %100000;
	if (argc >= 2){
		maxlines = atol(argv[1]);
		filenumber = atol(argv[2]);
	}

	rc = MPI_Init(&argc,&argv);
	if (rc != MPI_SUCCESS){
		printf ("Error starting MPI program. Terminating.\n");
		MPI_Abort(MPI_COMM_WORLD, rc);
	}

    MPI_Comm_size(MPI_COMM_WORLD,&numtasks); // Number of cores
    MPI_Comm_rank(MPI_COMM_WORLD,&rank);	 // rank of each core
	nthreads = numtasks;

	gethostname(hostname,255);
	if(rank == nthreads-1) reset_file(); // The last core will reset the output file 
	MPI_Bcast(filename, 256, MPI_CHAR, nthreads-1, MPI_COMM_WORLD); // send the name of the output file to all cores
	tstart = myclock(); // Global Clock

	// Initialization 
   	tstart_init = MPI_Wtime();  // Private Clock for each core
	init_list(&rank);
	read_dict_words();
	read_lines();
	tend_int   = MPI_Wtime();

    getrusage(RUSAGE_SELF, &ru);
    long MEMORY_USAGE = ru.ru_maxrss;   // Memory usage in Kb
	// Counting 
	tstart_count = MPI_Wtime(); 
	count_words(&rank);
	tend_count = MPI_Wtime(); 

	// Outputing on File 
	tend_reduce = MPI_Wtime();
	for(i = 0; i < nthreads;++i)
	{
		if(rank == i)	dump_words();
		MPI_Barrier(MPI_COMM_WORLD);
	}
	printf("initialization time %lf, counting time %lf, writing time %lf, size %d, rank %d, hostaname %s, memory %ld Kb\n",
	 tend_int - tstart_init, tend_count - tstart_count, tend_reduce - tend_count, numtasks, rank, hostname, MEMORY_USAGE);
	fflush(stdout);

	if ( rank == 0 ) {
	ttotal = myclock() - tstart;
	printf("version %d, cores %d, total time %lf seconds, words %d, lines %d\n",
	 		version, nthreads, ttotal, nwords, maxlines);	
	}
	MPI_Finalize();
	return 0;
}

