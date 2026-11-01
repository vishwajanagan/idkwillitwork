import os, io
from zoneinfo import ZoneInfo
import pandas as pd
import streamlit as st
import streamlit.components.v1 as components
from src.chemistry.core import analyze_smiles, smiles_to_svg, smiles_to_png, mol_block, molecule_3d
from src.database.pubchem import search_pubchem
from src.reports.pdf import build_report
from src.ai.fallback import fallback_answer

st.set_page_config(page_title='CHEMLABS',page_icon='⚛️',layout='wide')
st.markdown('''<style>
.stApp{background:#080611;color:#F8FAFC}[data-testid="stSidebar"]{background:#100A20;border-right:1px solid #34264F}
h1,h2,h3{color:#F8FAFC!important}.stMarkdown,p,label{color:#B6B0C9}.brand{font-weight:850;letter-spacing:.12em;color:#F8FAFC}.brand span{color:#A78BFA}.kicker{color:#67E8F9;letter-spacing:.16em;font-size:.72rem;font-weight:700}.hero{background:radial-gradient(ellipse at 90% 10%,#4c1d9540,transparent 40%),linear-gradient(130deg,#18112D,#100A20);border:1px solid #34264F;border-radius:20px;padding:25px;margin-bottom:16px}.panel,.metric{background:#18112D;border:1px solid #34264F;border-radius:14px;padding:16px}.metric{min-height:90px}.metric .label{color:#B6B0C9;font-size:.78rem}.metric .value{color:#F8FAFC;font-size:1.35rem;font-weight:750;margin-top:6px}div.stButton>button,div.stDownloadButton>button{background:#8B5CF6;color:white;border:1px solid #8B5CF6;border-radius:9px;font-weight:650}div.stButton>button:hover,div.stDownloadButton>button:hover{background:#A78BFA;color:#080611;border-color:#A78BFA}div.stButton>button:focus{outline:2px solid #67E8F9;outline-offset:2px}input,textarea,[data-baseweb="select"]>div{background:#100A20!important;border-color:#34264F!important}hr{border-color:#34264F}footer{visibility:hidden}
</style>''',unsafe_allow_html=True)
if 'smiles' not in st.session_state: st.session_state.smiles='CC(=O)OC1=CC=CC=C1C(=O)O'
if 'result' not in st.session_state: st.session_state.result=None
with st.sidebar:
 st.markdown('<div class="brand">CHEM<span>LABS</div>',unsafe_allow_html=True); st.caption('MOLECULAR INTELLIGENCE LAB'); st.divider()
 page=st.radio('WORKSPACE',['Dashboard','Molecular Laboratory','Property Analysis','Molecule Comparison','AI Chemistry Assistant','Compound Explorer','Reports & Exports','About'])
 st.divider(); st.caption('Designed & Developed by Varshini A')
cols=st.columns([3,1]); cols[0].markdown('<div class="kicker">EXPLORE · VISUALIZE · ANALYZE · COMPARE</div>',unsafe_allow_html=True)
components.html("""<div id="clock" style="font:600 12px system-ui;color:#C4B5FD;text-align:right"></div><script>function t(){let d=new Date();document.getElementById('clock').innerHTML=new Intl.DateTimeFormat('en-IN',{timeZone:'Asia/Kolkata',hour:'2-digit',minute:'2-digit',second:'2-digit',hour12:false}).format(d)+' IST<br>'+new Intl.DateTimeFormat('en-IN',{timeZone:'Asia/Kolkata',weekday:'short',day:'2-digit',month:'short',year:'numeric'}).format(d)}t();setInterval(t,1000)</script>""",height=45)

def result_for(s): return analyze_smiles(s)
def identity(r):
 cs=st.columns(4)
 for c,(k,v) in zip(cs,[('Formula',r['Formula']),('Molecular weight',f"{r['Molecular Weight']:.3f} g/mol"),('RDKit LogP',f"{r['LogP']:.2f}"),('TPSA',f"{r['TPSA']:.1f} Å²")]): c.markdown(f'<div class="metric"><div class="label">{k}</div><div class="value">{v}</div></div>',unsafe_allow_html=True)
