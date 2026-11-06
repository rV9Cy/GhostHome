#!/usr/bin/env python3
"""Ghost House: ارواح و فرشته‌های تست‌های ریپوی تو.
python ghost-house.py                      -> http://localhost:8080 (لینک ریپو رو توی صفحه بزن)
python ghost-house.py --repo https://github.com/user/repo
python ghost-house.py --junit report.xml --dir ~/myproject   (خروجی pytest --junitxml)
GITHUB_TOKEN=xxx برای محدودیت بالاتر API گیت‌هاب (اختیاری)
"""
import argparse, json, os, re, subprocess, time, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

TOK = os.environ.get('GITHUB_TOKEN', '')
SEV = {'assert': 3, 'timeout': 3, 'null': 2, 'flaky': 1, 'issue': 2}
TXT = {'assert': 'خروجی اشتباه', 'timeout': 'تایم‌اوت', 'null': 'مقدار خالی', 'flaky': 'تست ناپایدار', 'issue': 'باگ باز'}
FIX = {'assert': 'خروجی واقعی رو با انتظار تست مقایسه کن و تغییرات کامیت مشکوک رو ببین',
       'timeout': 'تایم‌اوت و retry با backoff رو بررسی کن و کار سنگین رو بشکن',
       'null': 'قبل از استفاده از مقدار، چک None/null بذار',
       'flaky': 'وابستگی به زمان، ترتیب یا وضعیت مشترک رو پیدا کن و جداش کن',
       'issue': 'issue رو باز کن و تستی بنویس که همین باگ رو بشکنه'}


def api(p):
    h = {'User-Agent': 'ghost-house', 'Accept': 'application/vnd.github+json'}
    if TOK:
        h['Authorization'] = 'Bearer ' + TOK
    with urllib.request.urlopen(urllib.request.Request('https://api.github.com' + p, headers=h), timeout=20) as r:
        return json.load(r)


def kind(m):
    m = m.lower()
    if re.search(r'time ?out|timed out', m): return 'timeout'
    if re.search(r'nonetype|null|undefined|none', m): return 'null'
    if 'flaky' in m: return 'flaky'
    return 'assert'


def age(iso):
    t = datetime.fromisoformat(iso.replace('Z', '+00:00'))
    return max(0, (datetime.now(timezone.utc) - t).days)


def tree(files):
    skip = re.compile(r'(^|/)(node_modules|\.git|dist|build|__pycache__|venv)(/|$)')
    files = [f for f in files if not skip.search(f)]
    ds = {'/'.join(f.split('/')[:i]) for f in files for i in range(1, len(f.split('/')))}
    items = sorted([(f, 0) for f in files] + [(d, 1) for d in ds], key=lambda x: x[0] + ('/' if x[1] else ''))
    rows = []
    for p, isd in items[:220]:
        parts = p.split('/')
        rows.append([len(parts) - 1, parts[-1] + ('/' if isd else '')] + ([] if isd else [p]))
    return rows


def done(gs, ans, files, meta):
    S, F, fam = [], {}, {}
    for i, g in enumerate(gs + ans, 1):
        g['id'] = i
        if g['t'] != 'angel':
            key = (g['f'], g['t'])
            if key not in fam:
                fam[key] = 'F%d' % len(fam)
                F[fam[key]] = {'t': TXT[g['t']] + ' در ' + os.path.basename(g['f']), 'sev': SEV[g['t']], 'fx': FIX[g['t']]}
            g['fam'] = fam[key]
        S.append(g)
    if not S:
        raise Exception('نه تست شکسته‌ای پیدا شد نه کامیت فیکسی؛ ریپو خیلی سالمه')
    return {'S': S, 'F': F, 'T': tree(files), 'meta': meta}


