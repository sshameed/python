#!/usr/bin/python3
import os
import subprocess

def find_used_uids():
    uidlist=[]
    ret=subprocess.getoutput('getent passwd')
    for line in ret.split('\n'):
        t1 = line.split(':')
        uidlist.append(int(t1[2]))
    uidlist.sort()
    return uidlist

def find_unused_uids(list1):
    length=len(list1)
    i=0
    while (i<=length-2):
        if (list1[i+1]-list1[i] > 1):
            difference=list1[i+1]-list1[i]
            j=1
            if (difference > j):
                lowerrange=list1[i]+j
                highestrange=list1[i]+difference-1
                print(lowerrange,'-',highestrange)
            elif (difference==2):
                print(list1[i]+1)
            '''
            while (j<difference):
                print(list1[i]+j)
                j=j+1
            '''
        i=i+1

    uidlimit=65535
    if (list1[length-1]<65535):
        print(list1[length-1]+1,'-','65535')

if __name__ == "__main__":
    x=find_used_uids()
    print(x)
    print("Following uid numbers are available for use.")
    find_unused_uids(x)

