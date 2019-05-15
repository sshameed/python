import re
import os
file2=r"K:\customers\nakilath\ffo_upgrade_2019\23_4_2019_upgrade_plan\ncn01_gather_data_pl.log"
regex2=r"she"

def check_pattern_in_file(file1, regex1):
    fin=open(file1,'rt',encoding="ISO-8859-1")
    occurence = 0
    while True:
        line=fin.readline()
        if not line:
            break
        m = re.search(regex1,line,re.IGNORECASE)
        if m:
            if (occurence==0):
                print(file1)
                occurence+=1
            print(line)
    fin.close()

check_pattern_in_file(file2,regex2)