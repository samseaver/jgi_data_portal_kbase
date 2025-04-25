#!/usr/bin/env python
import os
import json

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

	# strip key characters
	strip_table = str.maketrans({"_":"","-":"",",":"","'":""})
	stripped_gm_file = base_gm_file.translate(strip_table)

	# Protein
	if(ff['type'] == 'fasta' and ff['file'].translate(strip_table).lower() == ".".join([stripped_gm_file,"protein","fa","gz"])):
		if(species_version == 'TarvensevarMN106_v4.1'):
			print(json.dumps([ff],sort_keys=True,indent=2))
