from rdkit import Chem
from rdkit.Chem import AllChem, Descriptors, rdMolDescriptors, Draw
from rdkit.Chem.Draw import rdMolDraw2D
import io, json

EXPLANATIONS={"LogP":"RDKit-calculated octanol/water partition coefficient estimate.","TPSA":"Topological polar surface area in Å².","HBD":"Hydrogen-bond donors using RDKit's Lipinski definition.","HBA":"Hydrogen-bond acceptors using RDKit's Lipinski definition.","Rotatable Bonds":"RDKit strict rotatable bond count.","Fraction Csp3":"Fraction of carbon atoms assigned sp3 hybridization."}
def parse_smiles(smiles):
    if not isinstance(smiles,str) or not smiles.strip(): raise ValueError('Enter a SMILES string first.')
    mol=Chem.MolFromSmiles(smiles.strip())
    if mol is None: raise ValueError('Invalid SMILES. Check atom symbols, bond notation, ring closures, and bracket syntax.')
    return mol

def analyze_smiles(smiles):
    m=parse_smiles(smiles); atoms=m.GetAtoms(); carbons=sum(a.GetSymbol()=='C' for a in atoms)
    sp3=sum(a.GetSymbol()=='C' and a.GetHybridization()==Chem.HybridizationType.SP3 for a in atoms)
    mw=Descriptors.MolWt(m); logp=Descriptors.MolLogP(m); hbd=rdMolDescriptors.CalcNumHBD(m); hba=rdMolDescriptors.CalcNumHBA(m)
    result={'Formula':rdMolDescriptors.CalcMolFormula(m),'Molecular Weight':mw,'Exact Mass':Descriptors.ExactMolWt(m),'Atom Count':m.GetNumAtoms(),'Heavy Atom Count':m.GetNumHeavyAtoms(),'Bond Count':m.GetNumBonds(),'Formal Charge':sum(a.GetFormalCharge() for a in atoms),'LogP':logp,'TPSA':rdMolDescriptors.CalcTPSA(m),'HBD':hbd,'HBA':hba,'Rotatable Bonds':rdMolDescriptors.CalcNumRotatableBonds(m),'Ring Count':rdMolDescriptors.CalcNumRings(m),'Aromatic Rings':rdMolDescriptors.CalcNumAromaticRings(m),'Fraction Csp3':sp3/carbons if carbons else 0.0,'Stereocentres':rdMolDescriptors.CalcNumAtomStereoCenters(m),'Canonical SMILES':Chem.MolToSmiles(m,canonical=True),'Elemental Composition':{},'Explanations':EXPLANATIONS}
    for a in atoms: result['Elemental Composition'][a.GetSymbol()]=result['Elemental Composition'].get(a.GetSymbol(),0)+1
    result['Lipinski']=[('Molecular weight ≤ 500 Da',mw<=500,f'{mw:.2f} Da'),('LogP ≤ 5',logp<=5,f'{logp:.2f}'),('H-bond donors ≤ 5',hbd<=5,str(hbd)),('H-bond acceptors ≤ 10',hba<=10,str(hba))]
    return result

def molecule_2d(smiles):
    m=parse_smiles(smiles); AllChem.Compute2DCoords(m); return m

def smiles_to_svg(smiles,width=640,height=420):
    d=rdMolDraw2D.MolDraw2DSVG(width,height); d.DrawMolecule(molecule_2d(smiles)); d.FinishDrawing(); return d.GetDrawingText().encode()

def smiles_to_png(smiles):
    im=Draw.MolToImage(molecule_2d(smiles),size=(1000,700)); out=io.BytesIO(); im.save(out,format='PNG'); return out.getvalue()

def mol_block(smiles): return Chem.MolToMolBlock(molecule_2d(smiles))

def molecule_3d(smiles):
    m=Chem.AddHs(parse_smiles(smiles)); p=AllChem.ETKDGv3(); p.randomSeed=20261028
    if AllChem.EmbedMolecule(m,p)!=0: raise ValueError('RDKit could not generate a 3D conformer for this structure.')
    try: AllChem.MMFFOptimizeMolecule(m,maxIters=250)
    except Exception: pass
    block=json.dumps(Chem.MolToMolBlock(m))
    return f'''<div id="v" style="width:100%;height:480px;background:#FFFFFF;border-radius:12px"></div><script src="https://3Dmol.org/build/3Dmol-min.js"></script><script>const e=document.getElementById('v');if(window.$3Dmol){{const v=$3Dmol.createViewer(e,{{backgroundColor:'#FFFFFF',antialias:true}});v.addModel({block},'mol');v.setStyle({{}},{{stick:{{radius:.16}},sphere:{{scale:.24}}}});v.zoomTo();v.render();}}else{{e.innerHTML='<p style="color:#343A40;padding:20px">3D viewer unavailable; check network access.</p>'}}</script>'''