def structure(s,key):
 st.image(smiles_to_png(s),caption='RDKit-generated 2D structure',use_container_width=True)
 st.download_button('Download SVG',smiles_to_svg(s),f'{key}.svg','image/svg+xml',key=key+'svg')
 st.download_button('Download PNG',smiles_to_png(s),f'{key}.png','image/png',key=key+'png')
def get_result():
 try:
  r=analyze_smiles(st.session_state.smiles); st.session_state.result=r; return r
 except Exception as e: st.error(str(e)); return None

if page=='Dashboard':
 st.markdown('<div class="hero"><div class="kicker">MOLECULAR INTELLIGENCE & VISUALIZATION LABORATORY</div><h1 style="font-size:2.25rem">Chemistry, made <span style="color:#A78BFA">explorable.</span></h1><p>Explore. Visualize. Analyze. Compare. A focused workspace for molecular structures, calculated descriptors, comparisons, and reproducible reports.</p></div>',unsafe_allow_html=True)
 a,b,c=st.columns(3)
 for col,n,title,desc in [(a,'01','Molecular Laboratory','Validate SMILES, inspect structures, export molecular files.'),(b,'02','Property Analysis','Explore descriptors and Lipinski screening.'),(c,'03','Scientific Reports','Generate downloadable PDF reports.')]: col.markdown(f'<div class="panel"><div class="kicker">{n} / WORKSPACE</div><h3>{title}</h3><p>{desc}</p></div>',unsafe_allow_html=True)
 st.markdown('### Quick start'); ex=st.selectbox('Example molecule',['Aspirin · CC(=O)OC1=CC=CC=C1C(=O)O','Caffeine · Cn1c(=O)c2c(ncn2C)n(C)c1=O','Ethanol · CCO','Benzene · c1ccccc1','Glucose · C(C1C(C(C(C(O1)O)O)O)O)O'])
 if st.button('Load example'): st.session_state.smiles=ex.split(' · ',1)[1]; st.session_state.result=None; st.rerun()
 try: r=get_result(); identity(r); st.code(r['Canonical SMILES'])
 except Exception: pass
elif page=='Molecular Laboratory':
 st.title('Molecular Laboratory'); st.caption('SMILES are parsed and validated by RDKit.')
 ex={'Aspirin':'CC(=O)OC1=CC=CC=C1C(=O)O','Caffeine':'Cn1c(=O)c2c(ncn2C)n(C)c1=O','Ethanol':'CCO','Benzene':'c1ccccc1'}
 pick=st.selectbox('Load an example',['Choose…']+list(ex))
 if st.button('Use example') and pick!='Choose…': st.session_state.smiles=ex[pick]; st.rerun()
 st.session_state.smiles=st.text_input('SMILES notation',value=st.session_state.smiles)
 x,y,z=st.columns(3); validate=x.button('Validate & generate 2D',type='primary'); make3d=y.button('Generate 3D conformer'); clear=z.button('Clear')
 if clear: st.session_state.smiles=''; st.session_state.result=None; st.rerun()
 if validate or make3d: st.session_state.result=None
 if st.session_state.smiles.strip():
  r=get_result()
  if r:
   st.success('Valid molecular structure generated.'); identity(r); left,right=st.columns([1.15,1])
   with left: st.subheader('2D Structure'); structure(st.session_state.smiles,'molecule')
   with right:
    st.subheader('Molecular identity'); st.write('Original SMILES'); st.code(st.session_state.smiles); st.write('Canonical SMILES'); st.code(r['Canonical SMILES']); st.write(f"Atoms: {r['Atom Count']} · Bonds: {r['Bond Count']} · Charge: {r['Formal Charge']}")
    st.download_button('Download MOL',mol_block(st.session_state.smiles),'molecule.mol','chemical/x-mdl-molfile'); st.download_button('Download SDF',mol_block(st.session_state.smiles)+'$$$$\n','molecule.sdf','chemical/x-mdl-sdfile')
   if make3d:
    try: components.html(molecule_3d(st.session_state.smiles),height=500,scrolling=False); st.caption('Computational conformer, not an experimentally determined structure.')
    except Exception as e: st.error(f'3D generation failed: {e}')
 else: st.info('Enter a SMILES string to begin.')
