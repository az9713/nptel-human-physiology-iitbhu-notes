"""Original Chapter 23 nonmetric diagrams. All colors and distances are schematic."""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parents[1] / "assets"

def start(title, width=1100, height=620):
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="0 0 {width} {height}" role="img" aria-label="{escape(title)}">',
            '<defs><marker id="arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0 0L10 5L0 10Z" fill="#dce7f4"/></marker></defs>',
            f'<rect width="{width}" height="{height}" fill="#112033"/>',
            f'<text x="32" y="48" fill="#f2f6fc" font-family="system-ui" font-size="27" font-weight="700">{escape(title)}</text>']

def text(a,x,y,value,size=18,color="#e5eef8",anchor="start"):
    a.append(f'<text x="{x}" y="{y}" fill="{color}" text-anchor="{anchor}" font-family="system-ui" font-size="{size}">{escape(value)}</text>')

def box(a,x,y,w,h,label,fill="#244563",size=18):
    a.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="11" fill="{fill}" stroke="#9dbbd1"/>')
    words=label.split();lines=[];line=""
    for word in words:
        trial=(line+" "+word).strip()
        if len(trial)>max(11,w//12) and line:lines.append(line);line=word
        else:line=trial
    lines.append(line)
    for i,item in enumerate(lines):text(a,x+w/2,y+h/2+(i-(len(lines)-1)/2)*24+6,item,size,anchor="middle")

def arrow(a,x1,y1,x2,y2,label="",color="#dce7f4"):
    a.append(f'<path d="M{x1} {y1}L{x2} {y2}" fill="none" stroke="{color}" stroke-width="3" marker-end="url(#arr)"/>')
    if label:text(a,(x1+x2)/2,(y1+y2)/2-10,label,15,"#b9d3e6","middle")

def save(name,a):
    (OUT/name).write_text("\n".join(a+["</svg>"]),encoding="utf8")

a=start("A neuron is not a whole peripheral nerve")
box(a,30,135,175,105,"Dendrites")
box(a,275,135,180,105,"Soma nucleus RER Golgi")
box(a,520,135,165,105,"Axon initial segment")
box(a,755,135,165,105,"Axon terminal")
arrow(a,205,187,275,187)
arrow(a,455,187,520,187)
arrow(a,685,187,755,187)
text(a,40,278,"Synaptic input → initial-segment trigger → propagating axonal event",17,"#b9d3e6")
text(a,40,325,"Separate scale: cross-section of a peripheral nerve",22)
a.append('<circle cx="275" cy="440" r="110" fill="#344b67" stroke="#e2b877" stroke-width="8"/>')
a.append('<circle cx="260" cy="440" r="65" fill="#263c57" stroke="#8fd1c8" stroke-width="7"/>')
for x,y in [(230,415),(275,410),(230,455),(285,460)]:a.append(f'<circle cx="{x}" cy="{y}" r="14" fill="#f2c56b" stroke="#eaf4ff" stroke-width="3"/>')
text(a,480,390,"Epineurium: around nerve",19,"#e2b877")
text(a,480,430,"Perineurium: around fascicle",19,"#8fd1c8")
text(a,480,470,"Endoneurium: individual axon environment",19,"#f2c56b")
text(a,40,585,"Cross-section contains axons, Schwann cells, vessels and connective tissue; neuron somata are elsewhere.",16,"#b9d3e6")
save("ch23-neuron.svg",a)

a=start("Two motions inside one axon have different physics")
box(a,35,130,185,95,"Soma")
box(a,870,130,185,95,"Terminal")
a.append('<path d="M220 176L870 176" stroke="#91b9d3" stroke-width="13"/>')
for x in [320,460,600,740]:
    a.append(f'<rect x="{x}" y="144" width="90" height="65" rx="30" fill="#58476a" stroke="#bba9d8"/>')
    text(a,x+45,125,"myelin",14,"#bba9d8","middle")
arrow(a,245,268,835,268,"voltage signal: nodal regeneration + internodal current")
arrow(a,245,335,835,335,"kinesin-family cargo: toward distal plus ends","#89ddbb")
arrow(a,835,402,245,402,"dynein cargo: toward soma minus ends","#f1c474")
text(a,50,500,"Membrane voltage travels as a propagating event; a cargo organelle physically moves on microtubules.",18)
text(a,50,545,"Arrows are topology, not measured speed or a vesicle count. Myelin colors and node spacing are schematic.",16,"#b9d3e6")
save("ch23-transport.svg",a)

a=start("Which structure is continuous across an injury?")
for i,(name,axon,sheath,distal,fill) in enumerate([
("Neurapraxia","Axon continuous","Local block/myelin change","No distal Wallerian axon loss","#2b5a69"),
("Axonotmesis","Axon interrupted","Some guide tissue preserved","Distal Wallerian degeneration","#665339"),
("Neurotmesis","Nerve discontinuous","Guidance sheaths disrupted","Distal Wallerian degeneration","#663d53")]):
    y=120+145*i
    box(a,35,y,220,105,name,fill,20)
    box(a,290,y,230,105,axon)
    box(a,555,y,230,105,sheath)
    box(a,820,y,245,105,distal)
    for x in (255,520,785):arrow(a,x,y+52,x+35,y+52)
text(a,35,590,"Seddon classes are coarse; Sunderland grades refine tissue damage and mixed lesions need separate assessment.",16,"#b9d3e6")
save("ch23-injury.svg",a)

a=start("After axonal disconnection: separate repair events")
labels=["Surviving proximal soma and stump","Distal axon/myelin breakdown","Schwann repair cells and debris clearance","Proximal sprout enters permissive path","Remyelination and target reconnection"]
for i,label in enumerate(labels):
    x=28+i*214;box(a,x,190,185,140,label,"#285268" if i<2 else "#3f5962" if i<4 else "#4b4768",17)
    if i<4:arrow(a,x+185,260,x+214,260)
text(a,42,400,"Events may overlap. A surviving distal axon does not grow backward; new extension comes from the proximal neuron.",18)
text(a,42,447,"A guide path and myelin repair do not by themselves prove target-specific function has returned.",18)
text(a,42,500,"Neurapraxia with intact axon does not enter this distal-degeneration sequence.",18,"#f1c474")
text(a,42,555,"Sequence is conceptual, not a human recovery clock or prediction of surgery.",16,"#b9d3e6")
save("ch23-repair.svg",a)
