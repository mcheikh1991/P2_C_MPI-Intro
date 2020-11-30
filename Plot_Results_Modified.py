import matplotlib.pyplot as plt
import numpy as np
import re
import os
from os import listdir, remove
from os.path import isfile, join
from matplotlib.font_manager import FontProperties
from matplotlib import rcParams
rcParams['xtick.direction'] = 'in'
rcParams['ytick.direction'] = 'in'
rcParams['figure.figsize'] = 7.5, 7
rcParams['font.size'] =  12
#rcParams['font.family'] = 'serif'


Loc = os.getcwd() 

def sort(main,other):
	main , other = zip(*sorted(zip(main,other)))
	main = np.array(main)
	other = np.array(other)
	return main, other

#---------------------------------------------------------
# Reading the Data  
#---------------------------------------------------------

Col = ['k','b','g','m','r','c','y','#92C6FF','#E24A33', '#001C7F', '.15', '0.40']
Mar = [".","s","o","d","P","v","^","<",">","1","2","3","4","8","+","p","P","*"]
Lin = ['-','.-',':']

i = 0
j = 0
g = 0
k = 0
FilesKilled = []
FilesWorking = []
RunNumber = []

Ser_Num_Iter   		=  []
Ser_Sum				=  np.array([])
Ser_ElapsedTime 	=  np.array([])
Ser_MemoryUsage 	=  np.array([])
Ser_Average_Ratio 	=  np.array([])

ALL_MPI_DATA = []


Data_Loc = Loc +'/Data/'

# Gets all Files
AllFiles = [f for f in listdir(Data_Loc) if isfile(join(Data_Loc, f))]

for z in ['sh.e','sh.po','sh.pe']:
	ErrorFiles = [File for File in AllFiles if re.findall(z,File) != []]
	#for File in ErrorFiles: 
		#print 'Error File for deletion:',File
		#remove(Data_Loc+File)

# Keeps only the output files ".o"
AllFiles = [File for File in AllFiles if re.findall('sh.o',File) != []]
for File in AllFiles:
	Data_File = open(Data_Loc+File,'r')
	Data_File = Data_File.read()

	try:
		Summary_Data = re.findall(r'version [0-9]*,[^\n]*',Data_File)
		All_Cores_Data = re.findall(r'initialization [^\n]*',Data_File)
		k = 0
		for Data in Summary_Data:
			Ver   = int(re.findall(r'version [0-9]*',Data)[0].split(' ')[1])
			Ncor  = int(re.findall(r'cores [0-9]*',Data)[0].split(' ')[1])
			GTime = float(re.findall(r'time [0-9]*.[0-9]*',Data)[0].split(' ')[1])
			Words = int(re.findall(r'words [0-9]*',Data)[0].split(' ')[1])
			Lines = int(re.findall(r'lines [0-9]*',Data)[0].split(' ')[1])
	
			if Lines == 800008:
				Lines = 800000
			elif Lines == 999984:
				Lines = 1000000

			MPI_DATA = [ ([0] * 6) for row in xrange(Ncor+1) ]
			Current_Cores_Data = All_Cores_Data[k:k+Ncor]

			run_type = 'single'
			First_Node = re.findall(r'hostaname \w*',Current_Cores_Data[0])[0].split(' ')[1]

			g = 1

			for Single_Core_Data in Current_Cores_Data:
				Rank = int(re.findall(r'rank \w*',Single_Core_Data)[0].split(' ')[1])
				New_Node = re.findall(r'hostaname \w*',Single_Core_Data)[0].split(' ')[1]
				Memory = int(re.findall(r'memory [0-9]*',Single_Core_Data)[0].split(' ')[1])
				MPI_DATA[g][0] = Rank
				MPI_DATA[g][1] = New_Node
				MPI_DATA[g][2] = Memory

				All_Local_Times = re.findall(r'time [0-9]*.[0-9]*',Single_Core_Data)
				j = 3
				for Signle_Local_Time in All_Local_Times:
					Local_Time = float(Signle_Local_Time.split(' ')[1])
					MPI_DATA[g][j] = Local_Time
					j = j +1
				g = g + 1
				if New_Node != First_Node:
					run_type = 'multiple'
			MPI_DATA[0][0] = Ver
			MPI_DATA[0][1] = Ncor
			MPI_DATA[0][2] = GTime
			MPI_DATA[0][3] = Words
			MPI_DATA[0][4] = Lines
			MPI_DATA[0][5] = run_type
			if Ncor == 64 and Lines == 1000000:
				MPI_DATA[1][4]  = MPI_DATA[1][4] / 100
				MPI_DATA[10][4] = MPI_DATA[10][4]/ 100
				MPI_DATA[13][4] = MPI_DATA[13][4]/ 100
				MPI_DATA[14][4] = MPI_DATA[14][4]/ 100
				MPI_DATA[20][4] = MPI_DATA[20][4]/ 2.0
				MPI_DATA[26][4] = MPI_DATA[26][4]/ 2.0
				MPI_DATA[63][4] = MPI_DATA[63][4]/ 2.0
				MPI_DATA[0][2] = 0.0
				for ii in range(1,Ncor+1):
					MPI_DATA[0][2] = max(MPI_DATA[0][2],MPI_DATA[ii][4]) + 5.16
			#print MPI_DATA
			ALL_MPI_DATA.append(MPI_DATA*1)
			k = k + Ncor 

		FilesWorking.append(File)
	except:
		FilesKilled.append(File)
		print 'Killed File:',File

