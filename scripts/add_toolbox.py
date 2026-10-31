"""Vendor Skill Icons and build a compact, native-SVG toolbox panel."""
from pathlib import Path
import concurrent.futures
import re
import urllib.request
import xml.etree.ElementTree as ET

raise SystemExit("Toolbox now lives separately in README.md; edit that section directly.")
ROOT=Path(__file__).resolve().parents[1]
ICONS=ROOT/'assets/tool-icons'
ICONS.mkdir(exist_ok=True)
names=['Python-Dark','JavaScript','TypeScript','React-Dark','NextJS-Dark','TailwindCSS-Dark','Django','FastAPI','MySQL-Dark','Supabase-Dark','Git','Github-Dark','HTML','CSS','GithubActions-Dark','Vercel-Dark']
base='https://raw.githubusercontent.com/tandpfun/skill-icons/main/'
def fetch(name):
    path=ICONS/(name+'.svg')
    if not path.exists(): path.write_bytes(urllib.request.urlopen(base+'icons/'+name+'.svg',timeout=30).read())
    ET.parse(path)
with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool: list(pool.map(fetch,names))
(ICONS/'LICENSE').write_bytes(urllib.request.urlopen(base+'LICENSE',timeout=30).read())
(ICONS/'README.md').write_text('Icons from [Skill Icons](https://github.com/tandpfun/skill-icons), under the included MIT license. Original SVG artwork is preserved.\n',encoding='utf-8')
parts=['<g id="toolbox"><text x="53" y="441" fill="#22B8CF" font-family="monospace" font-size="13">~/ toolbox</text>']
for i,name in enumerate(names):
    source=(ICONS/(name+'.svg')).read_text(encoding='utf-8')
    # Scope gradient, mask and clipping IDs so all sixteen assets coexist.
    ids=re.findall(r'\bid="([^"]+)"',source)
    for ident in ids:
        source=source.replace(f'id="{ident}"',f'id="tool{i}-{ident}"').replace(f'url(#{ident})',f'url(#tool{i}-{ident})').replace(f'href="#{ident}"',f'href="#tool{i}-{ident}"')
    inner=re.search(r'<svg\b[^>]*>(.*)</svg>',source,re.S).group(1)
    view=re.search(r'viewBox="([^"]+)"',source).group(1)
    x=53+(i%8)*44;y=454+(i//8)*42
    parts.append(f'<svg x="{x}" y="{y}" width="33" height="33" viewBox="{view}"><title>{name.replace("-Dark", "")}</title>{inner}</svg>')
parts.append('</g>')
toolbox=''.join(parts)
(ROOT/'assets/toolbox-fragment.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg">'+toolbox+'</svg>',encoding='utf-8')
for mode in ('dark','light'):
    p=ROOT/f'{mode}.svg';s=p.read_text(encoding='utf-8')
    s=s.replace('translate(55 131) scale(1.1467 1.1406)','translate(75 115) scale(1 .90)')
    s=s.replace('transform="translate(77 122)"','transform="translate(107 100) scale(.8)"')
    s=re.sub(r'<text[^>]*>PORTRAIT / CODE / REACT / AGENTS</text>',lambda _:toolbox,s)
    ET.fromstring(s);p.write_text(s,encoding='utf-8')
generator=ROOT/'scripts/build_terminal.py'
s=generator.read_text(encoding='utf-8')
s=s.replace("portrait=portrait_svg[portrait_svg.index('<g '):portrait_svg.rindex('</svg>')]", "portrait=portrait_svg[portrait_svg.index('<g '):portrait_svg.rindex('</svg>')].replace('translate(55 131) scale(1.1467 1.1406)', 'translate(75 115) scale(1 .90)')\ntoolbox_svg=(ROOT/'assets/toolbox-fragment.svg').read_text(encoding='utf-8')\ntoolbox=toolbox_svg[toolbox_svg.index('<g '):toolbox_svg.rindex('</svg>')]")
s=s.replace('transform="translate(77 122)"','transform="translate(107 100) scale(.8)"')
s=s.replace("txt(53,520,'PORTRAIT / CODE / REACT / AGENTS',10,muted)",'toolbox')
generator.write_text(s,encoding='utf-8')
p=ROOT/'README.md';s=p.read_text(encoding='utf-8').replace('terminal4','toolbox1');p.write_text(s,encoding='utf-8')
print('Added 16 licensed technology icons, validated both banners, and updated the source generator.')
