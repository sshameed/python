import os
import re
dir2=r"C:\Users\ABUSHAHULS\Documents\temp\testdir"
#dir2=r"C:\Users\ABUSHAHULS\Documents\temp"
print("directory name is", dir2)

filelist=[]

def get_files_in_a_directory(dir1):
    global filelist
    if os.path.isdir(dir1):
        listlevel1=os.listdir(dir1)
        if (len(listlevel1)==0):
            print("no files found in", dir1)
            return
        else:
            for i in listlevel1:
                if os.path.isfile(dir1+'\\'+i):
                    print(dir1+'\\'+i)
                    filelist.append(dir1+'\\'+i)
                elif os.path.isdir(dir1+'\\'+i):
                    get_files_in_a_directory(dir1+'\\'+i)
    else:
        print(dir1,"is NOT a directory.")

get_files_in_a_directory(dir2)

print("after function call")
print("printing elements in global variable filelist")
for i in filelist:
    print(i)