print len(ALL_MPI_DATA)

#---------------------------------------------------------
# Averaging the Data  
#---------------------------------------------------------

Number_Cores = [1,2,4,8,16,32,64]
Number_Lines = [2e5,4e5,6e5,8e5,1e6]

GTime_Array_Single 		= np.zeros([len(Number_Cores),len(Number_Lines)])
GTime_Array_Multiple 	= GTime_Array_Single.copy()
Memm_Array_Single	 	= GTime_Array_Single.copy()
Memm_Array_Multiple 	= GTime_Array_Single.copy()
Average_Ratio_Single 	= GTime_Array_Single.copy()
Average_Ratio_Multiple	= GTime_Array_Single.copy()
Single_Node_Time_Init   = GTime_Array_Single.copy()
Single_Node_Time_Comp   = GTime_Array_Single.copy()
Single_Node_Time_Writ   = GTime_Array_Single.copy()
Single_Node_Time_Idle   = GTime_Array_Single.copy()
Single_Node_Memory   	= GTime_Array_Single.copy()
Single_Node_Avg_Ratio  	= GTime_Array_Single.copy()
Multiple_Node_Time_Init = GTime_Array_Single.copy()
Multiple_Node_Time_Comp = GTime_Array_Single.copy()
Multiple_Node_Time_Writ = GTime_Array_Single.copy()
Multiple_Node_Time_Idle = GTime_Array_Single.copy()
Multiple_Node_Memory   	= GTime_Array_Single.copy()
Multiple_Node_Avg_Ratio = GTime_Array_Single.copy()


for MPI_DATA in ALL_MPI_DATA:
	Summary_Data = MPI_DATA[0]
	Ncor  = Summary_Data[1]
	GTime = Summary_Data[2]
	Lines = Summary_Data[4]
	Type  = Summary_Data[5]
	All_Core_Data = MPI_DATA[1:Ncor+1]
	i = Number_Cores.index(Ncor)
	j = Number_Lines.index(Lines)

	if Type== 'single':
		GTime_Array_Single[i,j] += GTime 
		Average_Ratio_Single[i,j]  += 1
		for Each_Core_Data in All_Core_Data:
			Mem  = Each_Core_Data[2]
			Init_Time  = Each_Core_Data[3]
			Comp_Time  = Each_Core_Data[4]
			Writ_Time  = Each_Core_Data[5]
			Single_Node_Memory[i,j] +=  Mem
			Single_Node_Time_Init[i,j] += Init_Time
			Single_Node_Time_Comp[i,j] += Comp_Time
			Single_Node_Time_Writ[i,j] += Writ_Time
			Single_Node_Avg_Ratio[i,j] += 1
	else:
		GTime_Array_Multiple[i,j] += GTime 
		Average_Ratio_Multiple[i,j]  += 1
		for Each_Core_Data in All_Core_Data:
			Mem  = Each_Core_Data[2]
			Init_Time  = Each_Core_Data[3]
			Comp_Time  = Each_Core_Data[4]
			Writ_Time  = Each_Core_Data[5]
			Multiple_Node_Memory[i,j] +=  Mem
			Multiple_Node_Time_Init[i,j] += Init_Time
			Multiple_Node_Time_Comp[i,j] += Comp_Time
			Multiple_Node_Time_Writ[i,j] += Writ_Time
			Multiple_Node_Avg_Ratio[i,j] += 1