def scan_gh(q):
    m = re.search(r'github\.com[/:]([\w.-]+)/([\w.-]+?)(?:\.git)?(?:[/#?]|$)', q)
    o, r = m.groups()
    base = '/repos/%s/%s' % (o, r)
    br = api(base)['default_branch']
    files = [e['path'] for e in api(base + '/git/trees/%s?recursive=1' % br)['tree'] if e['type'] == 'blob']
    gs, ans, ci = [], [], 'هنوز بیلدی (GitHub Actions) پیدا نشد.'
    runs = api(base + '/actions/runs?per_page=1&branch=' + br)['workflow_runs']
    if runs:
        run = runs[0]
        sha = run['head_sha']
        au = ((run.get('head_commit') or {}).get('author') or {}).get('name', '?')
        res = {'success': 'موفق', 'failure': 'شکست خورد'}.get(run['conclusion'], run['conclusion'] or 'در حال اجرا')
        ci = 'آخرین بیلد روی <code>%s</code>: %s؛ کامیت <code>%s</code>.' % (br, res, sha[:7])
        for c in api(base + '/commits/%s/check-runs' % sha)['check_runs']:
            if c['conclusion'] not in ('failure', 'timed_out'): continue
            anns = [a for a in api(base + '/check-runs/%d/annotations' % c['id']) if a['annotation_level'] == 'failure']
            for a in anns[:15]:
                msg = a['message']
                gs.append({'n': (a.get('title') or msg.split('\n')[0])[:60], 't': kind(msg), 'f': a['path'], 'l': a['start_line'],
                           'c': msg[:160], 'cm': sha[:7], 'au': au, 'd': age(run['created_at'])})
            if not anns:
                gs.append({'n': c['name'], 't': 'assert', 'f': '.github/workflows', 'l': 0, 'c': 'این مرحله‌ی CI شکست خورده؛ جزئیاتش توی لاگ Actions هست',
                           'cm': sha[:7], 'au': au, 'd': age(run['created_at'])})
    for i in api(base + '/issues?labels=bug&state=open&per_page=8'):
        if 'pull_request' in i: continue
        gs.append({'n': ('#%d %s' % (i['number'], i['title']))[:60], 't': 'issue', 'f': 'issues', 'l': i['number'],
                   'c': (i.get('body') or i['title'])[:160].replace('\n', ' '), 'cm': '#%d' % i['number'], 'au': i['user']['login'], 'd': age(i['created_at'])})
    for c in api(base + '/commits?per_page=60'):
        msg = c['commit']['message'].split('\n')[0]
        if len(ans) < 4 and re.search(r'\b(fix|fixes|fixed|bugfix|hotfix|resolve[sd]?)\b', msg, re.I):
            fl = api(base + '/commits/' + c['sha']).get('files') or [{'filename': '?'}]
            ans.append({'n': msg[:60], 't': 'angel', 'f': fl[0]['filename'], 'l': 1, 'c': msg, 'cm': c['sha'][:7],
                        'au': c['commit']['author']['name'], 'd': age(c['commit']['author']['date'])})
    nt = len([f for f in files if re.search(r'test|spec', f, re.I)])
    return done(gs, ans, files, {'name': '%s/%s' % (o, r), 'url': 'https://github.com/%s/%s' % (o, r), 'ci': ci, 'total': nt, 't2': ['فایل تست', str(nt)]})


def git(d, *a):
    try:
        return subprocess.run(['git', '-C', d] + list(a), capture_output=True, text=True, timeout=15).stdout.strip()
    except Exception:
        return ''


