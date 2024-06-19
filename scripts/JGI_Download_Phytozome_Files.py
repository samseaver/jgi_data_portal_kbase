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

base_url = 'https://files-download.jgi.doe.gov/download_files/'
db_source = 'phytozome'
with open(os.path.join('..',db_source,'JGI_Data_Portal_Accepted_Files.json')) as jdpfh:
    organism_files = json.load(jdpfh)

downloaded_files=list()
base_genome_path = os.path.join('..','..','genomes','JGI_Data_Portal','Phytozome')
print(base_genome_path)
if(os.path.isdir(base_genome_path) is False):
    sys.exit()

defh = open(os.path.join('..',db_source,'Erroneous_Files.txt'),'w')
for ff in organism_files:
    dir_name = "_".join([ff['Gspecies'],ff['annotation_version']])
    dir_path = os.path.join(base_genome_path,dir_name)
    if(os.path.isdir(dir_path) is False):
        print("Creating: ",dir_path)
        os.mkdir(dir_path)

    if(os.path.isfile(os.path.join(dir_path,ff['file'])) is True):
        defh.write("File already downloaded: "+ff['file']+"\n")
        defh.write("===============================\n")
        downloaded_files.append(ff)
        continue

    response=requests.get(base_url+ff['jamo_id'], headers=headers)
    if response.status_code == 200:
        with open(os.path.join(dir_path,ff['file']), "wb") as fffh:
            if("Lsativa" in dir_name):
                print(dir_path,ff['file'])

            fffh.write(response.content)
            downloaded_files.append(ff)
            time.sleep(1)
    else:
        print("Failed to download "+ff['file'])
        defh.write("Failed to download the file: "+ff['file']+"\n")
        defh.write(ff['status']+"\n")
        defh.write(str(response.status_code)+"\n")
        defh.write(response.reason+"\n")
        defh.write("===============================\n")

print("Downloaded "+str(len(downloaded_files))+" files")
with open(os.path.join('..',db_source,'JGI_Data_Portal_Downloaded_Files.json'),'w') as jdpfh:
    jdpfh.write(json.dumps(downloaded_files,indent=2))