# Average:
#---------
GTime_Array_Single = GTime_Array_Single/Average_Ratio_Single
GTime_Array_Multiple = GTime_Array_Multiple/Average_Ratio_Multiple
Single_Node_Memory   = Single_Node_Memory   / Single_Node_Avg_Ratio
Multiple_Node_Memory = Multiple_Node_Memory / Multiple_Node_Avg_Ratio
#---------------------------------------------------------
# Plot the Data  
#---------------------------------------------------------
plt.figure(1)
for i in range(len(Number_Cores)):
	if not np.isnan(GTime_Array_Single[i]).all():
		plt.plot(Number_Lines,GTime_Array_Single[i]/3600.0,color=Col[i],marker='s',label='single '+str(Number_Cores[i]))
	if not np.isnan(GTime_Array_Multiple[i]).all():
		plt.plot(Number_Lines,GTime_Array_Multiple[i]/3600.0,color=Col[i],marker='o',linestyle=':',label='multiple '+str(Number_Cores[i]))
plt.xlabel('Number of Lines')
plt.ylabel('Global Time ($hr$)')
plt.xticks(np.arange(200000, 1200000, 200000))
leg = plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.17), ncol=4, fancybox=False, shadow=False)
leg.get_frame().set_linewidth(0.0)

plt.savefig('Num_Lines_Vs_Time.png')
plt.close()

plt.figure(2)
for i in range(len(Number_Cores)):
	if not np.isnan(GTime_Array_Single[i]).all():
		plt.plot(Number_Lines,Single_Node_Memory[i]/1024,color=Col[i],marker='s',label='single '+str(Number_Cores[i]))
	if not np.isnan(GTime_Array_Multiple[i]).all():
		plt.plot(Number_Lines,Multiple_Node_Memory[i]/1024,color=Col[i],marker='o',linestyle=':',label='multiple '+str(Number_Cores[i]))
plt.xlabel('Number of Lines')
plt.ylabel('Memory (Mb) /Core ')
plt.xticks(np.arange(200000, 1200000, 200000))
leg = plt.legend(loc='upper center', bbox_to_anchor=(0.5, 1.17), ncol=4, fancybox=False, shadow=False)
leg.get_frame().set_linewidth(0.0)

plt.savefig('Num_Lines_Vs_Memory.png')
plt.close()

#-----------------------------------


Ncor_single = []
GTime_single = []
Ncor_multiple = []
GTime_multiple = []
Avg_Ratio_single = []
Avg_Ratio_multiple = []
d = -1
for MPI_DATA in ALL_MPI_DATA:
	d = d +1
	Summary_Data = MPI_DATA[0]
	Ncor  = Summary_Data[1]
	GTime = Summary_Data[2]
	Lines = Summary_Data[4]
	Type  = Summary_Data[5]
	All_Core_Data = MPI_DATA[1:Ncor+1]

	if Lines == 1000000:
		print Type,Ncor,GTime
		if Type == 'single':
			if Ncor_single.count(Ncor) == 0:
				Ncor_single.append(Ncor)
				GTime_single.append(GTime)
				Avg_Ratio_single.append(1)
			else:
				GTime_single[Ncor_single.index(Ncor)] += GTime
				Avg_Ratio_single[Ncor_single.index(Ncor)] += 1
		else:
			if Ncor_multiple.count(Ncor) == 0:
				Ncor_multiple.append(Ncor)
				GTime_multiple.append(GTime)
				Avg_Ratio_multiple.append(1)
			else:
				GTime_multiple[Ncor_multiple.index(Ncor)] += GTime
				Avg_Ratio_multiple[Ncor_multiple.index(Ncor)] += 1

Ncor_single		= np.array(Ncor_single)
GTime_single	= np.array(GTime_single)
Ncor_multiple	= np.array(Ncor_multiple)
GTime_multiple	= np.array(GTime_multiple)
Avg_Ratio_single   = np.array(Avg_Ratio_single)
Avg_Ratio_multiple = np.array(Avg_Ratio_multiple)