elif page=='Property Analysis':
 st.title('Molecular Property Analysis'); st.session_state.smiles=st.text_input('SMILES',value=st.session_state.smiles,key='property_smiles')
 if st.button('Calculate descriptors',type='primary'): st.session_state.result=None
 try:
  r=get_result(); identity(r); rows=[{'Property':k,'Value':v,'Interpretation':r['Explanations'].get(k,'RDKit-calculated descriptor')} for k,v in r.items() if k not in ['Explanations','Lipinski','Elemental Composition']]; st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True); st.write('Elemental composition'); st.json(r['Elemental Composition']); st.subheader('Lipinski Rule of Five'); st.caption('Educational heuristic only—not proof of safety, activity, or clinical suitability.')
  for name,ok,detail in r['Lipinski']: st.write(('✅ ' if ok else '⚠️ ')+f'**{name}:** {detail}')
  structure(st.session_state.smiles,'property'); st.download_button('Export properties CSV',pd.DataFrame([{'Property':k,'Value':v} for k,v in r.items() if not isinstance(v,(dict,list))]).to_csv(index=False).encode(),'molecular_properties.csv','text/csv')
 except Exception as e: st.error(str(e))
elif page=='Molecule Comparison':
 st.title('Molecule Comparison'); a,b=st.columns(2); sa=a.text_input('Molecule A · SMILES','CCO'); sb=b.text_input('Molecule B · SMILES','c1ccccc1')
 if st.button('Compare molecules',type='primary'):
  try: st.session_state.comparison=(sa,sb,analyze_smiles(sa),analyze_smiles(sb))
  except Exception as e: st.error(str(e))
 if 'comparison' in st.session_state:
  sa,sb,ra,rb=st.session_state.comparison; rows=[]
  for k in ['Formula','Molecular Weight','Exact Mass','LogP','TPSA','HBD','HBA','Rotatable Bonds','Aromatic Rings','Ring Count','Atom Count','Heavy Atom Count','Bond Count','Fraction Csp3','Formal Charge']:
   va,vb=ra.get(k),rb.get(k); numeric=isinstance(va,(int,float)) and isinstance(vb,(int,float)); rows.append({'Property':k,'Molecule A':va,'Molecule B':vb,'B − A':round(vb-va,4) if numeric else '—'})
  st.dataframe(pd.DataFrame(rows),use_container_width=True,hide_index=True); ca,cb=st.columns(2)
  with ca: st.subheader('Molecule A'); structure(sa,'comparea')
  with cb: st.subheader('Molecule B'); structure(sb,'compareb')
  st.download_button('Comparison CSV',pd.DataFrame(rows).to_csv(index=False).encode(),'molecule_comparison.csv','text/csv')
elif page=='AI Chemistry Assistant':
 st.title('AI Chemistry Assistant'); key=os.getenv('OPENAI_API_KEY','').strip()
 if not key: st.info('Basic fallback mode is active. Set OPENAI_API_KEY in deployment secrets for live AI.')
 if 'chat' not in st.session_state: st.session_state.chat=[]
 for m in st.session_state.chat:
  with st.chat_message(m['role']): st.markdown(m['content'])
 prompt=st.chat_input('Ask about SMILES, LogP, TPSA, conformers…')
 if prompt:
  st.session_state.chat.append({'role':'user','content':prompt}); answer=None
  if key:
   try:
    from openai import OpenAI
    response=OpenAI(api_key=key,timeout=20).chat.completions.create(model=os.getenv('OPENAI_MODEL','gpt-4o-mini'),messages=[{'role':'system','content':'You are a careful educational cheminformatics assistant. Distinguish calculated results from experimental facts. No medical advice.'}]+st.session_state.chat[-12:]); answer=response.choices[0].message.content
   except Exception as e: answer=f'Live AI request failed ({type(e).__name__}). Fallback: '+fallback_answer(prompt)
  else: answer=fallback_answer(prompt)
  st.session_state.chat.append({'role':'assistant','content':answer}); st.rerun()