def scan_junit(path, d):
    d = os.path.expanduser(d)
    gs, ans, tot = [], [], 0
    for tc in ET.parse(os.path.expanduser(path)).getroot().iter('testcase'):
        tot += 1
        bad = tc.find('failure') if tc.find('failure') is not None else tc.find('error')
        fk = tc.find('flakyFailure') if tc.find('flakyFailure') is not None else tc.find('rerunFailure')
        node = bad if bad is not None else fk
        if node is None: continue
        txt = (node.get('message') or '') + '\n' + (node.text or '')
        loc = re.findall(r'([\w./-]+\.(?:py|js|ts|jsx|tsx|go|rs|java)):(\d+)', txt)
        src = [x for x in loc if 'test' not in x[0].lower()] or loc or [(tc.get('file') or tc.get('classname', '?'), '0')]
        f, l = src[-1]
        cm, au, ct = (git(d, 'log', '-1', '--format=%h|%an|%ct', '--', f) + '||').split('|')[:3]
        gs.append({'n': tc.get('name', '?')[:60], 't': 'flaky' if bad is None else kind(txt), 'f': f, 'l': int(l),
                   'c': (node.get('message') or txt)[:160].replace('\n', ' '), 'cm': cm or '-', 'au': au or '-',
                   'd': int((time.time() - int(ct)) / 86400) if ct.isdigit() else 0})
    cur = None
    for ln in git(d, 'log', '-12', '-i', '--grep=fix', '--format=@%h|%an|%ct|%s', '--name-only').splitlines():
        if ln.startswith('@'):
            if len(ans) >= 4: break
            h, a, ct, s = ln[1:].split('|', 3)
            cur = {'n': s[:60], 't': 'angel', 'f': '?', 'l': 1, 'c': s, 'cm': h, 'au': a, 'd': int((time.time() - int(ct)) / 86400)}
            ans.append(cur)
        elif ln and cur and cur['f'] == '?':
            cur['f'] = ln
    files = git(d, 'ls-files').splitlines()
    return done(gs, ans, files, {'name': os.path.basename(os.path.abspath(d)), 'url': '', 'total': tot,
                                 'ci': 'گزارش تست: %d تست اجرا شد و %d مشکل داره.' % (tot, len(gs))})



import sqlite3, sys
DB = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'ghosts.db')


def db():
    os.makedirs(os.path.dirname(DB), exist_ok=True)
    c = sqlite3.connect(DB)
    c.executescript('create table if not exists settings(k text primary key, v text);'
                    'create table if not exists scans(id integer primary key autoincrement, repo text, ts integer,'
                    ' ghosts integer, angels integer, health integer, data text);')
    return c


def out(o):
    print(json.dumps(o, ensure_ascii=False))


if __name__ == '__main__':
    a = sys.argv[1:]
    cmd = a[0] if a else ''
    try:
        r = db().execute("select v from settings where k='token'").fetchone()
        TOK = os.environ.get('GITHUB_TOKEN') or (r[0] if r else '')
        if cmd == 'scan':
            q = a[1] if len(a) > 1 else ''
            if not q:
                raise Exception('لینک ریپوی گیت‌هاب رو بالا وارد کن و اسکن رو بزن')
            d = scan_gh(q) if 'github.com' in q else scan_junit(q, a[2] if len(a) > 2 and a[2] else '.')
            gs = [s for s in d['S'] if s['t'] != 'angel']
            health = max(0, 100 - 2 * sum(d['F'][s['fam']]['sev'] for s in gs))
            c = db()
            c.execute('insert into scans(repo,ts,ghosts,angels,health,data) values(?,?,?,?,?,?)',
                      (d['meta']['name'], int(time.time()), len(gs), len(d['S']) - len(gs), health, json.dumps(d, ensure_ascii=False)))
            c.commit()
            out(d)
        elif cmd == 'repos':
            if not TOK:
                raise Exception('اول توکن گیت‌هاب رو ذخیره کن')
            out([{'name': x['full_name'], 'url': x['html_url'], 'pushed': (x['pushed_at'] or '')[:10]}
                 for x in api('/user/repos?per_page=30&sort=pushed')])
        elif cmd == 'settoken':
            c = db()
            c.execute("insert or replace into settings values('token',?)", (sys.stdin.read().strip(),))
            c.commit()
            out({'ok': True})
        elif cmd == 'gettoken':
            print(TOK)
        elif cmd == 'history':
            out([dict(zip(('repo', 'ts', 'ghosts', 'angels', 'health'), x)) for x in
                 db().execute('select repo,ts,ghosts,angels,health from scans order by id desc limit 10')])
        else:
            out({'error': 'دستور ناشناخته: scan | repos | settoken | history'})
    except Exception as e:
        out({'error': str(e)[:200]})