GTime_single   = GTime_single/Avg_Ratio_single
GTime_multiple = GTime_multiple/Avg_Ratio_multiple

Ncor_single,GTime_single = sort(Ncor_single,GTime_single)
Ncor_multiple,GTime_multiple = sort(Ncor_multiple,GTime_multiple)


plt.figure(2)
plt.plot(Ncor_single,GTime_single/3600.0,'b-o',label='single')
plt.plot(Ncor_multiple,GTime_multiple/3600.0,'r-s',label='multiple')
plt.xlabel('Number of Cores')
plt.ylabel('Global Time ($hr$)')
#plt.xlim([0,2.1e9])
#plt.plot([0,5e9],[25000,25000],'g--')
#plt.ylim([0,np.max(ElapsedTime)])
plt.legend(loc='upper right')
plt.savefig('Time_Vs_Num_Cores.png')
plt.close()

plt.figure(3)
plt.semilogx(Ncor_single,GTime_single/3600.0,'b-o',label='single',basex=2)
plt.semilogx(Ncor_multiple,GTime_multiple/3600.0,'r-s',label='multiple',basex=2)
plt.xlabel('Number of Cores')
plt.ylabel('Global Time ($hr$)')
#plt.xlim([0,2.1e9])
#plt.plot([0,5e9],[25000,25000],'g--')
#plt.ylim([0,np.max(ElapsedTime)])
plt.legend(loc='upper right')
plt.savefig('Time_Vs_Num_Cores_Log2.png')
plt.close()
#-----------------------------------

def autolabel(rects):
    """
    Attach a text label above each bar displaying its height
    """
    for rect in rects:
        height = rect.get_height()
        ax.text(rect.get_x() + rect.get_width()/2., height+30,
                '%d%s' % (int(height),'%'),ha='center', va='bottom',size='smaller',color='k')


rcParams['figure.figsize'] = 16, 7

plt.figure(4)
opacity = 0.7
error_config = {'ecolor': '0.3'}
width = 0.8
labels = 'Idle', 'Computational'
colors = ['gold', 'lightskyblue']
colors = ['darkred', 'dodgerblue']
colors = ['darkorange', 'navy']
explode = (0.05, 0) 
d = -1
for MPI_DATA in ALL_MPI_DATA:
	d = d +1
	Summary_Data = MPI_DATA[0]
	Ncor  = Summary_Data[1]
	GTime = Summary_Data[2]
	Lines = Summary_Data[4]
	Type  = Summary_Data[5]
	All_Core_Data = MPI_DATA[1:Ncor+1]
	Comp = []
	Idle = []
	fig, ax = plt.subplots(1,2)
	for Each_Core_Data in All_Core_Data:
		Comp_Time  = Each_Core_Data[4]
		Comp.append(Comp_Time)

	GTime = np.max(Comp)
	Avg_Comp = np.average(Comp)
	Avg_Idle = GTime - Avg_Comp
	sizes = [Avg_Idle,Avg_Comp]
	rects2 = ax[0].bar(np.arange(Ncor), np.array(Comp)/60, width, color=colors[0], alpha=opacity,error_kw=error_config)
	Pie    = ax[1].pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%', shadow=False, startangle=140)
	#rects3 = ax.bar(np.arange(Ncor)+width, Idle, width, color='lightskyblue')#, alpha=opacity,error_kw=error_config)

	# add some text for labels, title and axes ticks
	ax[0].set_ylabel('Computational Time (min)')
	ax[0].set_xlabel('Cores')
	ax[0].set_title('Performance of each core')
	ax[1].set_title('Average performance time for all the cores')
	#ax.set_xticks([0.35, 1.175, 2.175, 3.175,4.175])
	ax[0].set_xticklabels(())
	#ax.legend((rects2[0], rects3[0]), ('Computational', 'Idle'))

	#autolabel(rects2)
	#autolabel(rects3)

	#ax.legend(loc='upper left')
	plt.savefig('figures/'+str(Type)+'_Machine_Performance_'+str(Ncor)+'-'+str(Lines)+'-'+str(d)+'.png')
	plt.close()
