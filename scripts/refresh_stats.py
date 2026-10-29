"""Render public GitHub metrics as local SVG cards, without third-party widgets."""
import datetime as dt
import html
import json
import os
from pathlib import Path
import subprocess
from collections import Counter

USER = os.environ.get('PROFILE_USER', 'smirthi-dharma')
OUT = Path(os.environ.get('STATS_OUT', 'dist'))
OUT.mkdir(parents=True, exist_ok=True)

def gh(*args):
    return json.loads(subprocess.check_output(['gh', *args], text=True, encoding='utf-8'))

query = '''query($login:String!) { user(login:$login) {
  contributionsCollection { contributionCalendar { totalContributions weeks { contributionDays { date contributionCount } } }
    totalCommitContributions totalPullRequestContributions totalIssueContributions totalPullRequestReviewContributions }
  repositories(first:100,privacy:PUBLIC,ownerAffiliations:OWNER) { nodes { name isFork stargazerCount languages(first:20,orderBy:{field:SIZE,direction:DESC}) { edges { size node { name color } } } } }
} }'''
result = gh('api', 'graphql', '-f', 'query='+query, '-f', 'login='+USER)
if result.get('errors'): raise RuntimeError(result['errors'])
user=result['data']['user']; c=user['contributionsCollection']
days=[d for w in c['contributionCalendar']['weeks'] for d in w['contributionDays']]
today=dt.datetime.now(dt.timezone.utc).date().isoformat()
days=[d for d in days if d['date']<=today]
longest=run=0
for d in days:
    run=run+1 if d['contributionCount'] else 0
    longest=max(longest,run)
recent=days[:-1] if days and days[-1]['date']==today and not days[-1]['contributionCount'] else days
current=0
for d in reversed(recent):
    if not d['contributionCount']: break
    current+=1
repos=user['repositories']['nodes']
languages=Counter();colors={}
for repo in repos:
    if repo['name']==USER: continue
    for edge in repo['languages']['edges']:
        lang=edge['node']['name'];languages[lang]+=edge['size'];colors[lang]=edge['node']['color'] or '#A78BFA'

def text(x,y,value,size=16,color='#94A3B8',anchor='start',weight='400'):
    return f'<text x="{x}" y="{y}" font-family="monospace" font-size="{size}" font-weight="{weight}" text-anchor="{anchor}" fill="{color}">{html.escape(str(value))}</text>'
def svg(w,h,body,bg,stroke):
    return f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect x="1" y="1" width="{w-2}" height="{h-2}" rx="14" fill="{bg}" stroke="{stroke}"/>{body}</svg>'

for mode,bg,ink,muted,cyan,border in [('dark','#0A101F','#F8FAFC','#94A3B8','#22D3EE','#233047'),('light','#F8FAFC','#0F172A','#475569','#0891B2','#CBD5E1')]:
    body=text(30,35,'ACTIVITY.LOG / LAST 12 MONTHS',15,cyan)
    for x,value,label in [(200,c['contributionCalendar']['totalContributions'],'Contributions'),(590,current,'Current streak · days'),(980,longest,'Longest streak · days')]:
        body+=text(x,102,value,40,ink,'middle','700')+text(x,137,label,15,muted,'middle')
    body+=text(590,177,'Public activity · trailing-year window · refreshed '+today+' UTC',12,muted,'middle')
    (OUT/f'streak-{mode}.svg').write_text(svg(1180,200,body,bg,border),encoding='utf-8')
    body=text(26,36,'GITHUB.STATS',18,cyan)
    values=[('Commit contributions',c['totalCommitContributions']),('Pull requests',c['totalPullRequestContributions']),('Code reviews',c['totalPullRequestReviewContributions']),('Issues',c['totalIssueContributions']),('Public repositories',len(repos))]
    for i,(label,value) in enumerate(values):
        body+=text(27,76+i*30,label,15,muted)+text(550,76+i*30,value,17,ink,'end','600')
    body+=text(27,252,'Contributions: last 12 months. Repositories: current.',11,muted)
    (OUT/f'stats-{mode}.svg').write_text(svg(580,280,body,bg,border),encoding='utf-8')
    body=text(26,36,'LANGUAGES / PUBLIC WORKSPACE',17,cyan)
    top=languages.most_common(6);total=sum(languages.values()) or 1;x=26
    for lang,size in top:
        width=528*size/total
        body+=f'<rect x="{x:.2f}" y="57" width="{width:.2f}" height="12" fill="{colors[lang]}"/>';x+=width
    for i,(lang,size) in enumerate(top):
        x=27+(i%2)*280;y=108+(i//2)*41
        body+=f'<circle cx="{x+5}" cy="{y-5}" r="5" fill="{colors[lang]}"/>'
        body+=text(x+19,y,f'{lang} {size/total:.1%}',14,muted)
    body+=text(27,239,'Code bytes across public repos, including forks.',11,muted)+text(27,257,'Profile assets excluded. This is not a skill rating.',11,muted)
    (OUT/f'languages-{mode}.svg').write_text(svg(580,280,body,bg,border),encoding='utf-8')
print(json.dumps({'contributions':c['contributionCalendar']['totalContributions'],'current_streak':current,'longest_in_window':longest,'public_repos':len(repos),'languages':dict(languages)}))
