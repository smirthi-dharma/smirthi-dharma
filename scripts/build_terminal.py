"""Compose native SVG terminal chrome and particle animation around a generated portrait."""
from pathlib import Path
import base64, html, math, random, shutil
import numpy as np
from scipy.optimize import linear_sum_assignment

ROOT=Path(__file__).resolve().parents[1]
BASE=ROOT.parent
(ROOT/'scripts').mkdir(exist_ok=True)
(ROOT/'assets').mkdir(exist_ok=True)
PHOTO=ROOT/'assets/portrait.png'
portrait_svg=(ROOT/'assets/portrait-paths.svg').read_text(encoding='utf-8')
portrait=portrait_svg[portrait_svg.index('<g '):portrait_svg.rindex('</svg>')].replace('translate(55 131) scale(1.1467 1.1406)', 'translate(75 115) scale(1 .90)')
toolbox_svg=(ROOT/'assets/toolbox-fragment.svg').read_text(encoding='utf-8')
toolbox=toolbox_svg[toolbox_svg.index('<g '):toolbox_svg.rindex('</svg>')]
rng=np.random.default_rng(21)
N=720

def line(a,b,count): return np.linspace(a,b,count)
# Three developer motifs: code brackets, React's atom geometry, and an agent network.
code=np.concatenate([line((105,125),(48,185),120),line((48,185),(105,245),120),line((195,125),(252,185),120),line((252,185),(195,245),120),line((173,110),(127,260),240)])
t=np.linspace(0,2*np.pi,240)
atom=[]
for angle in (0,np.pi/3,2*np.pi/3):
    p=np.column_stack((112*np.cos(t),43*np.sin(t)))
    R=np.array([[np.cos(angle),-np.sin(angle)],[np.sin(angle),np.cos(angle)]])
    atom.append(p@R+np.array([150,185]))
atom=np.concatenate(atom)
vertices=np.array([[70,105],[230,105],[150,185],[70,265],[230,265]])
edges=[(0,2),(1,2),(2,3),(2,4),(0,1),(3,4)]
network=np.concatenate([line(vertices[a],vertices[b],120) for a,b in edges])
shapes=[code,atom,network]
shapes=[s+rng.normal(0,1.3,s.shape) for s in shapes]
for i in range(1,3):
    costs=((shapes[i-1][:,None,:]-shapes[i][None,:,:])**2).sum(axis=2)
    _,order=linear_sum_assignment(costs);shapes[i]=shapes[i][order]
np.savez_compressed(ROOT/'scripts/particle-paths.npz',code=shapes[0],atom=shapes[1],network=shapes[2])

def txt(x,y,s,size=14,color='#94A3B8',extra=''):
    return f'<text x="{x}" y="{y}" font-family="ui-monospace,SFMono-Regular,Consolas,monospace" font-size="{size}" fill="{color}" {extra}>{html.escape(s)}</text>'
