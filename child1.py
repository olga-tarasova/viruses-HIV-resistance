import sys
import subprocess
import os


os.chdir('D:\\Dir\\') # please, enter the name of the target directory
drug = sys.stdin.readline().rstrip()
id_uniq= sys.stdin.readline().rstrip()
dir_all="D:\\Dir\\"+drug+"\\"
cutoff="D:\\Dir\\cutoffs.csv"
cutoff_3=0
cutoff_1_2=0
with open(cutoff) as f:
	for line in f:
		elt=line.strip().split(',')
		if elt[0]==drug:
			cutoff_3=float(elt[1])
			cutoff_1_2=float(elt[2])
file_res="D:\\Dir\\"+id_uniq+"_"+drug+".csv"
file_res2="D:\\Dir\\"+id_uniq+"_"+drug+"_predicted.csv"
cmd="SarMathCpp.exe"
p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
p.stdin.write(bytes(dir_all+"ovr3.sar"+'\r\n','UTF-8'))
p.stdin.write(bytes(file_res+'\r\n','UTF-8'))
out = p.communicate()
p.stdin.close()
text_file = open(file_res2, "r")
res = [i.strip() for i in text_file.readlines()]
fin=''
if float(res[0])>cutoff_3:
	fin=3 #'non resistant'
else:
	p=subprocess.Popen(cmd,shell=True,stdout=subprocess.PIPE,stdin=subprocess.PIPE)
	p.stdin.write(bytes(dir_all+"ovo_1_2.sar"+'\r\n','UTF-8'))
	p.stdin.write(bytes(file_res+'\r\n','UTF-8'))
	out = p.communicate()
	p.stdin.close()
	text_file = open(file_res2, "r")
	res = [i.strip() for i in text_file.readlines()]
	if float(res[0])>cutoff_1_2:
		fin=1 #'higly resistant'
	else:
		fin=2 #'moderate resistant'

print(drug+';'+str(fin))
#os.remove(file_res)

			