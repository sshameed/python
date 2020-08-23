#!/usr/bin/python3
# 23-8-2020
# this script can be used to block or unblock access to specific sites, such as youtube.com at specific times
# schedule this script from cron on the host running pi-hole (https://pi-hole.net)
# update list regexBlackList with regular expression for websites that you want to block
# schedule this script from cron on the host running pi-hole (https://pi-hole.net)
import argparse
import sys
import os
import subprocess
import logging

def checkforBlocked(sitea):
    t1 = subprocess.run(["/usr/local/bin/pihole", "--regex", "-l"], capture_output=True,encoding='utf-8')
    if sitea in t1.stdout:
        return(True)
    else:
        return(False)

def listblockedSites():
    t1 = subprocess.run(["/usr/local/bin/pihole", "--regex", "-l"], capture_output=True,encoding='utf-8')
    print(t1.stdout)
    logging.info(t1.stdout)

def blockSites():
    tempblocklist = []
    for i in regexBlackList:
        check = checkforBlocked(i)
        if check:
            print(i + " is already blocked, nothing to do.")
            logging.info(i + " is already blocked, nothing to do.")
        else:
            tempblocklist.append(i)
    if tempblocklist:
        for k in tempblocklist:
            t1 = subprocess.Popen(["/usr/local/bin/pihole", "--regex", k], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=my_env, encoding='utf-8').communicate()
            if t1[0]:
                logging.info(t1[0])
            if t1[1]:
                logging.error(t1[1])
            t1 = subprocess.Popen(["/usr/local/bin/pihole", "restartdns"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=my_env, encoding='utf-8').communicate()
            if t1[0]:
                logging.info(t1[0])
            if t1[1]:
                logging.error(t1[1])
    else:
        print("all sites in list are already blocked, nothing to do.")
        logging.info("all sites in list are already blocked, nothing to do.")

def unblockSites():
    tempunblocklist = []
    for i in regexBlackList:
        check = checkforBlocked(i)
        if not check:
            print(i + " is already unblocked, nothing to do.")
            logging.info(i + " is already unblocked, nothing to do.")
        else:
            tempunblocklist.append(i)
    if tempunblocklist:
        for k in tempunblocklist:
            t1 = subprocess.Popen(["/usr/local/bin/pihole", "--regex", "-d", k], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=my_env, encoding='utf-8').communicate()
            if t1[0]:
                logging.info(t1[0])
            if t1[1]:
                logging.error(t1[1])
            t1 = subprocess.Popen(["/usr/local/bin/pihole", "restartdns"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=my_env, encoding='utf-8').communicate()
            if t1[0]:
                logging.info(t1[0])
            if t1[1]:
                logging.error(t1[1])
    else:
        print("all sites in list are already unblocked, nothing to do.")
        logging.info("all sites in list are already unblocked, nothing to do.")

if __name__ == "__main__":
    regexBlackList = [ '(\.|^)youtube\.com$', '(\.|^)googlevideo\.com$' ]
    logging.basicConfig(filename='/var/log/block.py.log', filemode='a', format='%(asctime)s - %(message)s', level=logging.INFO)
    my_parser = argparse.ArgumentParser(prog='block.py', usage='%(prog)s block,\n%(prog)s unblock,\n%(prog)s list.',
	                                    description='block or unblock websites')
    my_parser.add_argument('--action', action='store', type=str, required=True)
    args = my_parser.parse_args()
    arg1 = args.action

    my_env=os.environ.copy()

    if (arg1 == "block"):
        print("proceeding to block sites ...")
        blockSites()
    elif (arg1 == "unblock"):
        print("proceeding to unblock sites ...")
        unblockSites()
    elif (arg1 == "list"):
        print("blocked sites are given below: ")
        listblockedSites()
    else:
        print("usage error: invalid argument")
        sys.exit(1)
