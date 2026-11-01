import io
from datetime import datetime
try:
    from zoneinfo import ZoneInfo
except ImportError:
    from backports.zoneinfo import ZoneInfo
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image, PageBreak, KeepTogether
from rdkit import Chem
from rdkit.Chem import AllChem, Draw

def _png(smiles):
    m=Chem.MolFromSmiles(smiles)
    if m is None: raise ValueError('Invalid SMILES')
    AllChem.Compute2DCoords(m); im=Draw.MolToImage(m,size=(1000,560)); b=io.BytesIO(); im.save(b,format='PNG'); b.seek(0); return b

def _3d_png(smiles):
    import matplotlib; matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    m=Chem.AddHs(Chem.MolFromSmiles(smiles))
    if AllChem.EmbedMolecule(m,randomSeed=20261028)!=0: return None
    try: AllChem.MMFFOptimizeMolecule(m,maxIters=180)
    except Exception: pass
    xyz=m.GetConformer().GetPositions(); fig=plt.figure(figsize=(6,3.6),facecolor='#100A20'); ax=fig.add_subplot(111,projection='3d',facecolor='#100A20')
    ec={'C':'#B6B0C9','O':'#FB7185','N':'#67E8F9','S':'#FBBF24','H':'#F8FAFC','F':'#34D399','Cl':'#34D399'}
    for i,a in enumerate(m.GetAtoms()): ax.scatter(*xyz[i],s=38 if a.GetSymbol()!='H' else 10,color=ec.get(a.GetSymbol(),'#A78BFA'))
    for bond in m.GetBonds():
        i,j=bond.GetBeginAtomIdx(),bond.GetEndAtomIdx(); ax.plot(xyz[[i,j],0],xyz[[i,j],1],xyz[[i,j],2],color='#8B5CF6',linewidth=1.2)
    ax.set_axis_off(); b=io.BytesIO(); fig.savefig(b,format='png',dpi=140,facecolor=fig.get_facecolor(),bbox_inches='tight'); plt.close(fig); b.seek(0); return b

