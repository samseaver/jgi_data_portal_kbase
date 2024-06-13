#!/usr/bin/env python
import os
import json
import time
import requests

# https://data.jgi.doe.gov/refine-download/phytozome
# Copy Session Token
# Bearer /api/sessions/faf69c37e163f009d664b0eee870c19a
# https://files-download.jgi.doe.gov/apidoc/

Session_Token = 'Bearer /api/sessions/faf69c37e163f009d664b0eee870c19a'
headers = {
    'accept': 'application/json',
    'Authorization': Session_Token,
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
        
# Download
# curl -X GET "https://files-download.jgi.doe.gov/download_files/53112ac349607a1be00559cb/"
# -H "accept: application/json"
# -H "Authorization: Bearer /api/sessions/3c4f7df597e6f307f2a09c01ba096558"
# -H "X-CSRFToken: T4RZT9zZtQHsEqFZVMDr2UUBw0WkWjlA99orsLaTxGWwQoQn7JMKL3sV4J3SNW67"

