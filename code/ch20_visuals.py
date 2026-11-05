"""Generate original nonmetric static Chapter 20 mechanism diagrams.

All geometry is schematic; no anatomical appearance or measured time claim.
"""
from pathlib import Path
from html import escape

OUT = Path(__file__).resolve().parents[1] / "assets"


def svg_start(title: str, w=1100, h=650) -> list[str]:
    return [f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}" role="img" aria-label="{escape(title)}">',
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M 0 0 L 10 5 L 0 10 z" fill="#d5e8f6"/></marker></defs>',
            f'<rect width="{w}" height="{h}" fill="#102032"/>',
            f'<text x="35" y="48" fill="#f1f6fc" font-family="system-ui" font-size="28" font-weight="700">{escape(title)}</text>']


def box(a: list[str], x: int, y: int, w: int, h: int, label: str, color="#244363") -> None:
    a.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="12" fill="{color}" stroke="#a9c4d9"/>')
    if label:
        words = label.split()
        lines, line = [], ""
        for word in words:
            trial = (line + " " + word).strip()
            if len(trial) > max(15, w // 12) and line:
                lines.append(line); line = word
            else:
                line = trial
        lines.append(line)
        font = 19 if len(lines) > 1 else 21
        start_y = y + h / 2 + (6 if len(lines) == 1 else -4)
        for i, part in enumerate(lines):
            a.append(f'<text x="{x+w/2}" y="{start_y+i*25}" text-anchor="middle" fill="white" font-family="system-ui" font-size="{font}">{escape(part)}</text>')


def arrow(a: list[str], x1: int, y1: int, x2: int, y2: int, label="") -> None:
    a.append(f'<path d="M{x1} {y1} L{x2} {y2}" stroke="#d5e8f6" stroke-width="3" marker-end="url(#arrow)"/>')
    if label:
        a.append(f'<text x="{(x1+x2)//2}" y="{(y1+y2)//2-10}" text-anchor="middle" fill="#c8d9e6" font-family="system-ui" font-size="16">{escape(label)}</text>')


def note(a: list[str], x: int, y: int, value: str) -> None:
    a.append(f'<text x="{x}" y="{y}" fill="#bdd4e5" font-family="system-ui" font-size="18">{escape(value)}</text>')


def save(name: str, a: list[str]) -> None:
    (OUT/name).write_text("\n".join(a+["</svg>"]), encoding="utf-8")


a=svg_start("Two organs and a feedback route")
box(a,35,110,205,72,"Hypothalamus")
box(a,310,110,210,72,"Anterior pituitary")
box(a,615,100,210,85,"Theca interna")
box(a,615,260,210,85,"Granulosa")
box(a,870,260,190,85,"Estradiol")
box(a,615,450,210,85,"Corpus luteum")
box(a,870,450,190,85,"Endometrium")
arrow(a,240,146,310,146,"GnRH")
arrow(a,520,145,615,145,"LH")
arrow(a,520,165,615,300,"FSH")
arrow(a,720,185,720,260,"androgen")
arrow(a,825,303,870,303,"aromatase")
a.append('<path d="M965 260 L965 75 L415 75 L415 110" fill="none" stroke="#d5e8f6" stroke-width="2" stroke-dasharray="7 6" marker-end="url(#arrow)"/>')
note(a,565,68,"Feedback: mainly −; sustained high E₂ supports + LH surge")
arrow(a,965,345,965,450,"proliferation")
arrow(a,825,493,870,493)
note(a,630,575,"Luteal output: progesterone and estradiol")
note(a,36,607,"Follicular growth → ovulation/LH surge → luteal secretion → withdrawal or hCG rescue")
save("ch20-cycle.svg",a)

a=svg_start("Location and order: fertilization to implantation",1000,650)
box(a,40,140,245,82,"Tubal ampulla")
box(a,375,140,245,82,"Transit toward uterus")
box(a,710,140,245,82,"Uterine endometrium")
arrow(a,285,180,375,180)
arrow(a,620,180,710,180)
box(a,42,300,220,76,"Sperm–oocyte fusion")
box(a,290,300,190,76,"Pronuclei")
box(a,510,300,190,76,"Cleavage/morula")
box(a,730,300,220,76,"Blastocyst")
arrow(a,262,338,290,338)
arrow(a,480,338,510,338)
arrow(a,700,338,730,338)
box(a,715,450,230,76,"Apposition/invasion","#4b3b64")
arrow(a,840,376,840,450)
note(a,42,575,"Approximate post-fertilization order; neither cell counts nor transport speed are measured here.")
save("ch20-fertilization.svg",a)

a=svg_start("Term villus: exchange across separate blood compartments",1000,650)
box(a,50,145,330,170,"Maternal intervillous blood","#6b3345")
box(a,600,145,330,170,"Fetal capillary blood","#284f75")
box(a,412,130,155,210,"","#514061")
note(a,424,330,"Villous barrier")
arrow(a,380,200,600,200,"O₂, nutrients")
arrow(a,600,265,380,265,"CO₂, wastes")
note(a,58,408,"Maternal red cells remain outside the villus in the illustrated section.")
note(a,58,450,"Fetal red cells remain inside villous capillaries.")
note(a,58,535,"Net solute exchange is not wholesale mixing of the two blood streams.")
save("ch20-placenta.svg",a)

a=svg_start("Labor events, not a universal stopwatch",1000,600)
labels=["Effacement and dilation","Complete dilation ~10 cm","Infant birth","Placental delivery"]
for i,label in enumerate(labels):
    x=35+i*240
    box(a,x,210,205,105,label, "#304964" if i<3 else "#5a4265")
    if i<3: arrow(a,x+205,262,x+240,262)
note(a,40,435,"Cervix: thinning ≠ opening. Stage 2 follows complete dilation; stage 3 follows infant birth.")
note(a,40,485,"Cesarean birth uses abdominal and uterine incisions; the placenta is also delivered.")
save("ch20-labor.svg",a)

a=svg_start("Three clocks: illustrative near-day-14 fertilization",1100,580)
for y,label,marks in [(140,"Cycle events",[(100,"day 1: bleeding"),(540,"near day 14: ovulation"),(980,"next onset: +28 d")]),
                      (290,"After fertilization",[(540,"0"),(750,"~7: implantation begins"),(980,"~14")]),
                      (440,"Gestational age from LMP",[(100,"0 weeks"),(540,"~2 weeks"),(980,"~4 weeks")])]:
    note(a,60,y-25,label)
    a.append(f'<path d="M100 {y} L990 {y}" stroke="#7da9c7" stroke-width="4"/>')
    for x,text in marks:
        a.append(f'<circle cx="{x}" cy="{y}" r="8" fill="#efc06e"/>')
        a.append(f'<text x="{x}" y="{y+33}" text-anchor="middle" fill="white" font-family="system-ui" font-size="17">{escape(text)}</text>')
save("ch20-clocks.svg",a)
def text2(a,x,y,value,size=18,color="#e5eef8",anchor="start"):
    a.append(f'<text x="{x}" y="{y}" fill="{color}" text-anchor="{anchor}" font-family="system-ui" font-size="{size}">{escape(value)}</text>')

a=svg_start("Term placenta: uterine attachment and separate blood circuits",1100,700)
note(a,40,92,"A. Uterine/placental section (schematic)")
note(a,610,92,"B. One villus (separate scale)")
a.append('<rect x="36" y="115" width="500" height="565" rx="12" fill="#172b41" stroke="#718da8"/>')
a.append('<rect x="56" y="150" width="460" height="105" fill="#233e61" stroke="#97b7d0"/>')
text2(a,72,185,"Amniotic space",17)
a.append('<path d="M260 160L260 265" stroke="#8ac8ed" stroke-width="25"/>')
text2(a,288,210,"umbilical cord: fetal vessels",16)
a.append('<rect x="56" y="255" width="460" height="42" fill="#314c72"/>')
text2(a,72,282,"chorionic plate: fetal vessel branches",16)
a.append('<rect x="56" y="297" width="460" height="206" fill="#6a3545"/>')
text2(a,72,323,"maternal intervillous blood",18)
a.append('<path d="M260 245L260 310" fill="none" stroke="#9dd8ee" stroke-width="18" stroke-linecap="round"/>')
a.append('<path d="M260 297L260 445 M260 345L190 405 M260 350L345 410 M260 385L310 455" fill="none" stroke="#9dd8ee" stroke-width="20" stroke-linecap="round"/>')
a.append('<path d="M260 297L260 445 M260 345L190 405 M260 350L345 410 M260 385L310 455" fill="none" stroke="#e4d4ef" stroke-width="31" stroke-linecap="round"/>')
a.append('<path d="M260 297L260 445 M260 345L190 405 M260 350L345 410 M260 385L310 455" fill="none" stroke="#9dd8ee" stroke-width="18" stroke-linecap="round"/>')
text2(a,350,465,"villous tree",16)
a.append('<rect x="56" y="503" width="460" height="45" fill="#7d5b64"/>')
text2(a,175,532,"decidua basalis: maternal endometrium",16)
a.append('<rect x="56" y="548" width="460" height="104" fill="#5d444d"/>')
text2(a,70,626,"myometrium",17)
a.append('<path d="M145 630L145 552L145 497" fill="none" stroke="#f5b0a7" stroke-width="10"/>')
a.append('<path d="M145 487L136 504L154 504Z" fill="#f5b0a7"/>')
text2(a,74,576,"spiral artery ↑",15)
a.append('<path d="M450 490L450 552L450 630" fill="none" stroke="#e9a49c" stroke-width="10"/>')
a.append('<path d="M450 640L441 623L459 623Z" fill="#e9a49c"/>')
text2(a,375,576,"uterine vein ↓",15)
a.append('<rect x="590" y="115" width="475" height="565" rx="12" fill="#6a3545" stroke="#718da8"/>')
text2(a,618,165,"Maternal intervillous blood (outside villus)",17)
a.append('<ellipse cx="859" cy="390" rx="155" ry="180" fill="#d6bfdc" stroke="#f2d9e5" stroke-width="4"/>')
text2(a,859,248,"trophoblast / villous boundary",16,"#1a2535","middle")
a.append('<ellipse cx="859" cy="400" rx="82" ry="112" fill="#255875" stroke="#9dd8ee" stroke-width="5"/>')
text2(a,859,387,"fetal capillary",18,"#ffffff","middle")
text2(a,859,414,"blood (inside)",17,"#ffffff","middle")
a.append('<path d="M615 458L800 455" stroke="#e3d7f3" stroke-width="3" marker-end="url(#arrow)"/>')
text2(a,610,480,"O₂ / nutrients →",15)
a.append('<path d="M815 480L615 545" stroke="#e3d7f3" stroke-width="3" marker-end="url(#arrow)"/>')
text2(a,610,575,"← CO₂ / wastes",15)
text2(a,620,640,"No whole-blood mixing or measured flux inferred",16)
text2(a,37,687,"Term topology only; first-week implantation differs. Panel B is not a continuous zoom of panel A.",15)
save("ch20-context.svg",a)