for mode,bg,panel,ink,muted,cyan,purple,border in [('dark','#0A101F','#0D1528','#F8FAFC','#94A3B8','#22D3EE','#A78BFA','#233047'),('light','#F8FAFC','#EFF4FA','#0F172A','#475569','#0891B2','#7C3AED','#CBD5E1')]:
    p=[f'<svg xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink" width="1180" height="610" viewBox="0 0 1180 610" role="img" aria-labelledby="title desc"><title id="title">Smirthika Dharmalingam — live developer terminal</title><desc id="desc">AI Developer and Full-Stack Builder. An animated dotted portrait transitions into code, React and agent-network motifs. Python, TypeScript, React, Next.js, Django, FastAPI, MySQL and Supabase.</desc>']
    p.append('''<style>@keyframes pulse{50%{opacity:.35}}.live{animation:pulse 1.8s ease-in-out infinite}@keyframes reveal{from{opacity:0}to{opacity:1}}.intro{animation:reveal 2s ease-out both}.still{display:none}@media(prefers-reduced-motion:reduce){.live,.intro{animation:none}.motion{display:none}.still{display:inline}}</style>''')
    p.append(f'<defs>{portrait}<clipPath id="portraitClip"><rect x="45" y="116" width="365" height="402" rx="8"/></clipPath></defs>')
    p.append(f'<rect x="1" y="1" width="1178" height="608" rx="18" fill="{bg}" stroke="{border}" stroke-width="2"/><path d="M1 51H1179" stroke="{border}"/>')
    for x,color in [(25,'#F87171'),(47,'#FBBF24'),(69,'#10B981')]:p.append(f'<circle cx="{x}" cy="26" r="6" fill="{color}"/>')
    p.append(txt(99,31,'profile.sh --live',14,muted)+txt(1029,31,'UTF-8 / SSH',12,muted))
    p.append(txt(31,88,'01 / VISUAL.MAP',13,cyan)+txt(470,88,'02 / SYSTEM.INFO',13,cyan))
    p.append(f'<rect x="1048" y="68" width="100" height="27" rx="13" fill="{panel}" stroke="{border}"/><circle class="live" cx="1065" cy="81" r="4" fill="#F87171"/>'+txt(1080,85,'LIVE',12,ink))
    p.append(f'<rect x="30" y="104" width="395" height="430" rx="10" fill="{panel}" stroke="{border}"/>')
    # One embedded portrait, referenced by both the intro and repeated dissolve layers.
    p.append('<g clip-path="url(#portraitClip)"><g class="motion"><use xlink:href="#portrait"/><animate attributeName="opacity" values="1;1;0;0;1" keyTimes="0;.2113;.3028;.9085;1" begin="3.2s" dur="14.2s" repeatCount="indefinite"/><animateTransform attributeName="transform" type="translate" values="0 0;0 0;35 0;35 0;0 0" keyTimes="0;.2113;.3028;.9085;1" begin="3.2s" dur="14.2s" repeatCount="indefinite"/></g><g class="still"><use xlink:href="#portrait"/></g></g>')
    p.append(f'<g class="motion" transform="translate(107 100) scale(.8)" fill="{purple}" opacity="0"><animate attributeName="opacity" values="0;0;1;1;1;1;1;1;0" keyTimes="0;.2113;.3028;.4437;.5352;.6761;.7676;.9085;1" begin="3.2s" dur="14.2s" repeatCount="indefinite"/>')
    for i in range(N):
        a,b,c=[s[i] for s in shapes]
        xs=[a[0],a[0],a[0],a[0],b[0],b[0],c[0],c[0],a[0]];ys=[a[1],a[1],a[1],a[1],b[1],b[1],c[1],c[1],a[1]]
        p.append(f'<circle r="1.55" cx="{a[0]:.1f}" cy="{a[1]:.1f}"><animate attributeName="cx" values="'+ ';'.join(f'{v:.1f}' for v in xs)+'" keyTimes="0;.2113;.3028;.4437;.5352;.6761;.7676;.9085;1" begin="3.2s" dur="14.2s" repeatCount="indefinite"/><animate attributeName="cy" values="'+';'.join(f'{v:.1f}' for v in ys)+'" keyTimes="0;.2113;.3028;.4437;.5352;.6761;.7676;.9085;1" begin="3.2s" dur="14.2s" repeatCount="indefinite"/></circle>')
    p.append('</g>'+toolbox)
    rows=[('Subject','Smirthika Dharmalingam'),('Role','AI Developer / Full-Stack Builder'),('Status','Building + Learning + Shipping'),('Focus','AI agents + consent-first apps'),('ToolChain','Git / GitHub'),('', ''),('Core.Lang','Python / TypeScript / JavaScript'),('Core.Frontend','React / Next.js / Tailwind'),('Core.Backend','Django / FastAPI'),('Core.Database','MySQL / Supabase'),('Core.Infra','GitHub Actions / Vercel'),('', ''),('Grid.LinkedIn','in/smirthika-dharmalingam'),('Grid.GitHub','github.com/smirthi-dharma'),('Workspace','Open source + web applications')]
    for i,(label,value) in enumerate(rows):
        if not label: continue
        y=128+i*24
        leaders='.'*max(2,63-len(label)-len(value))
        row=label+' '+leaders+' '+value
        p.append(txt(470,y,row,14,muted,'textLength="670" lengthAdjust="spacingAndGlyphs"'))
    p.append(f'<rect x="470" y="506" width="250" height="32" rx="16" fill="{purple}" fill-opacity=".13" stroke="{purple}" stroke-opacity=".4"/>'+txt(491,527,'@smirthi-dharma',14,purple))
    p.append(f'<path d="M30 555H1150" stroke="{border}"/>'+txt(31,584,'❯',17,'#10B981')+txt(55,583,'ready to build something meaningful_',13,cyan)+txt(969,583,'SYSTEM / ONLINE',12,'#10B981')+'</svg>')
    (ROOT/f'{mode}.svg').write_text(''.join(p),encoding='utf-8')

