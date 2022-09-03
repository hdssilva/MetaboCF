import pandas as pd
import codecs
from tqdm import tqdm
from rdkit.Chem.inchi import MolToInchi
from rdkit.Chem import MolFromMolBlock


# DF Columns
TAX_DICT = {'CATEGORY': 'LM.Category',
            'MAIN_CLASS': 'LM.Main Class',
            'SUB_CLASS': 'LM.Sub Class',
            'CLASS_LEVEL4': 'LM.Lv4 Class',
            'LM_ID': 'Lipid Maps ID',
            'EXACT_MASS': 'Molecular Mass',
            'FORMULA': 'Chemical Formula',
            'PUBCHEM_CID': 'PubChem ID',
            'HMDB_ID': 'HMDB ID',
            'CHEBI_ID': 'ChEBI ID',
            'LIPIDBANK_ID': 'Lipid Bank ID',
            'INCHI': 'InChI',
            'INCHI_KEY': 'InChIKey',
            'SMILES': 'SMILES'}
#Parse SDF to retrieve LMSD info
def get_LMSD(sdffile):
    f = codecs.open(sdffile + '.sdf', 'r', 'iso-8859-1')
    file = f.read()
    f.close()
    all_info = file.split('$$$$')
    all_info.pop()
    
    #List for information of each compound
    compounds_info = [] 
    for compound_txt in tqdm(all_info):
        #Dictionary for info of one compound
        compound_dic = {}
        #Retrieve compound names in database (NAME, SYSTEMATIC_NAME, and SYNONYMS)
        names = []
        for chunk in compound_txt.split('> '):
            info = chunk.split('\n')
            key = info[0][1:-1]
            value = info[1]
            #Retrieve columns in dictionary
            if key in TAX_DICT:
                if key == 'INCHI':
                    value = value.split('=')[-1]
                if key in ['CATEGORY', 'MAIN_CLASS', 'SUB_CLASS', 'CLASS_LEVEL4']:
                    value = ' '.join(value.split(' ')[:-1])
                compound_dic[TAX_DICT[key]] = value
            elif key == 'NAME' or key == 'SYSTEMATIC_NAME':
                names.append(value)
            elif key == 'SYNONYMS':
                names_to_add = value.split(';')
                for name in names_to_add:
                    if len(name)>0 and name not in names:
                        names.append(name.strip())
        compound_dic["Names"] = names
        compound_dic["Molecular Mass"] = float(compound_dic["Molecular Mass"])
        #If there is no inchi, try to retrieve it from the mol structural information
        if 'InChI' not in compound_dic:
            mol_txt = compound_txt.split('M  END')[0][1:] + 'M  END'
            mol = MolFromMolBlock(mol_txt)
            inchi = MolToInchi(mol)
            compound_dic['InChI'] = inchi.replace('InChI=', '')
        
        if len(compound_dic)>0:
            compounds_info.append(compound_dic)
    
    index = ['LM.Category', 'LM.Main Class', 'LM.Sub Class', 'LM.Lv4 Class', 'Lipid Maps ID']
    df = pd.DataFrame(compounds_info).set_index(index).sort_values(index)
    df.to_excel(sdffile + '.xlsx', merge_cells=False)
    df.to_pickle(sdffile + '.pkl')
    print(df.info())

get_LMSD('LMSD_05_05_2022')