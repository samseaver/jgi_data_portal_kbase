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

file_types = ['gff','fasta','text']
accepted_files=dict()
for ff in organism_files:
    species_version = "_".join([ff['Gspecies'],ff['annotation_version']])

    annotation = ff['annotation_version']
    assembly = ff['assembly_version']
    if(species_version in base_file_versions):
       annotation=base_file_versions[species_version]['annotation']
       assembly=base_file_versions[species_version]['assembly']

#    if(ff['Gspecies'].startswith("Bdistachyon") and ff['Gspecies'] != "Bdistachyon"):
#        Bdi_accession = ff['Gspecies'][len('Bdistachyon'):]
#        annotation = annotation.split(".")
#        annotation.insert(1,Bdi_accession)
#        if(annotation[-1] != "1"):
#            annotation.append("1")
#        annotation = ".".join(annotation)

    base_gm_file = "_".join([ff['Gspecies'],str(ff['proteome_id']),annotation]).lower()
    base_as_file = "_".join([ff['Gspecies'],str(ff['proteome_id']),assembly]).lower()

    # strip key characters
    strip_table = str.maketrans({"_":"","-":"",",":"","'":""})
    stripped_gm_file = base_gm_file.translate(strip_table)
    stripped_as_file = base_as_file.translate(strip_table)

    base_key = "_".join([ff['Gspecies'],str(ff['proteome_id'])])
    if(base_key not in accepted_files):
        accepted_files[base_key]=list()
        
    # Gene Model
    if(ff['type'] == 'gff' and ff['file'].translate(strip_table).lower() == ".".join([stripped_gm_file,"gene","gff3","gz"])):
        accepted_files[base_key].append(ff)

    # Gunzipped Gene Model
    if(ff['type'] == 'gff' and ff['file'].translate(strip_table).lower() == ".".join([stripped_gm_file,"gene","gff3"])):
        accepted_files[base_key].append(ff)

    # Assembly
    if(ff['type'] == 'fasta' and ff['file'].translate(strip_table).lower() == ".".join([stripped_as_file,"fa","gz"])):
        accepted_files[base_key].append(ff)

    # Protein
    if(ff['type'] == 'fasta' and ff['file'].translate(strip_table).lower() == ".".join([stripped_gm_file,"protein","fa","gz"])):
        accepted_files[base_key].append(ff)

    # Annotation
    if(ff['type'] == 'text' and ff['file'].translate(strip_table).lower() == ".".join([stripped_gm_file,"annotationinfo","txt"])):
        accepted_files[base_key].append(ff)

    # Synonyms
    if(ff['type'] == 'text' and ff['file'].translate(strip_table).lower() == ".".join([stripped_gm_file,"synonym","txt"])):
        accepted_files[base_key].append(ff)

    # Defline
    if(ff['type'] == 'text' and ff['file'].translate(strip_table).lower() == ".".join([stripped_gm_file,"defline","txt"])):
        accepted_files[base_key].append(ff)

    if(species_version in missing_assemblies_dict and ff['file'] == missing_assemblies_dict[species_version]):
        accepted_files[base_key].append(ff)

filtered_files = list()
for base_key in accepted_files:
    has_gff=False
    has_assembly=False

    if(base_key.startswith("Bdistachyon") and "Bdistachyon_" not in base_key):
        bdist_pangenome = True
        continue

    for ff in accepted_files[base_key]:
        if(ff['type'] =='gff'):
            has_gff=True

        if(ff['type'] == 'fasta' and 'protein' not in ff['file']):
            has_assembly=True

    if(not has_assembly or not has_gff):

        print(base_key,has_assembly,has_gff)
        for off in organism_files:
            if(base_key == "_".join([off['Gspecies'],str(off['proteome_id'])])):
                print("\t",off['type'],off['file'],off['assembly_version'],off['annotation_version'])
                if('data_release_policy' in off):
                    print("\t\t",off['data_release_policy'])
        continue

    drp=list()
    for ff in accepted_files[base_key]:
        if(ff['type'] =='gff' or (ff['type'] == 'fasta' and 'protein' not in ff['file'])):
            if('data_release_policy' not in ff):
                drp.append(None)
            else:
                drp.append(ff['data_release_policy'])                
    
    if(len(set(drp)) == 1 and drp[0] == 'unrestricted'):
        for ff in accepted_files[base_key]:
            filtered_files.append(ff)

filtered_files = sorted(filtered_files, key = lambda d: [str(d[key]) for key in ("proteome_id","jamo_id")])
with open(os.path.join('..',db_source,'JGI_Data_Portal_Accepted_Files.json'),'w') as jdpfh:
    jdpfh.write(json.dumps(filtered_files,sort_keys=True,indent=2))