import pandas as pd
import codecs
from tqdm import tqdm
from rdkit.Chem import MolFromMolBlock
from rdkit.Chem.inchi import MolToInchiAndAuxInfo, InchiToInchiKey

#Parse SDF to retrieve ChEBI info
def get_ChEBI(sdffile):
    TAX_DICT = {'ChEBI ID': 'ChEBI ID',
                'Secondary ChEBI ID': "Secondary ChEBI ID's",
                'Mass': 'Molecular Mass',
                'Monoisotopic Mass': 'Monoisotopic Mass',
                'Formulae': 'Chemical Formula',
                'InChI': 'InChI',
                'InChIKey': 'InChIKey',
                'SMILES': 'SMILES'}
    f = codecs.open(sdffile + '.sdf', 'r', 'iso-8859-1')
    file = f.read()
    f.close()
    #Split sdf file into compound
    all_info = file.split('$$$$')
    #List for information of each compound
    compounds_info = []
    for compound_txt in tqdm(all_info):
        #Dictionary for info of one compound
        compound_dic = {}
        #Retrieve compound names in database (ChEBI Name and Synonyms)
        names = []
        for chunk in compound_txt.split('> <'):
            info = chunk.split('\n')
            key = info[0][0:-1]
            value = info[1]
            #Retrieve columns in dictionary
            if key in TAX_DICT:
                if key == 'InChI':
                    value = value.split('=')[-1]
                elif key == 'ChEBI ID':
                    value = str(value.split(':')[-1])
                elif key == "Secondary ChEBI ID":
                    value = [ID.split(':')[-1] for ID in info[1:-2]]
                elif key == 'Formulae':
                    value = [form for form in info[1:-2]]
                    if len(value) == 1:
                        value=value[0]
                compound_dic[TAX_DICT[key]] = value
                
            elif key == 'ChEBI Name':
                names.append(value)
            elif key == 'Synonyms':
                values = info[1:]
                for name in values:
                    if len(name)>0 and name not in names:
                        names.append(name.strip())
        if len(names)>0:
            compound_dic["Names"] = names
        if 'Molecular Mass' in compound_dic:
            compound_dic["Molecular Mass"] = float(compound_dic["Molecular Mass"])
        if 'Monoisotopic Mass' in compound_dic:
            compound_dic["Monoisotopic Mass"] = float(compound_dic["Monoisotopic Mass"])
        
        #If inchi is not returned
        if 'InChI' not in compound_dic:
            #Try to get InChI from mol info in sdf
            split = compound_txt.split('M  END')
            if len(split)<=1:
                #compound_dic['InChI'] = 'No MOL info'
                #compound_dic['InChIKey'] = 'No MOL info'
                pass
            else: 
                mol_txt = split[0][1:] + 'M  END'
                mol = MolFromMolBlock(mol_txt)
                if mol is None:
                    #compound_dic['InChI'] = 'Failed to parse MOL'
                    #compound_dic['InChIKey'] = 'Failed to parse MOL'
                    pass
                else:
                    try:
                        inchi = MolToInchiAndAuxInfo(mol)[0]
                    except:
                        inchi = ''
                    if inchi == '':
                        #No InChI returned (Radical/Polymer)
                        #compound_dic['InChI'] = 'No InChI returned (Radical/Polymer)'
                        #compound_dic['InChIKey'] = 'No InChI returned (Radical/Polymer)'
                        pass
                    else:
                        compound_dic['InChI'] = inchi.replace('InChI=', '')
                        inchikey = InchiToInchiKey(inchi)
                        compound_dic['InChIKey'] = inchikey.replace('InChI=', '')
        
        if len(compound_dic)>0:
            compounds_info.append(compound_dic)

    df = pd.DataFrame(compounds_info).set_index('ChEBI ID').sort_index()
    df.to_pickle(sdffile + '.pkl')
    df.to_excel(sdffile + '.xlsx')
    print(df.info())
    
get_ChEBI('ChEBI_complete_04_04_2022')