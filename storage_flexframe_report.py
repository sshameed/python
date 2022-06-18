#!/home/netapp_ontap/bin/python3
# v 1.1 , 10-10-2021, subin.hameed@sampleconsultcompany.com
from netapp_ontap import config,NetAppRestError
from netapp_ontap.host_connection import HostConnection
from netapp_ontap.resources import Volume,Snapshot,SnapmirrorRelationship
import smtplib
import pandas as pd
import os
import subprocess

my_env=os.environ.copy()
pd.set_option('display.max_rows', 100)
availablethreshold = 20

## DR site
def show_snapmirror() -> None:
    """List Snapmirror"""
    source_path_list = []
    destination_path_list = []
    policy_name_list = []
    state_list = []
    lag_time_list = []
    snapmirror_status_dict = { "source_path":source_path_list, "destination_path":destination_path_list, "policy":policy_name_list, "state":state_list, "lag_time":lag_time_list } 
    config.CONNECTION =  HostConnection('clusterdr', cert='/home/netapp_ontap/py/storemon_user_drsite.cert', key='/home/netapp_ontap/py/storemon_user_drsite.key', verify=False)
#    print("List of SnapMirror Relationships:")
#    print("=================================")
    
    try:
        for snapmirrorrelationship in SnapmirrorRelationship.get_collection(fields="uuid"):
            snapmirror1 = SnapmirrorRelationship.find(
            uuid=snapmirrorrelationship.uuid)
            t = snapmirror1.to_dict()
            try:
                if (t['state'] != "snapmirrored"):
                    continue
                state_list.append(t['state'])
                source_path_list.append(t['source']['path'])
                destination_path_list.append(t['destination']['path'])
                policy_name_list.append(t['policy']['name'])
                lag_time_list.append(t['lag_time'])
            except:
                print(f"encountered error with {snapmirrorrelationship.uuid}")                
    except NetAppRestError as error:
        print("Error:- " % error.http_err_response.http_response.text)
        print("Exception caught :" + str(error))
    snapmirror_state_df = pd.DataFrame(snapmirror_status_dict)
    return(snapmirror_state_df)
## end DR site

h_volume_list = []
h_aggr_list = []
h_svm_list = []
h_volsize_list = []
h_volusedsize_list = []
h_volspaceavail_list = []

n_volume_list = []
n_aggr_list = []
n_svm_list = []
n_volsize_list = []
n_volusedsize_list = []
n_volspaceavail_list = []

hostname_list = []
sid_list = []

high_usage_vol_dict = {"volume_name":h_volume_list, "containing_aggregate":h_aggr_list, "svm":h_svm_list, "volume_size":h_volsize_list, "volume_space_used":h_volusedsize_list, "volume_space_available":h_volspaceavail_list}

normal_usage_vol_dict = {"volume_name":n_volume_list, "containing_aggregate":n_aggr_list, "svm":n_svm_list, "volume_size":n_volsize_list, "volume_space_used":n_volusedsize_list, "volume_space_available":n_volspaceavail_list}

ff_services_dict = { "hostname":hostname_list, "sid":sid_list }

config.CONNECTION =  HostConnection('clusterprimary', cert='/home/netapp_ontap/py/storemon_user.cert', key='/home/netapp_ontap/py/storemon_user.key', verify=False)

for vol in Volume.get_collection():
    tempdict = vol.to_dict()
    volumedetails =  Volume(uuid=tempdict['uuid'])
    volumedetails.get()
    tempdict = volumedetails.to_dict()
    volname = tempdict['name']
    aggregate = tempdict['aggregates'][0]['name']
    svm = tempdict['svm']['name']
    try:
        volsize = tempdict['space']['size']/1024/1024/1024
        usedspace = tempdict['space']['used']/1024/1024/1024
        availablespace = tempdict['space']['available']/1024/1024/1024
        percentageavail = availablespace * 100/volsize
    except:
        print("error")
    if (percentageavail < availablethreshold):
        h_volume_list.append(volname)
        h_aggr_list.append(aggregate)
        h_svm_list.append(svm)
        t1volsize = "{:.0f}".format(volsize)
        h_volsize_list.append(t1volsize)
        t1usedspace = "{:.0f}".format(usedspace)
        h_volusedsize_list.append(t1usedspace)
        t1availablespace = "{:.0f}".format(availablespace)
        h_volspaceavail_list.append(t1availablespace)
    else:
        n_volume_list.append(volname)
        n_aggr_list.append(aggregate)
        n_svm_list.append(svm)
        t2volsize = "{:.0f}".format(volsize)
        n_volsize_list.append(t2volsize)
        t2usedspace = "{:.0f}".format(usedspace)
        n_volusedsize_list.append(t2usedspace)
        t2availablespace = "{:.0f}".format(availablespace)
        n_volspaceavail_list.append(t2availablespace)

highusage_df = pd.DataFrame(high_usage_vol_dict)
normalusage_df = pd.DataFrame(normal_usage_vol_dict).sort_values(by=['volume_name'],ignore_index=True)

try:
    t1 = subprocess.Popen(["ssh", "ffan1", "/FlexFrame/scripts/view_hosts"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=my_env, encoding='utf-8').communicate()
except:
    print("error getting view_hosts output.")

if(t1[0]):
    for j in t1[0].splitlines():
        if "smd" not in j:
            hostname_list.append(j.split()[-1])
            sid_list.append(j.split()[0])

ff_services_df = pd.DataFrame(ff_services_dict).sort_values(by=['hostname'],ignore_index=True)

snapmirror_state_df = show_snapmirror()

# message html header
message = '''From: FlexFrame report <flexframe.report@samplecompany.com>
To: Subin <subin.hameed@sampleconsultant.com>
MIME-Version: 1.0
Content-type: text/html
Subject: Storage and SAP service report

'''

snapmirror_state_header = '''
<h1><font color="blue">Snapmirror Status</font></h1>
'''

highusage_header = '''
<h1><font color="red">Volumes with high usage - please check</font></h1>
'''

normalusage_header = '''
<h1><font color="blue">Volumes with normal usage</font></h1>
'''

ff_services_header = '''
<h1><font color="blue">Hosts running SAP Services</font></h1>
'''

message = message + snapmirror_state_header + snapmirror_state_df.to_html()  +  highusage_header + highusage_df.to_html() + normalusage_header + normalusage_df.to_html() +  ff_services_header + ff_services_df.to_html()
sender = "flexframe.report@samplecompany.com"
receivers = ['subin.hameed@sampleconsult.com', 'team@samplecompany.com']

try:
    smtpObj = smtplib.SMTP('smtp.samplecompany.com')
    smtpObj.sendmail(sender, receivers, message)
    print ("Successfully sent email")
except SMTPException:
    print ("Error: unable to send email")
