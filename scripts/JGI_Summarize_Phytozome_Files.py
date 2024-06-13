#!/usr/bin/env python
import json
import sys
import os

missing_assemblies_dict=dict()
with open('Input_Files/Missing_Assemblies.txt') as msfh:
    for line in msfh.readlines():
        line=line.strip('\r\n')
        tmp_lst=line.split('\t')
        missing_assemblies_dict[tmp_lst[0]]=tmp_lst[1]

db_source = 'phytozome'
with open(os.path.join('..',db_source,'JGI_Data_Portal_Downloaded_Files.json')) as jdpfh:
    organism_files = json.load(jdpfh)

# The organism *must* have an assembly file and a gene model (gff) file
# Protein fasta is optional but important for fixing protein sequences
# Annotation_info, synonym, and defline, are optional but 
# important for updating data in genome object
base_genome_path = os.path.join(sys.path[0],'..','..','genomes','JGI_Data_Portal','Phytozome')
if(os.path.isdir(base_genome_path) is False):
    sys.exit()

overridden_versions=dict()
with open('Input_Files/Overridden_Versions.txt') as ovfh:
    for line in ovfh.readlines():
        line = line.strip('\r\n')
        tmp_lst = line.split('\t')
        old_spp_vers = "_".join(tmp_lst[:2])
        new_spp_vers = "_".join([tmp_lst[0],tmp_lst[2]])
        overridden_versions[old_spp_vers]=new_spp_vers

base_file_versions=dict()
with open('Input_Files/Base_File_Version.txt') as bvfh:
    for line in bvfh.readlines():
        line = line.strip('\r\n')
        tmp_lst = line.split('\t')
        base_file_versions[tmp_lst[0]]={'assembly':tmp_lst[1],'annotation':tmp_lst[2]}

organism_summary=dict()
for ff in organism_files:
    species_version = "_".join([ff['Gspecies'],ff['annotation_version']])
    if(species_version in overridden_versions):
        species_version = overridden_versions[species_version]

    annotation = ff['annotation_version']
    assembly = ff['assembly_version']
    if(species_version in base_file_versions):
       annotation=base_file_versions[species_version]['annotation']
       assembly=base_file_versions[species_version]['assembly']

    base_gm_file = "_".join([ff['Gspecies'],str(ff['proteome_id']),annotation])
    base_as_file = "_".join([ff['Gspecies'],str(ff['proteome_id']),assembly])
    if(species_version not in organism_summary):
        organism_summary[species_version]={'as_file_root':base_as_file,
                                           'gm_file_root':base_gm_file,
                                           'name':ff['proteome_name'],
                                           'release':ff['phytozome_release_id'],
                                           'taxon':ff['taxon']}

for organism in organism_summary:
    for entry in ['assembly','gene_models','proteins','annotations','synonyms','functions']:
        if(entry not in organism_summary[organism]):
            organism_summary[organism][entry]={'file':False,'path':False,'exists':False}
    
    base_as_file = organism_summary[organism]['as_file_root']
    assembly_file = ".".join([base_as_file,"fa","gz"])
    organism_summary[organism]['assembly']['file']=assembly_file

    if(organism in missing_assemblies_dict):
        organism_summary[organism]['assembly']['file']=missing_assemblies_dict[organism]

    base_gm_file = organism_summary[organism]['gm_file_root']
    gene_model_file = ".".join([base_gm_file,"gene","gff3","gz"])
    organism_summary[organism]['gene_models']['file']=gene_model_file

    protein_file    = ".".join([base_gm_file,"protein","fa","gz"])
    organism_summary[organism]['proteins']['file']=protein_file

    annotation_file = ".".join([base_gm_file,"annotation_info","txt"])
    organism_summary[organism]['annotations']['file']=annotation_file

    synonym_file    = ".".join([base_gm_file,"synonym","txt"])
    organism_summary[organism]['synonyms']['file']=synonym_file

    function_file   = ".".join([base_gm_file,"defline","txt"])
    organism_summary[organism]['functions']['file']=function_file

print(len(organism_summary.keys()))

for organism in organism_summary:
    dir_path = os.path.join(base_genome_path,organism)
    if(os.path.isdir(dir_path) is False):
        print("Organism dir not found: "+dir_path)
        break

    for entry in ['assembly','gene_models','proteins','annotations','synonyms','functions']:
        ff = str(organism_summary[organism][entry]['file'])
        organism_summary[organism][entry]['path']=os.path.join(dir_path,ff)
        organism_summary[organism][entry]['exists']=os.path.isfile(os.path.join(dir_path,ff))

with open(os.path.join('..',db_source,'JGI_Data_Portal_Files.json')) as jdpfh:
    all_files = json.load(jdpfh)

organism_file_dict=dict()
for ff in all_files:
    species_version = "_".join([ff['Gspecies'],ff['annotation_version']])
    if(species_version not in organism_file_dict):
        organism_file_dict[species_version]=list()
    organism_file_dict[species_version].append(ff)

ready_to_load=dict()
with open('Output_Files/Missing_Required_Files.txt','w') as mrffh:
    for organism in organism_summary:
        if(organism_summary[organism]['assembly']['exists'] is False or \
           organism_summary[organism]['gene_models']['exists'] is False):
            mrffh.write("===============================\n")
            mrffh.write("\t".join([organism,"Assembly:",str(organism_summary[organism]['assembly']['exists']),
                                   "Gene models:",str(organism_summary[organism]['gene_models']['exists'])])+"\n")
            for ff in organism_file_dict[organism]:
                mrffh.write("--------------------------------\n")
                for entry in ['file','annotation_version','proteome_id','phytozome_genome_id','Gspecies','version','assembly_version']:
                    mrffh.write("\t"+entry+"\t"+str(ff[entry])+"\n")

        else:
            ready_to_load[organism]=organism_summary[organism]

print(len(ready_to_load.keys()))

with open(os.path.join('..',db_source,'Phytozome_Files_to_Load.json'),'w') as pflfh:
    pflfh.write(json.dumps(ready_to_load,indent=2))

with open('Output_Files/Species_Versions_List.txt','w') as slfh:
    slfh.write('\n'.join(ready_to_load.keys()))
