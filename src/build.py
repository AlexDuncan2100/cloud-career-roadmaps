# Builds ../index.html from src/template.html and src/data.json (same UI as the e-commerce roadmaps).
# Usage: python3 src/build.py
import json, os, re
D = os.path.dirname(os.path.abspath(__file__))
ALL = json.load(open(os.path.join(D, 'data.json')))
ORDER = ['aws', 'awscert', 'devops', 'kube', 'k8s', 'azure', 'azdevops', 'devsecops', 'finops', 'cloudsec']
TABS = {'aws': 'AWS', 'awscert': 'AWS Certificates', 'devops': 'DevOps', 'kube': 'Kubernetes', 'k8s': 'Kubernetes Certification',
        'azure': 'Azure', 'azdevops': 'Azure DevOps', 'devsecops': 'DevSecOps', 'finops': 'FinOps', 'cloudsec': 'Cloud Security'}
PDF = {'aws': 'AWS Roadmap', 'awscert': 'AWS Certificate Roadmap', 'devops': 'DevOps Roadmap', 'kube': 'Kubernetes Roadmap',
       'k8s': 'Kubernetes Certification Roadmap', 'azure': 'Azure Roadmap', 'azdevops': 'Azure DevOps Roadmap',
       'devsecops': 'DevSecOps Roadmap', 'finops': 'FinOps Roadmap', 'cloudsec': 'Cloud Security Roadmap'}
# resource groups shown in the drawer (type keys must exist in UI.types)
XMAP = {'course': 'course', 'book': 'book', 'cheat': 'cheat', 'read': 'article', 'awesome': 'oss', 'lab': 'lab', 'workshop': 'lab',
        'project': 'lab', 'exam': 'exam', 'tool': 'tool', 'sec': 'official', 'community': 'community', 'news': 'community', 'jobs': 'jobs'}
GROUPS = [('docs', {'tr': 'Resmî dokümantasyon', 'en': 'Official documentation'}),
          ('learn', {'tr': 'Ücretsiz kurs, kitap ve cheat sheet', 'en': 'Free courses, books and cheat sheets'}),
          ('video', {'tr': 'Videolar', 'en': 'Videos'}),
          ('practice', {'tr': 'Pratik, lab ve sınav', 'en': 'Practice, labs and exams'}),
          ('read', {'tr': 'Okuma, araçlar ve GitHub', 'en': 'Reading, tools and GitHub'}),
          ('community', {'tr': 'Topluluk, haber ve iş ilanları', 'en': 'Community, news and jobs'})]
def bucket(t):
    return {'official': 'docs', 'course': 'learn', 'book': 'learn', 'cheat': 'learn', 'video': 'video', 'lab': 'practice',
            'exam': 'practice', 'practice': 'practice', 'article': 'read', 'oss': 'read', 'tool': 'read', 'community': 'community', 'jobs': 'community'}[t]
def step_groups(s):
    seen, items = set(), []
    def add(l, u, t):
        k = u.rstrip('/').lower()
        if k in seen: return
        seen.add(k); items.append([l, u, t])
    for r in s['docs']: add(r['l'], r['u'], 'official')
    for r in s['off']:
        gh = r['l'].startswith('GitHub')
        add(r['l'].replace('GitHub · ', 'GitHub: '), r['u'], 'oss' if gh else 'official')
    for r in s['vid']: add(r['l'] + ' (YouTube)', r['u'], 'video')
    for r in s['x']: add(r['l'], r['u'], XMAP[r['b']])
    for r in s['res']: add(r['l'], r['u'], 'practice')
    out = []
    for g, names in GROUPS:
        arr = [i for i in items if bucket(i[2]) == g]
        if arr: out.append({'h': names, 'items': arr})
    return out
def chan(r):
    seen, out = set(), []
    for s in r['steps']:
        for v in s['vid']:
            base = v['u'].split('/search')[0]
            if base not in seen: seen.add(base); out.append([v['l'], base, 'video'])
    return out[:16]
def auth(r):
    seen, out = set(), []
    for s in r['steps']:
        for v in s['x']:
            if v['b'] in ('read', 'book', 'course', 'awesome') and v['u'] not in seen:
                seen.add(v['u']); out.append([v['l'], v['u'], XMAP[v['b']]])
    return out[:24]
ROADMAPS = []
for k in ORDER:
    r = ALL[k]
    mods = []
    for s in r['steps']:
        desc = s['sessions'] or ''
        if s.get('project'): desc += (' · ' if desc else '') + 'Project: ' + s['project']
        mods.append({'title': {'tr': s['title'], 'en': s['title']}, 'phase': s['phase'], 'desc': {'tr': desc, 'en': desc},
                     'subs': {'tr': s['learn'], 'en': s['learn']}, 'groups': step_groups(s),
                     'files': [f['l'] for f in s['files']]})
    ROADMAPS.append({'id': k, 'title': {'tr': r['title'], 'en': r['title']}, 'tab': TABS[k], 'intro': {'tr': r['sub'], 'en': r['sub']},
                     'goal': r.get('cert', ''), 'pdf': 'pdf/' + PDF[k].replace(' ', '%20') + '.pdf', 'modules': mods,
                     'channels': {'tr': chan(r), 'en': chan(r)}, 'authorities': {'tr': auth(r), 'en': auth(r)}})
t = open(os.path.join(D, 'template.html')).read()
t = t.split('<style>', 1)[1]
t = '<style>' + t
t = t.replace('/*__DATA__*/', 'const ROADMAPS = ' + json.dumps(ROADMAPS, ensure_ascii=False).replace('</', '<\\/') + ';')
t = t.replace('/*__CHEAT__*/', 'const CHEAT = {};').replace('/*__SUBRES__*/', 'const SUBRES = {};').replace('/*__INIT__*/', '')
SITE = 'https://alexduncan2100.github.io/cloud-career-roadmaps/'
desc = 'roadmap.sh-style interactive learning roadmaps for AWS, AWS certifications, DevOps, Kubernetes, Kubernetes certification, Azure, Azure DevOps, DevSecOps, FinOps and Cloud Security, with verified free resources.'
head = f'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Cloud Career Roadmaps</title>
<meta name="description" content="{desc}">
<meta property="og:type" content="website">
<meta property="og:title" content="Cloud Career Roadmaps">
<meta property="og:description" content="{desc}">
<meta property="og:url" content="{SITE}">
<meta property="og:image" content="{SITE}assets/preview.png">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" href="data:image/svg+xml,<svg xmlns=%22http://www.w3.org/2000/svg%22 viewBox=%220 0 100 100%22><text y=%22.9em%22 font-size=%2290%22>☁️</text></svg>">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Balsamiq+Sans:wght@400;700&family=Inter:wght@400;500;600&display=swap">
</head>
<body>
'''
open(os.path.join(D, '..', 'index.html'), 'w').write(head + t + '\n</body>\n</html>\n')
print('index.html built', len(ROADMAPS), 'roadmaps', sum(len(r['modules']) for r in ROADMAPS), 'modules')