elif page=='Compound Explorer':
 st.title('Compound Database Explorer'); st.caption('PubChem PUG REST lookup; network access required.'); q=st.text_input('Compound name or identifier',placeholder='aspirin, caffeine…')
 if st.button('Search PubChem',type='primary') and q.strip():
  try: st.session_state.pubchem=search_pubchem(q)
  except Exception as e: st.error(str(e))
 if st.session_state.get('pubchem'):
  p=st.session_state.pubchem; st.subheader(p['Title']); st.write(f"PubChem CID: {p['CID']} · Source: NIH PubChem PUG REST"); st.write('Canonical SMILES'); st.code(p.get('CanonicalSMILES') or 'Unavailable'); st.write('IUPAC name:',p.get('IUPACName') or 'Unavailable'); st.write('Formula:',p.get('MolecularFormula') or 'Unavailable')
  if p.get('CanonicalSMILES') and st.button('Load into Molecular Laboratory'): st.session_state.smiles=p['CanonicalSMILES']; st.success('SMILES loaded; open Molecular Laboratory.')
elif page=='Reports & Exports':
 st.title('Reports & Exports'); st.caption('PDFs contain real RDKit-calculated values. Student image uploads are processed in memory.')
 try:
  r=analyze_smiles(st.session_state.smiles); identity(r); student=st.text_input('Student name (optional)'); reg=st.text_input('Registration number (optional)'); photo=st.file_uploader('Student photo (optional, PNG/JPG; max 2 MB)',type=['png','jpg','jpeg']); sig=st.file_uploader('Student signature (optional, PNG/JPG; max 2 MB)',type=['png','jpg','jpeg'])
  if st.button('Generate academic PDF report',type='primary'):
   if any(u and u.size>2*1024*1024 for u in [photo,sig]): st.error('Each image must be 2 MB or smaller.')
   else:
    st.session_state.pdf=build_report(st.session_state.smiles,r,student,reg,photo.getvalue() if photo else None,sig.getvalue() if sig else None); st.success('PDF generated.')
  if st.session_state.get('pdf'): st.download_button('Download Molecular Analysis Report',st.session_state.pdf,'molecular_analysis_report.pdf','application/pdf')
  st.download_button('Download MOL',mol_block(st.session_state.smiles),'molecule.mol','chemical/x-mdl-molfile'); st.download_button('Properties CSV',pd.DataFrame([{'Property':k,'Value':v} for k,v in r.items() if not isinstance(v,(dict,list))]).to_csv(index=False).encode(),'properties.csv','text/csv')
 except Exception as e: st.error(str(e))
elif page=='About':
 st.title('About CHEMLABS'); st.markdown('<div class="hero"><div class="kicker">MOLECULAR INTELLIGENCE & VISUALIZATION LABORATORY</div><h2>Explore. Visualize. Analyze. Compare.</h2><p>Designed & Developed by Varshini A</p></div>',unsafe_allow_html=True); st.write('Educational application using RDKit for parsing, depictions, calculated descriptors, and conformer generation.')
 st.markdown('**Scientific limitations**\n- Descriptors are calculated, not experimental.\n- Generated conformers are not necessarily experimental structures or global minima.\n- Lipinski rules are screening heuristics, not proof of safety or suitability.\n- PubChem and live AI require external connectivity.\n- No official SRM logo or institutional approval is represented.');
