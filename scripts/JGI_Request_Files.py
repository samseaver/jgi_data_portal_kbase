#!/usr/bin/env python
import os
import json
import requests

with open('../jdp_token') as tfh:
    jdp_token=tfh.readline().strip('\n')

headers = {
    'accept': 'application/json',
    'Authorization': jdp_token,
    'Content-Type': 'application/json',
}

db_source = 'phytozome'
with open(os.path.join('..',db_source,'JGI_Data_Portal_Accepted_Files.json')) as jdpfh:
    organism_files = json.load(jdpfh)

restore_ids=list()
for ff in organism_files:
    if(ff['status'] == 'RESTORED' or \
       ff['status'] == 'RESTORE_REGISTERED' or \
       ff['status'] == 'BACKUP_COMPLETE'):
        continue

    print(ff['file'],ff['status'])
    restore_ids.append(ff['jamo_id'])

json_data = {
    'ids': restore_ids
}

base_url = 'https://files.jgi.doe.gov/request_archived_files/'
response = requests.post(base_url, headers=headers, json=json_data)
data=response.json()

with open(os.path.join('..',db_source,'Request_Response.json'),'w') as rrfh:
    rrfh.write(json.dumps(data,indent=2))
