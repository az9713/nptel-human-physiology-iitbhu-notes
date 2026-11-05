"""Original source-checked, nonmetric Chapter 24 vector context and trace exports."""
import json
from html import escape
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
D=json.loads((ROOT/'assets/ch24-model.json').read_text(encoding='utf8'))

def start(title,w=1100,h=650):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">',
            '<rect width="100%" height="100%" fill="#101c2c"/>',f'<text x="30" y="42" fill="#f0f4fb" font-family="system-ui" font-size="27" font-weight="700">{escape(title)}</text>',
            '<defs><marker id="arrow" markerWidth="10" markerHeight="8" refX="9" refY="4" orient="auto"><path d="M0 0L10 4L0 8Z" fill="#c5e3fa"/></marker></defs>']
def t(a,x,y,s,size=17,color="#e7f0f9",anchor="start"):
    a.append(f'<text x="{x}" y="{y}" text-anchor="{anchor}" fill="{color}" font-family="system-ui" font-size="{size}">{escape(str(s))}</text>')
def box(a,x,y,w,h,label,color="#294965"):
    a.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{color}" stroke="#8eb7d0"/>')
    lines=label.split('|')
    for i,line in enumerate(lines): t(a,x+w/2,y+h/2+(i-(len(lines)-1)/2)*25+5,line,17,anchor="middle")
