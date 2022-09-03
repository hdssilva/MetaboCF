from tqdm import tqdm
import pandas as pd
import requests
from rdkit.Chem.rdinchi import *
import os
import pickle as pk
import time
#This script works with KEGG's API

#Request a list of KEGG compounds and saves it into a file
def list_request(path):
    url = 'http://rest.kegg.jp/list/compound'
    r = requests.get(url)
    #txt has the KEGG compound identifier and respective name
    with open(path + "_list.txt", "w") as f:
        f.write(r.text)
    #pickle is the c_list, only with the identifiers
    c_list = []
    for line in r.text.splitlines():
        c_list.append(line.split()[0].split(":")[1])
    with open(path + "_list.pkl", 'wb') as f:
        pk.dump(c_list, f)

#Reads pickle list of KEGG compounds and individually requests each compound into a text file
def compound_request(path):
    #get compound list
    with open(path + '_list.pkl', "rb") as f:
        c_list = pk.load(f)
    #make compounds request
    url = 'http://rest.kegg.jp/get/'
    for compound in tqdm(c_list):
        print(compound)
        while True:
            try:
                r = requests.get(url + compound)
                txt = r.text[:-4] + '\n'
                r = requests.get(url + compound + '/mol')
                with open(path + "_info.txt", "a") as f:
                    f.write(txt + 'MOL\n' + r.text.split('M  END')[0] + 'M  END\n///\n')
                break
            except:
                time.sleep(5)
                continue

#Parse text file with compound info and retrieve the information
def get_compound_info(path):
    #open requested compound info
    with open(path + "_info.txt", "r") as f:
        compounds_info = f.read().split('///')
    #List for information of each compound
    all_compounds = []
    for compound_info in tqdm(compounds_info):
        lines = compound_info.splitlines()
        #Dictionary for info of one compound
        dic = {}
        #Dictionary with only external references of databases
        db_links = {}
        #Get all info (KEGG ID, Names, Chemical formula, masses, Brite and external links)
        for i in range(len(lines)):
            line = lines[i]
            if line.startswith('ENTRY'):
                dic['KEGG ID'] = line.split()[1]
            #Append all compound names to a list
            if line.startswith('NAME'):
                names = [line.split()[1].strip(';')]
                for z in range(i+1, len(lines)):
                    line = lines[z]
                    if line.startswith(' '):
                        names.append(line.strip(' ;'))
                    else:
                        break
                dic['Names'] = list(set(names))
            elif line.startswith('FORMULA'):
                dic['Chemical Formula'] = line.split()[1]
                if line.split()[1][-1]=='.':
                    dic['Chemical Formula'] = ''.join(line.split()[1:])
            elif line.startswith('EXACT_MASS'):
                dic['Monoisotopic Mass'] = float(line.split()[1])
            elif line.startswith('MOL_WEIGHT'):
                dic['Molecular Mass'] = float(line.split()[1])
            elif line.startswith('BRITE'):
                brite = [line.replace("BRITE       ", "")]
                for z in range(i+1, len(lines)):
                    line = lines[z]
                    if line.startswith(' '):
                        brite.append(line.replace('       ', ''))
                    else:
                        break
                dic['BRITE'] = "".join(brite)
            elif line.startswith('DBLINKS'):
                link = line.replace('DBLINKS     ', '')
                db_links[link.split(':')[0]] = link.split(':')[1][1:]
                for z in range(i+1, len(lines)):
                    line = lines[z]
                    if line.startswith(' '):
                        link = line.replace('            ', '')
                        db_links[link.split(':')[0]] = link.split(':')[1][1:]
                    else:
                        break
            #KEGG does not have inchi. All inchies were computed from the mol info
            elif line.startswith('MOL'):
                molblock = ''
                for z in range(i+1, len(lines)):
                    line = lines[z]
                    if not line.startswith('M  END'):
                        molblock += line + '\n'
                    else:
                        if molblock == '':
                            #No MOL info
                            #dic['InChI'] = 'No MOL info'
                            #dic['InChIKey'] = 'No MOL info'
                            break
                        molblock += line
                        inchi_tuple = MolBlockToInchi(molblock)
                        inchi = inchi_tuple[0]
                        inchikey = InchiToInchiKey(inchi)
                        if inchi_tuple[1] == 2:
                            #Polymer/Radicals
                            #dic['InChI'] = 'Polymer/Radicals'
                            #dic['InChIKey'] = 'Polymer/Radicals'
                            break
                        dic['InChI'] = inchi.replace('InChI=', '')
                        dic['InChIKey'] = inchikey.replace('InChIKey=', '')
                        
        for db in db_links.keys():
            if db in ['CAS', 'PubChem', 'ChEBI', 'LIPIDMAPS', 'LipidBank']:
                if db == 'LIPIDMAPS':
                    dic['Lipid Maps ID'] = db_links[db].split()
                elif db == 'LipidBank':
                    dic['Lipid Bank ID'] = db_links[db].split()
                elif db == 'CAS':
                    dic[db] = db_links[db].split()
                else:
                    dic[db + ' ID'] = db_links[db].split()
        if len(dic)>0:
            all_compounds.append(dic)
    df = pd.DataFrame(all_compounds).set_index('KEGG ID')
    with open(path + '_list.pkl', "rb") as f:
        c_list = pk.load(f)
    print(f'There is a total of {len(c_list)} compounds, {len(df)} compounds in the Dataframe')
    df.info()
    df.to_excel(path + '.xlsx')
    df.to_pickle(path + '.pkl')

path = 'KEGG_compounds(22_10_2021)'
list_request(path)
compound_request(path)
get_compound_info(path)