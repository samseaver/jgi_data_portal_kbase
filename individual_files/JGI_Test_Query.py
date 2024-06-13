#!/usr/bin/env python
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

org = 'phytozome'
base_url = 'https://files.jgi.doe.gov/'+org+'_file_list/'
# params['q']='Cryptophyta'

organism_files=list()
next_page = 1
last_page = 1
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
                print(ff['metadata']['ncbi_taxon_id'],ff['metadata']['ncbi_taxon']['ncbi_taxon_species'])
            break

    if(next_page == last_page):
        break

    next_page=data['next_page']
