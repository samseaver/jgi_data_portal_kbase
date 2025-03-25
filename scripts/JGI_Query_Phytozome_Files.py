#!/usr/bin/env python
import os
import sys
import json
import requests

headers = {
    'accept': 'application/json',
}

params = {
    'version': 'current',
    'api_version': '2',
    'a': 'false',
    'h': 'false',
    'd': 'asc',
    'p': '1',
    'x': '100',
}

db_source = 'phytozome'
base_url = 'https://files.jgi.doe.gov/'+db_source+'_file_list/'

organism_files=list()
next_page = 1
last_page = 1000
while(isinstance(next_page,int)):
    if(next_page is False):
        break

    print("Fetching page: ",next_page)
    params['p']=next_page
    response = requests.get(base_url, params=params, headers=headers)
    print(response.status_code,response.reason)

    if response.status_code == 200:
        data = response.json()

        if('error' in data.keys()):
            print(data['error'])
            break

        for org in data['organisms']:
            for ff in org['files']:
                phy = ff['metadata']['phytozome']
                phy['jamo_id']=ff['_id']
                phy['file']=ff['file_name']
                phy['status']=ff['file_status']
                phy['type']=ff['file_type']
                phy['date']=ff['file_date']
                if(phy['phytozome_release_id'][-1] == "current"):
                    phy['phytozome_release_id'].pop()
                phy['phytozome_release_id'] = phy['phytozome_release_id'][-1]
                if('metadata' in ff and 'ncbi_taxon_id' in ff['metadata']):
                    phy['taxon']=ff['metadata']['ncbi_taxon_id']

                organism_files.append(phy)

    if(next_page == last_page):
        break

    next_page=data['next_page']

organism_files = sorted(organism_files, key = lambda d: [str(d[key]) for key in ("proteome_id","jamo_id")])
with open(os.path.join('..',db_source,'JGI_Data_Portal_Files.json'),'w') as jdpfh:
    jdpfh.write(json.dumps(organism_files,sort_keys=True,indent=2))

# List files
# curl -X GET "https://files.jgi.doe.gov/phytozome_file_list/?version=current&api_version=2&a=false&h=false&d=asc&p=1&x=1000"
# -H "accept: application/json"
# -H "X-CSRFToken: ynF3R6gnMVoE2TW92VR4iaqjFnJKxRJXLFa1IehEWtqe6iC0hUz6gDz7TqTfWC9Q"
