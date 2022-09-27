import xml.etree.ElementTree as ET
import numpy as np
import pandas as pd
from rdkit.Chem.inchi import InchiToInchiKey, MolToInchiAndAuxInfo
from rdkit.Chem.rdmolfiles import MolFromSmiles, MolFromMolBlock
from rdkit import Chem
from tqdm import tqdm

#This function separates metabolites in the xml 
def generate_xml_chunks(xmlfile):
    reading = False
    for line in xmlfile:
        line=line.strip()
        if not reading:
            if not '<metabolite>' in line:
                continue
            else:
                reading = True              #start reading chunk when beginning of metabolite is found
                chunk = []                  #list with lines for one chunk
                chunk.append(line)
        else: # reading
            if '</metabolite>' not in line: #append lines while end of chunk is not found
                chunk.append(line)
            else:                           #return chunk when end is found
                reading = False
                chunk.append(line)
                yield '\n'.join(chunk)

#This function takes an sdf file and returns its structures
def get_structures(sdfname):
    with open(sdfname, encoding='utf8') as f:
        chunks = f.read().split('$$$$')
    
    all_structures = {}
    for chunk in tqdm(chunks):
        if len(chunk)>0:
            id = ''
            chunk = chunk.split('> ')
            if len(chunk)>1:
                id = chunk[1].split('\n')[1]
                mol_struct = chunk[0]
                if id != '' and mol_struct != '':
                    all_structures[id] = mol_struct
    return all_structures

#Summary info of HMDB into a pandas DF.
def get_HMDB(xmlfilename, sdfname):
    
    #Return this columns, with the correspondent key in xml
    FIELDS_DICT = {'HMDB ID': 'accession',
                'Chemical Formula': 'chemical_formula',
                'Monoisotopic Mass': 'monisotopic_molecular_weight',
                'Molecular Mass': 'average_molecular_weight',
                'CAS': 'cas_registry_number',
                'InChI': 'inchi',
                'InChIKey': 'inchikey',
                'SMILES': 'smiles'}
    
    
    chemont = {'kingdom': 'ChemOnt.Kingdom', 'super_class': 'ChemOnt.SuperClass', 
                        'class': 'ChemOnt.Class', 'sub_class': 'ChemOnt.SubClass'}
    OtherDb = {'kegg_id': 'KEGG ID', 'chebi_id': 'ChEBI ID', 'pubchem_compound_id': 'PubChem ID'}

    extracted = []
    print(f'extracting {sdfname} data')

    all_structures = get_structures(sdfname + '.sdf')

    print(f'extracting {xmlfilename} data')

    with open(xmlfilename + '.xml', encoding='utf8') as datafile:
        #iterate each metabolite xml chunk
        for i, record in tqdm(enumerate(generate_xml_chunks(datafile))):
            extracted_dict = {}
            root = ET.fromstring(record)
            
            if str(root.tag) != 'metabolite':
                print('WARNING, BAD root tag', i, root.tag)
                break
            #list with all names, synonyms, and iupac names
            names = [root.find('name').text] 
            synonyms = root.find('synonyms')
            for synonym in root.findall('synonym'):
                if synonym.text not in names:
                    names.append(synonym.text)
            try:
                names.append(root.find('iupac_name').text)
            except:
                pass
            try:
                names.append(root.find('traditional_iupac').text)
            except:
                pass
            if len(names)>0:
                extracted_dict['Names'] = list(set(names))
            #Extract info in FIELDS_DICT, with the corresponding key
            for name, tagname in FIELDS_DICT.items():
                tag = root.find(tagname)
                if tag is None:
                    continue
                else:
                    if tag.text is not None:
                        extracted_dict[name] = tag.text
                        if tagname == 'inchi':
                            extracted_dict[name] = tag.text.split('=')[-1]
            #Extract the ChemOnt classification (Kingdom, Superclass, Class and Subclass)
            for subchild in root.findall('taxonomy'):
                for tag, name in chemont.items():
                    try:
                        extracted_dict[name] = subchild.find(tag).text
                    except:
                        pass
            #Extract external references of other databases
            for db in OtherDb.keys():
                try:
                    extracted_dict[OtherDb[db]] = root.find(db).text
                except:
                    pass
            #If the inchi is not found, see if there is structure in sdf to compute inchi using the rdkit package
            #If there is no sdf structure or inchi was not retrieved (error), try to retrieve it from SMILES
            if 'InChI' not in extracted_dict:
                mol = None
                if extracted_dict['HMDB ID'] in all_structures:
                    mol = MolFromMolBlock(all_structures[extracted_dict['HMDB ID']])
                
                if mol is None and 'SMILES' in extracted_dict:
                    mol = MolFromSmiles(extracted_dict['SMILES'])
                else:
                    #No MOL/SMILES info
                    pass
                if mol is not None:
                    inchi = MolToInchiAndAuxInfo(mol)[0]
                    extracted_dict['InChI'] = inchi.replace('InChI=', '')
                    extracted_dict['InChIKey'] = InchiToInchiKey(inchi).replace('InChIKey=', '')
            if 'Molecular Mass' in extracted_dict:
                extracted_dict['Molecular Mass'] = float(extracted_dict['Molecular Mass'])
            if 'Monoisotopic Mass' in extracted_dict:
                extracted_dict['Monoisotopic Mass'] = float(extracted_dict['Monoisotopic Mass'])
            if len(extracted_dict)>0:
                extracted.append(extracted_dict)

    print(f'{len(extracted)} metabolite records in file {xmlfilename}')

    index = ['ChemOnt.Kingdom', 'ChemOnt.SuperClass', 'ChemOnt.Class', 'ChemOnt.SubClass', 'HMDB ID']
    df = pd.DataFrame(extracted).set_index(index).sort_values(index)
    df.to_excel(xmlfilename + '.xlsx', sheet_name = 'Metabolites', merge_cells=False)
    df.to_pickle(xmlfilename + '.pkl')
    df.info()

get_HMDB('hmdb_metabolites(17_11_2021)', 'hmdb_structures(02_11_2021)')