def build_report(smiles,result,student='',registration='',photo_bytes=None,signature_bytes=None):
    out=io.BytesIO(); doc=SimpleDocTemplate(out,pagesize=A4,rightMargin=18*mm,leftMargin=18*mm,topMargin=16*mm,bottomMargin=18*mm,title='Molecular Analysis Report',author='CHEMLABSVARSHINI')
    s=getSampleStyleSheet(); s.add(ParagraphStyle(name='VioletTitle',parent=s['Title'],textColor=colors.HexColor('#8B5CF6'),fontSize=19)); s.add(ParagraphStyle(name='SectionV',parent=s['Heading2'],textColor=colors.HexColor('#8B5CF6'),fontSize=13,spaceBefore=8,spaceAfter=6)); s.add(ParagraphStyle(name='Tiny',parent=s['BodyText'],fontSize=8,textColor=colors.HexColor('#55516A')))
    story=[Paragraph('CHEMLABSVARSHINI',s['VioletTitle']),Paragraph('Molecular Intelligence & Visualization Laboratory',s['Normal']),Paragraph('MOLECULAR ANALYSIS REPORT',s['Heading1'])]
    now=datetime.now(ZoneInfo('Asia/Kolkata')).strftime('%d %b %Y · %H:%M:%S IST'); story.append(Paragraph('Generated: '+now,s['Tiny']))
    if student or registration or photo_bytes:
        data=[['Student name',student or 'Not provided'],['Registration number',registration or 'Not provided']]
        if photo_bytes:
            try: data.append(['Student photo',Image(io.BytesIO(photo_bytes),width=22*mm,height=26*mm,kind='proportional')])
            except Exception: data.append(['Student photo','Image could not be rendered'])
        t=Table(data,colWidths=[45*mm,110*mm]); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,-1),colors.HexColor('#F3EEFF')),('GRID',(0,0),(-1,-1),.4,colors.HexColor('#D9D0EE')),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('PADDING',(0,0),(-1,-1),6)])); story += [Paragraph('Student details',s['SectionV']),t]
    story += [Paragraph('Molecular identity',s['SectionV']),Paragraph(f"<b>Formula:</b> {result['Formula']} &nbsp;&nbsp; <b>Canonical SMILES:</b> {result['Canonical SMILES']}",s['BodyText']),Paragraph('Calculated properties',s['SectionV'])]
    units={'Molecular Weight':'g/mol','Exact Mass':'Da','TPSA':'Å²','LogP':'dimensionless','Fraction Csp3':'fraction'}; rows=[['Property','Calculated value','Units / notes']]
    for k in ['Molecular Weight','Exact Mass','Atom Count','Heavy Atom Count','Bond Count','Formal Charge','LogP','TPSA','HBD','HBA','Rotatable Bonds','Ring Count','Aromatic Rings','Fraction Csp3','Stereocentres']:
        v=result.get(k); rows.append([k,'Unavailable' if v is None else (f'{v:.4f}' if isinstance(v,float) else str(v)),units.get(k,'count')])
    t=Table(rows,colWidths=[54*mm,42*mm,59*mm],repeatRows=1); t.setStyle(TableStyle([('BACKGROUND',(0,0),(-1,0),colors.HexColor('#21163D')),('TEXTCOLOR',(0,0),(-1,0),colors.white),('GRID',(0,0),(-1,-1),.35,colors.HexColor('#D9D0EE')),('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,colors.HexColor('#F3EEFF')]),('FONTSIZE',(0,0),(-1,-1),8),('VALIGN',(0,0),(-1,-1),'MIDDLE'),('PADDING',(0,0),(-1,-1),5)])); story.append(t)
    story += [PageBreak(),Paragraph('2D Molecular Structure',s['SectionV']),Paragraph('RDKit-generated molecular depiction.',s['Tiny']),Image(_png(smiles),width=150*mm,height=84*mm,kind='proportional'),Paragraph('3D Molecular Structure',s['SectionV'])]
    im3=_3d_png(smiles)
    if im3: story += [Paragraph('Computational conformer; not an experimentally determined structure.',s['Tiny']),Image(im3,width=135*mm,height=75*mm,kind='proportional')]
    else: story.append(Paragraph('A 3D conformer could not be generated. No substitute image is shown.',s['BodyText']))
    story += [Paragraph('Lipinski Rule of Five screening',s['SectionV']),Paragraph('Educational heuristic only; not proof of safety, activity, or clinical suitability.',s['Tiny'])]
    for name,ok,detail in result['Lipinski']: story.append(Paragraph(('PASS — ' if ok else 'THRESHOLD EXCEEDED — ')+name+': '+detail,s['BodyText']))
    signature_block = [Spacer(1,8*mm),Paragraph('Student signature',s['SectionV'])]
    if signature_bytes:
        try: signature_block.append(Image(io.BytesIO(signature_bytes),width=48*mm,height=20*mm,kind='proportional'))
        except Exception: signature_block.append(Paragraph('Signature image could not be rendered.',s['Tiny']))
    else: signature_block.append(Spacer(1,12*mm))
    signature_block += [Paragraph('Faculty signature / approval',s['SectionV']),Spacer(1,18*mm),Paragraph('Faculty signature: __________________________________   Date: ______________',s['Normal']),Spacer(1,5*mm),Paragraph('Automatically generated educational report; not an official institutional document and not faculty-approved.',s['Tiny']),Paragraph('Designed & Developed by Varshini A',s['Tiny'])]
    story.append(KeepTogether(signature_block))
    def footer(c,d):
        c.saveState(); w,h=A4; c.setStrokeColor(colors.HexColor('#D9D0EE')); c.line(18*mm,13*mm,w-18*mm,13*mm); c.setFont('Helvetica',8); c.setFillColor(colors.HexColor('#55516A')); c.drawString(18*mm,8*mm,'CHEMLABSVARSHINI · Educational report'); c.drawRightString(w-18*mm,8*mm,f'Page {d.page}'); c.restoreState()
    doc.build(story,onFirstPage=footer,onLaterPages=footer); return out.getvalue()
