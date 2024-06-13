#!/usr/bin/env python
import os
import json
import time
import requests

with open('../jdp_token') as tfh:
	jdp_token=tfh.readline().strip('\n')

headers = {
    'accept': 'application/json',
    'Authorization': jdp_token
}

file_to_download = "Sbicolor_454_v3.1.1.transcript_primaryTranscriptOnly.fa.gz"
db_source = 'phytozome'
base_url = 'https://files-download.jgi.doe.gov/download_files/'
with open(os.path.join('..',db_source,'JGI_Data_Portal_Files.json') as jdpfh:
    organism_files = json.load(jdpfh)

for ff in organism_files:
    if(ff['file'] != file_to_download):
        continue

    print(ff['file'],ff['jamo_id'])
    response=requests.get(base_url+ff['jamo_id'], headers=headers)
    if response.status_code == 200:
        with open(ff['file'], "wb") as fffh:
            fffh.write(response.content)
            print("Downloaded")
    else:
        print("Download failed")
        print(ff['status'])
        print(str(response.status_code))
        print(response.reason)
