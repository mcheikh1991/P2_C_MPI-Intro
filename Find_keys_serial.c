#include <stdlib.h>
#include <stdio.h>
#include <string.h>
#include <time.h>

int maxwords = 5000;
int maxlines = 10000;
int nwords;
int nlines;
int err, *count, nthreads = 1;

double tstart, ttotal;
FILE *fd;
char **word, **line;
char *key_array;
int key_array_size;
char newword[15];

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
void init_list()
{
	// Malloc space for the word list and lines
	int i;
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
}


/* read_dict_words: (Read Dictianary words)
--------------------------------------------*/
void read_dict_words()
{
// Read in the dictionary words

	fd = fopen( "keywords.txt", "r" );
	nwords = -1;
	do {
		err = fscanf( fd, "%[^\n]\n", word[++nwords] );
	} while( err != EOF && nwords < maxwords );
	fclose( fd );

	printf( "Read in %d words\n", nwords);
}


/* read_lines: (Read wiki lines)
--------------------------------------------*/
void read_lines()
{
// Read in the lines from the data file
	double nchars = 0;
	fd = fopen( "wiki_dump.txt", "r" );
	nlines = -1;
	do {
		err = fscanf( fd, "%[^\n]\n", line[++nlines] );
		if( line[nlines] != NULL ) nchars += (double) strlen( line[nlines] );
	} while( err != EOF && nlines < maxlines);
	fclose( fd );

	printf( "Read in %d lines averaging %.0lf chars/line\n", nlines, nchars / nlines);
}

/* count_words: (count the words)
--------------------------------------------*/
void *count_words()
{
	int i,k;
	for( i = 0; i < nwords; i++ ) {
		for( k = 0; k < nlines; k++ ) {
			if( strstr( line[k], word[i] ) != NULL ) 
			{
				if (count[i] == 0)
				{
					snprintf(newword,8,"%s:",word[i]);
					strcat(key_array,newword);
					key_array_size += 8;
					char* myrealloced_array = realloc(key_array, key_array_size * sizeof(char));
					if (myrealloced_array) {
			     		key_array = myrealloced_array;
			  	 	}
				}
				count[i]++; 
				snprintf(newword,8,"%d,",k);
				strcat(key_array,newword);
				key_array_size += 8;
				char* myrealloced_array = realloc(key_array, key_array_size * sizeof(char));
				if (myrealloced_array) {
     				key_array = myrealloced_array;
  	 			}
			}
		}

		if (i % 1000 == 0) printf("Loop %d of %d done\n", i, nwords);
		if (count[i] != 0)
		{
			snprintf(newword,5,"\n");
			strcat(key_array,newword);
			key_array_size += 5;
			char* myrealloced_array2 = realloc(key_array, key_array_size * sizeof(char));
			if (myrealloced_array2) {
	     		key_array = myrealloced_array2;
	  	 	}
  		}
	}
	//printf(key_array);
}

/* dump_words: (write the output on file)
--------------------------------------------*/
void dump_words()
{
	int i,k;
	// Dump out the word counts

	fd = fopen( "wiki.out", "w" );
	for( i = 0; i < nwords; i++ ) {
		fprintf( fd, "%d %s %d\n", i, word[i], count[i] );
	}
	fprintf( fd, "The run on %d cores took %lf seconds for %d words\n",
			  nthreads, ttotal, nwords);
	fclose( fd );

	fd = fopen( "wiki_words.out", "w" );
	int results =fputs(key_array,fd);
	fclose( fd );
}


/*--------------------------------------------------
                      Main 
--------------------------------------------------*/

int main()
{
	key_array_size = 15;
 	key_array = malloc(sizeof(char)*key_array_size); 
	init_list();
	read_dict_words();
	read_lines();

	// Loop over the word list

	tstart = myclock();  // Set the zero time
	count_words();
	ttotal = myclock() - tstart;
	printf( "The run on %d cores took %lf seconds for %d words\n", nthreads, ttotal, nwords);

	dump_words();

}