(ROOT/'assets/linkedin.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" width="155" height="36" viewBox="0 0 155 36"><rect width="155" height="36" rx="4" fill="#0A66C2"/><text x="15" y="25" font-family="Arial" font-size="24" font-weight="700" fill="white">in</text><text x="50" y="23" font-family="Arial" font-size="13" letter-spacing="1" fill="white">LINKEDIN</text></svg>',encoding='utf-8')
readme='''<!-- Terminal profile inspired by the GitHub Portfolio guide shared by Automation With Clarity.
     Generated assets live in this repository; GitHub Actions refreshes public metrics. -->
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="dark.svg" />
  <img src="light.svg" width="100%" alt="Smirthika Dharmalingam — animated developer terminal: AI Developer, Full-Stack Builder and Open Source Contributor" />
</picture>

<br />

<div align="center">
'''
for name,width,alt in [('streak','100%','Public contribution activity and current and longest streaks in the last 12 months'),('stats','49%','GitHub contribution statistics'),('languages','49%','Language distribution by code bytes in public repositories, including forks')]:
    readme+=f'''<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/smirthi-dharma/smirthi-dharma/output/{name}-dark.svg" />
  <img width="{width}" src="https://raw.githubusercontent.com/smirthi-dharma/smirthi-dharma/output/{name}-light.svg" alt="{alt}" />
</picture>
'''
    if name=='streak': readme+='<br /><br />\n'
readme+='''</div>

<br />

<div align="center">
<picture>
  <source media="(prefers-color-scheme: dark)" srcset="https://raw.githubusercontent.com/smirthi-dharma/smirthi-dharma/output/github-snake-dark.svg" />
  <img width="100%" src="https://raw.githubusercontent.com/smirthi-dharma/smirthi-dharma/output/github-snake.svg" alt="Animated snake eating my GitHub contributions" />
</picture>
</div>

<br />

<div align="center">
  <a href="https://www.linkedin.com/in/smirthika-dharmalingam"><img src="assets/linkedin.svg" alt="Connect on LinkedIn" /></a>
</div>

<details>
<summary>Explore my projects &amp; how these stats work</summary>

- [Hushh Research](https://github.com/smirthi-dharma/hushh-research) — personal AI agents and consent-driven experiences.
- [Hushh Tech Website](https://github.com/smirthi-dharma/hushh_Tech_website) — public web experiences and API integrations.
- [Super Market](https://github.com/smirthi-dharma/e-commerce-) — React storefront and Django API.

These repositories are public forks in my workspace. Activity cards use GitHub's public contribution data for the trailing year and refresh every 12 hours. The current streak allows today to remain in progress; the longest streak is limited to the displayed year. Language percentages represent code volume across public repositories, including forks, with this profile repository excluded. They are not a skill rating.

</details>
'''
(ROOT/'README.md').write_text(readme,encoding='utf-8')
workflow=(ROOT/'.github/workflows/contribution-snake.yml').read_text(encoding='utf-8')
workflow=workflow.replace('Refresh contribution snake','Refresh profile activity').replace("'23 3 * * *'","'23 */12 * * *'")
workflow=workflow.replace("paths: ['.github/workflows/contribution-snake.yml']","paths: ['.github/workflows/contribution-snake.yml', 'scripts/refresh_stats.py']")
workflow=workflow.replace('color_snake=#ba6b9c&color_dots=#f4e7f2,#F8BBD0,#EF93C4,#d477b0,#a95795','color_snake=#0891B2&color_dots=#ebedf0,#a5b4fc,#818cf8,#6366f1,#0891B2')
workflow=workflow.replace('color_snake=#F8BBD0&color_dots=#261d32,#58334f,#99517e,#cf7caf,#EF93C4','color_snake=#10B981&color_dots=#2d3343,#4b5563,#7C3AED,#A78BFA,#22D3EE')
(ROOT/'.github/workflows/contribution-snake.yml').write_text(workflow,encoding='utf-8')
import xml.etree.ElementTree as ET
for f in [ROOT/'dark.svg',ROOT/'light.svg',*list((ROOT/'assets').glob('*.svg'))]: ET.parse(f)
print('Generated terminal banners, verified XML, README, themed snake workflow and stats generator.')
print({f.name:f.stat().st_size for f in [ROOT/'dark.svg',ROOT/'light.svg']})