def arrow(a,x1,y1,x2,y2,color="#c5e3fa"):
    a.append(f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{color}" stroke-width="3" marker-end="url(#arrow)"/>')
def save(name,a):
    (ROOT/'assets'/name).write_text(''.join(a)+'</svg>\n',encoding='utf8')
def lineplot(a,data,key,x0,y0,w,h,tmax,vmin,vmax,color,width=3):
    pts=' '.join(f'{x0+q["t"]/tmax*w:.2f},{y0+h-(q[key]-vmin)/(vmax-vmin)*h:.2f}' for q in data)
    a.append(f'<polyline points="{pts}" fill="none" stroke="{color}" stroke-width="{width}"/>')
def axes(a,x,y,w,h,xticks,yticks,xlabel,ylabel):
    a.append(f'<path d="M{x} {y}V{y+h}H{x+w}" fill="none" stroke="#9fb6cb" stroke-width="2"/>')
    for val,px in xticks:
        a.append(f'<path d="M{px} {y+h}V{y+h+7}" stroke="#9fb6cb"/>')
        t(a,px,y+h+29,val,15,anchor="middle")
    for val,py in yticks:
        a.append(f'<path d="M{x-7} {py}H{x}" stroke="#9fb6cb"/>')
        t(a,x-12,py+5,val,15,anchor="end")
    t(a,x+w/2,y+h+55,xlabel,17,anchor="middle")
    t(a,x-8,y-18,ylabel,17)

a=start('Membrane and chemical synapse: separate compartments',1100,690)
t(a,40,94,'A. Membrane patch: V = inside − outside',19)
a.append('<rect x="40" y="117" width="465" height="215" rx="12" fill="#263e59" stroke="#779ab5"/>')
t(a,60,152,'Extracellular fluid (outside)',18)
a.append('<path d="M65 213H480" stroke="#d5a778" stroke-width="16"/>')
t(a,60,285,'Cytosol (inside)',18)
box(a,95,178,96,70,'Na⁺|channel','#405f7d')
box(a,235,178,96,70,'K⁺|channel','#405f7d')
box(a,380,178,85,70,'3 Na⁺ out|2 K⁺ in','#405f7d')
t(a,56,315,'Selective channels carry current; ATPase maintains gradients.',15)
t(a,565,94,'B. Presynaptic terminal to postsynaptic cell',19)
box(a,575,125,195,90,'Presynaptic|cytosol')
box(a,830,125,210,90,'Vesicle membrane|synaptobrevin')
arrow(a,770,169,830,169)
a.append('<path d="M570 280H1040" stroke="#d5a778" stroke-width="15"/>')
t(a,585,266,'Presynaptic plasma membrane: syntaxin + SNAP-25',16)
box(a,605,330,405,62,'Extracellular synaptic cleft','#51445c')
arrow(a,850,289,850,324)
t(a,600,424,'Postsynaptic receptor conductance changes V toward its Erev',17)
box(a,640,448,335,75,'Postsynaptic cytosol','#355b62')
t(a,47,580,'Ca²⁺ enters through terminal voltage-gated channels; synaptotagmin senses Ca²⁺.',17)
t(a,47,612,'Primed SNAREs support fusion; a pore opens, transmitter crosses cleft, then is cleared.',17)
t(a,47,645,'Topological sketch only: no molecular geometry, distances, rates or species are measured.',15,'#b9cee0')
save('ch24-context.svg',a)

a=start('One-ion reversal and maintained multi-ion rest',1100,630)
box(a,55,115,220,90,'K⁺ only|E_K ≈ −95.0 mV')
box(a,325,115,220,90,'Na⁺ only|E_Na ≈ +60.6 mV')
box(a,595,115,440,90,'Synthetic multi-ion rest|V ≈ −68.75 mV')
t(a,55,255,'Nernst: T=310.15 K, activities approximated by stated concentrations; one permeant ion.',18)
t(a,55,290,'At its E_ion the net electrochemical flux of that ion is zero in the ideal equilibrium model.',18)
t(a,55,338,'Rest construction: g_K=0.8, g_Na=0.15, g_other=0.25 mS/cm²;',18)
t(a,55,372,'E_K=−90, E_Na=+60, E_other=−70 mV; outward pump current=2 µA/cm².',18)
t(a,55,415,'Without the imposed pump current V=−67.08 mV; with it V=−68.75 mV.',18)
t(a,55,463,'The 1.67 mV direct shift is conditional on these chosen conductances, not a universal pump voltage.',17)
t(a,55,520,'Pump stoichiometry: 3 Na⁺ out / 2 K⁺ in per ATP; gradient maintenance acts over longer times.',18)
t(a,55,565,'This figure does not imply a physiological sequence 0 → −5 → −90 → −70 mV.',16,'#b9cee0')
save('ch24-rest.svg',a)

a=start('Squid HH current-clamp trace: 6.3 °C, single compartment',1100,700)
x,y,w,h=95,110,780,330
axes(a,x,y,w,h,[(q,x+q/25*w) for q in (0,5,10,15,20,25)],[(q,y+h-(q+90)/140*h) for q in (-80,-40,0,40)],'Time (ms)','V inside − outside (mV)')
lineplot(a,D['hh']['states'],'v',x,y,w,h,25,-90,50,'#f4bf71',4)
for pulse_start,pulse_stop,amp in D['hh']['pulses_uA_cm2_ms']:
    xx=x+pulse_start/25*w
    a.append(f'<path d="M{xx} {y}V{y+h}" stroke="#91c7e5" stroke-width="1" stroke-dasharray="4 6"/>')
t(a,895,155,'V',23,'#f4bf71')
t(a,895,190,'g_Na',21,'#80c5ef')
t(a,895,225,'g_K',21,'#81d4ab')
x2,y2,w2,h2=95,515,780,90
gmin,gmax=0,45
gy=lambda g:y2+h2-(g-gmin)/(gmax-gmin)*h2
axes(a,x2,y2,w2,h2,[(q,x2+q/25*w2) for q in (0,5,10,15,20,25)],[(g,gy(g)) for g in (0,15,30,45)],'Time (ms)','g (mS/cm²)')
lineplot(a,D['hh']['states'],'gNa',x2,y2,w2,h2,25,gmin,gmax,'#80c5ef',3)
lineplot(a,D['hh']['states'],'gK',x2,y2,w2,h2,25,gmin,gmax,'#81d4ab',3)
t(a,925,535,'Pulses at 1, 6, 18 ms',15)
t(a,925,565,'equal amplitude',15)
t(a,925,600,'early repeat fails',15)
save('ch24-ap.svg',a)

a=start('Synthetic RC synapse: reversal and shunt, no spike model',1100,690)
x,y,w,h=90,105,800,360
axes(a,x,y,w,h,[(q,x+q/40*w) for q in (0,10,20,30,40)],[(q,y+h-(q+75)/25*h) for q in (-75,-70,-65,-60,-55,-50)],'Time (ms)','V inside − outside (mV)')
for key,col in [('exc_only','#f4bf71'),('shunt','#80c5ef'),('depolarizing_GABA','#c6a5ee')]:
    lineplot(a,D['synapse'][key],'v',x,y,w,h,40,-75,-50,col,3)
for i,(lab,col) in enumerate([('Exc only','#f4bf71'),('Exc + GABA, E_GABA=−70','#80c5ef'),('Exc + GABA, E_GABA=−60','#c6a5ee')]):
    t(a,110,525+i*35,lab,17,col)
t(a,110,647,'Onset at 8 ms; conductances and V share one state table. No presynaptic Ca/fusion kinetics fit.',16,'#b9cee0')
save('ch24-synapse.svg',a)
