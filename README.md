# Assembly interfaces analysis 

## Basic information

This python package works with PISA-Lite to analyse data for macromolecular interfaces and interactions in assemblies.

The code will:
- Analyse macromolecular interfaces with PISA
- Create Json dictionary with assembly interactions/interfaces information

## Usage 

```
git clone  https://github.com/PDBe-KB/pisa-analysis

cd pisa-analysis 

``` 
Dependecies:

```
pip install -r requirements.txt

```

usage: 

```
pisa-analysis/run/run.py [-h] -c PISA_CONFIGURATION_FILE --pdb_id PDB_ID --assembly_id ASSEMBLY_CODE -o OUTPUT_PATH
```
OR
```
pisa-analysis/run/run.py --config PISA_CONFIGURATION_FILE  --pdb_id PDB_ID --assembly_id ASSEMBLY_CODE --output-dir OUTPUT_PATH
```
OR install module **pisa_analysis**:

```
cd pisa-analysis/

python setup.py install
```
usage: pisa_analysis [-h] -c PISA_CONFIGURATION_FILE --pdb_id PDB_ID --assembly_id ASSEMBLY_CODE -o OUTPUT_PATH


Other optional arguments are:

```
--input_updated_cif
--pisa_binary 
--result_json 
--input_cif_file 
--force  
```
**input_updated_cif**: updated cif file, by default process reads 'XXX_updated.cif' where XXX is the pdb_id entry

**pisa_binary** : path to PISA binary, by default uses environmental variable 'pisa'

**result_json** : Select different name for the output json file. By default it writes '[pdb_id]-assembly[assembly_code].json

**input_cif_file**: Provide input cif file, by default it reads '[pdb_id]-assembly[assembly_code].cif.gz

**force**: always runs PISA and recalculates interfaces

The process runs PISA-Lite in a subprocess and needs a binary path to PISA. For more information on how to compile PISA-LITE visit our internal page: 

https://www.ebi.ac.uk/seqdb/confluence/pages/viewpage.action?spaceKey=PDBE&title=Interaction+and+interfaces+-+assemblies

The process is as follows:

1. The process first runs PISA-Lite in a subprocess and generates two xml files:
   - interfaces.xml
   - assembly.xml
   
    The xml files are saved in the output directory defined by the -o or --output-path arguments. If the xml files exist and are valid, the process wil.          skip running PISA-Lite unless the --force is used in the arguments. 

2. Next, the process parses xml files generated by PISA-Lite and creates a dictionary that contains all assembly interfaces/interactions information. 

3. While creating the assembly dictionary, the process reads Uniprot accession and sequence numbers from an Updated CIF file using Gemmi. 

4. In the last step, the process dumps the dictionary into a json file. The json file is saved in the output directory defined by the -o or --output-path arguments. The output json file is:
  
     xxx-assembly*.json 
  
     where xxx is the pdb id entry and * is the assembly code. 
  

## Expected JSON file

Documentation on the output json file and schema can be found here: 

https://pisalite.docs.apiary.io/#reference/0/pisaqualifierjson/interaction-interface-data-per-pdb-assembly-entry


## Dependencies 

See  [requirements.txt](https://github.com/PDBe-KB/pisa-analysis/requirements.txt)

For development: 

### pre-commit usage

```
pip install pre-commit
pre-commit
pre-commit install
```

## Versioning

We use [SemVer](https://semver.org) for versioning.

## Authors
Grisell Diaz Leines

Mihaly Varadi 

## License

See  [license.txt](https://github.com/PDBe-KB/pisa-analysis/license.txt

## Acknowledgements
