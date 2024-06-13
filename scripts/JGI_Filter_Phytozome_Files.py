#!/usr/bin/env python
import os
import json
import requests

missing_assemblies_dict=dict()
with open('Input_Files/Missing_Assemblies.txt') as msfh:
    for line in msfh.readlines():
        line=line.strip('\r\n')
        tmp_lst=line.split('\t')
        missing_assemblies_dict[tmp_lst[0]]=tmp_lst[1]

db_source = 'phytozome'
with open(os.path.join('..',db_source,'JGI_Data_Portal_Files.json')) as jdpfh:
    organism_files = json.load(jdpfh)

base_file_versions=dict()
with open('Input_Files/Base_File_Version.txt') as bvfh:
    for line in bvfh.readlines():
        line = line.strip('\r\n')
        tmp_lst = line.split('\t')
        base_file_versions[tmp_lst[0]]={'assembly':tmp_lst[1],'annotation':tmp_lst[2]}

base_species=dict()
with open('Input_Files/Base_Species.txt') as bvfh:
    for line in bvfh.readlines():
        line = line.strip('\r\n')
        tmp_lst = line.split('\t')
        base_species[tmp_lst[0]]=tmp_lst[1]

file_types = ['gff','fasta','text']
accepted_files=list()
for ff in organism_files:
    if(ff['type'] not in file_types):
        continue

    if('data_release_policy' not in ff or ff['data_release_policy'] != 'unrestricted'):
        continue

    if(ff['Gspecies'] in base_species):
        ff['Gspecies'] = base_species[ff['Gspecies']]

    species_version = "_".join([ff['Gspecies'],ff['annotation_version']])

    annotation = ff['annotation_version']
    assembly = ff['assembly_version']
    if(species_version in base_file_versions):
       annotation=base_file_versions[species_version]['annotation']
       assembly=base_file_versions[species_version]['assembly']

    accepted=False
    base_gm_file = "_".join([ff['Gspecies'],str(ff['proteome_id']),annotation])
    base_as_file = "_".join([ff['Gspecies'],str(ff['proteome_id']),assembly])
    if(ff['type'] == 'gff'):
        if(ff['file'] == ".".join([base_gm_file,"gene","gff3","gz"])):
            accepted=True

    if(ff['type'] == 'fasta'):
        if(ff['file'] == ".".join([base_gm_file,"protein","fa","gz"])):
            accepted=True

        if(ff['file'] == ".".join([base_as_file,"fa","gz"])):
            accepted=True

        if(species_version in missing_assemblies_dict and ff['file'] == missing_assemblies_dict[species_version]):
            accepted=True

    if(ff['type'] == 'text'):
        if(ff['file'] == ".".join([base_gm_file,"annotation_info","txt"])):
            accepted=True

        if(ff['file'] == ".".join([base_gm_file,"synonym","txt"])):
            accepted=True

        if(ff['file'] == ".".join([base_gm_file,"defline","txt"])):
            accepted=True

    if(accepted is True):
        accepted_files.append(ff)

with open(os.path.join('..',db_source,'JGI_Data_Portal_Accepted_Files.json'),'w') as jdpfh:
    jdpfh.write(json.dumps(accepted_files,indent=2))
