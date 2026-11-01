import requests

def search_pubchem(query):
    if not query or not query.strip(): raise ValueError('Enter a compound name or identifier.')
    url='https://pubchem.ncbi.nlm.nih.gov/rest/pug/compound/name/'+requests.utils.quote(query.strip(),safe='')+'/property/Title,IUPACName,MolecularFormula,CanonicalSMILES/JSON'
    try:
        r=requests.get(url,timeout=(4,12),headers={'User-Agent':'ChemLabsVarshini/1.0 educational'} )
        if r.status_code==404: raise ValueError(f'No PubChem compound found for “{query}”.')
        r.raise_for_status(); p=r.json()['PropertyTable']['Properties'][0]
        return {'CID':p.get('CID'),'Title':p.get('Title',query),'IUPACName':p.get('IUPACName'),'MolecularFormula':p.get('MolecularFormula'),'CanonicalSMILES':p.get('ConnectivitySMILES') or p.get('CanonicalSMILES'),'Source':'NIH PubChem PUG REST'}
    except requests.Timeout as e: raise RuntimeError('PubChem request timed out.') from e
    except requests.RequestException as e: raise RuntimeError('Could not reach PubChem. Check network access.') from e
