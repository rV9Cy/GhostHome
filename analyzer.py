#!/usr/bin/env python3
"""Ghost House: ارواح و فرشته‌های تست‌های ریپوی تو.
python ghost-house.py                      -> http://localhost:8080 (لینک ریپو رو توی صفحه بزن)
python ghost-house.py --repo https://github.com/user/repo
python ghost-house.py --junit report.xml --dir ~/myproject   (خروجی pytest --junitxml)
GITHUB_TOKEN=xxx برای محدودیت بالاتر API گیت‌هاب (اختیاری)
"""
import argparse, json, os, re, shutil, subprocess, time, urllib.parse, urllib.request
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


def done(gs, ans, files, meta, sleep=None):
    S, F, fam = [], {}, {}
    for i, g in enumerate(gs + ans, 1):
        g['id'] = i
        g.setdefault('n', g.get('ttl', ''))
        if g['t'] != 'angel':
            key = (g['f'], g.get('rule') or g['t'])
            if key not in fam:
                fam[key] = 'F%d' % len(fam)
                F[fam[key]] = {'t': (g.get('ttl') or TXT[g['t']]) + ' در ' + (os.path.basename(g['f'].rstrip('/')) or g['f']),
                               'sev': g.get('sev') or SEV[g['t']], 'fx': g.get('fx') or FIX[g['t']]}
            g['fam'] = fam[key]
        S.append(g)
    sl = [{'id': 1000 + k, 't': 'sleep', 'f': x['f'], 'n': os.path.basename(x['f']), 'loc': x['loc']} for k, x in enumerate(sleep or [])]
    return {'S': S, 'F': F, 'T': tree(files), 'meta': meta, 'sleep': sl}



import io, zipfile, urllib.error
from inspector import inspect_repo


class _NoRedir(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


def run_logs(base, run_id):
    """لاگ کامل آخرین بیلد (نیاز به توکن دارد)."""
    h = {'User-Agent': 'ghost-house', 'Authorization': 'Bearer ' + TOK}
    try:
        urllib.request.build_opener(_NoRedir).open(urllib.request.Request('https://api.github.com%s/actions/runs/%d/logs' % (base, run_id), headers=h), timeout=20)
        return ''
    except urllib.error.HTTPError as e:
        if e.code != 302: raise
        loc = e.headers['Location']
    z = zipfile.ZipFile(io.BytesIO(urllib.request.urlopen(loc, timeout=60).read()))
    return '\n'.join(z.read(n).decode('utf-8', 'replace') for n in z.namelist() if n.endswith('.txt'))[:6000000]


def log_ghosts(txt, sha, au, d):
    """تست‌های شکسته‌ی pytest، Jest و Go رو از متن لاگ درمیاره."""
    out, seen = [], set()
    txt = re.sub(r'\x1b\[[0-9;]*m', '', txt)

    def add(n, f, msg, l=0):
        if n in seen or len(out) >= 20: return
        seen.add(n)
        out.append({'n': n[:60], 't': kind(msg), 'f': f, 'l': l, 'c': (msg or 'failed')[:160], 'cm': sha[:7], 'au': au, 'd': d})
    for m in re.finditer(r'FAILED\s+(\S+?)::(\S+?)(?:\s+-\s+(.*))?$', txt, re.M):
        ln = re.search(re.escape(m[1]) + r':(\d+)', txt)
        add(m[2], m[1], (m[3] or '').strip(), int(ln[1]) if ln else 0)
    lines, fl = txt.split('\n'), ''
    for i, ln in enumerate(lines):
        m = re.search(r'\bFAIL\s+(\S+\.(?:js|ts|jsx|tsx))', ln)
        if m: fl = m[1]
        m = re.search(r'●\s+(.+?)\s*$', ln)
        if m and '›' in m[1]:
            msg = next((x.split('Z ', 1)[-1].strip() for x in lines[i + 1:i + 14] if re.search(r'expect|Error|Received|Expected', x)), '')
            add(m[1], fl or 'tests', msg)
        m = re.search(r'--- FAIL:\s+(\S+)', ln)
        if m: add(m[1], 'go test', ln.split('Z ', 1)[-1])
    return out


ROOT = os.path.dirname(os.path.abspath(__file__))


def ensure_clone(o, r):
    d = os.path.join(ROOT, 'cache', '%s__%s' % (o, r))
    pub = 'https://github.com/%s/%s.git' % (o, r)
    if os.path.isdir(d):
        healthy = subprocess.run(['git', '-C', d, 'rev-parse', '--verify', '-q', 'HEAD'], capture_output=True).returncode == 0
        if healthy:
            auth = ['-c', 'http.extraHeader=Authorization: Bearer ' + TOK] if TOK else []
            subprocess.run(['git', '-C', d] + auth + ['fetch', '--depth', '100', '-q', 'origin'], capture_output=True, timeout=300)
            git(d, 'reset', '-q', '--hard', 'origin/HEAD')
            return d
        shutil.rmtree(d, ignore_errors=True)  # کلون ناقص از دفعه‌ی قبل
    os.makedirs(os.path.dirname(d), exist_ok=True)
    tmp = d + '.tmp'
    shutil.rmtree(tmp, ignore_errors=True)
    url = 'https://x-access-token:%s@github.com/%s/%s.git' % (TOK, o, r) if TOK else pub
    p = subprocess.run(['git', 'clone', '--depth', '100', '-q', url, tmp], capture_output=True, text=True, timeout=900)
    if p.returncode:
        shutil.rmtree(tmp, ignore_errors=True)
        raise Exception('clone نشد؛ اگه ریپو خصوصیه توکن رو ذخیره کن. ' + p.stderr.strip()[-120:])
    git(tmp, 'remote', 'set-url', 'origin', pub)
    os.rename(tmp, d)
    return d


def run_tests(d, sha, au):
    """اجرای واقعی تست‌ها روی همین دستگاه (فقط وقتی کاربر بخواد)."""
    out, notes = [], []

    def sh(cmd):
        try:
            r = subprocess.run(cmd, cwd=d, capture_output=True, text=True, timeout=180)
            return r.stdout + '\n' + r.stderr
        except FileNotFoundError:
            return 'NOTFOUND'
        except subprocess.TimeoutExpired:
            return 'TIMEOUT'
    has = lambda *p: any(os.path.exists(os.path.join(d, x)) for x in p)
    if has('pytest.ini', 'tox.ini', 'setup.cfg', 'pyproject.toml', 'tests', 'test'):
        txt = sh([sys.executable, '-m', 'pytest', '-q', '-rf', '--tb=line', '-p', 'no:cacheprovider'])
        if 'No module named pytest' in txt: notes.append('pytest نصب نیست (pip install pytest)')
        elif 'TIMEOUT' == txt: notes.append('اجرای pytest بیشتر از ۳ دقیقه طول کشید')
        else: out += log_ghosts(txt, sha, au, 0)
    if has('package.json') and has('node_modules'):
        pj = json.load(open(os.path.join(d, 'package.json'), encoding='utf-8'))
        if (pj.get('scripts') or {}).get('test'):
            out += log_ghosts(sh(['npm', 'test', '--silent']), sha, au, 0)
    elif has('package.json'):
        notes.append('node_modules نیست؛ اول npm install بزن تا تست‌ها اجرا بشن')
    if has('go.mod'):
        out += log_ghosts(sh(['go', 'test', './...']), sha, au, 0)
    for g in out: g['src'] = 'test'
    return out, ' · '.join(notes)


def scan_gh(q, tests=False):
    m = re.search(r'github\.com[/:]([\w.-]+)/([\w.-]+?)(?:\.git)?(?:[/#?]|$)', q)
    o, r = m.groups()
    base = '/repos/%s/%s' % (o, r)
    d = ensure_clone(o, r)
    files = git(d, 'ls-files').splitlines()
    if not files:  # راه‌حل جایگزین: خوندن مستقیم از دیسک
        files = [os.path.relpath(os.path.join(rt, f), d).replace(os.sep, '/') for rt, ds, fs in os.walk(d) if '.git' not in rt.split(os.sep) for f in fs]
    if not files:
        shutil.rmtree(d, ignore_errors=True)
        raise Exception('ریپو خالیه یا clone ناقص بود؛ یه بار دیگه اسکن بزن')
    gs, scanned, healthy = inspect_repo(d, files)
    head = (git(d, 'log', '-1', '--format=%h|%an') + '|').split('|')
    sha, au = head[0], head[1]
    notes, ci = [], 'CI پیدا نشد (یا بدون توکن قابل‌خوندن نیست).'
    try:
        runs = api(base + '/actions/runs?per_page=1')['workflow_runs']
        if runs:
            run = runs[0]
            sha, au = run['head_sha'][:7], ((run.get('head_commit') or {}).get('author') or {}).get('name', au)
            res = {'success': 'موفق', 'failure': 'شکست خورد'}.get(run['conclusion'], run['conclusion'] or 'در حال اجرا')
            ci = 'آخرین بیلد CI: %s؛ کامیت <code>%s</code>.' % (res, sha)
            ci_g = []
            for c in api(base + '/commits/%s/check-runs' % run['head_sha'])['check_runs']:
                if c['conclusion'] not in ('failure', 'timed_out'): continue
                anns = [x for x in api(base + '/check-runs/%d/annotations' % c['id']) if x['annotation_level'] == 'failure']
                for x in anns[:15]:
                    msg = x['message']
                    ci_g.append({'n': (x.get('title') or msg.split('\n')[0])[:60], 't': kind(msg), 'f': x['path'], 'l': x['start_line'], 'c': msg[:160],
                                 'cm': sha, 'au': au, 'd': age(run['created_at']), 'src': 'ci'})
                if not anns:
                    ci_g.append({'n': c['name'], 't': 'assert', 'f': '.github/workflows', 'l': 0, 'c': 'این مرحله‌ی CI شکست خورده؛ جزئیات توی لاگ Actions',
                                 'cm': sha, 'au': au, 'd': age(run['created_at']), 'src': 'ci'})
            if TOK and run['conclusion'] == 'failure':
                try:
                    have = {x['n'] for x in ci_g}
                    ci_g += [x for x in log_ghosts(run_logs(base, run['id']), sha, au, age(run['created_at'])) if x['n'] not in have]
                except Exception:
                    pass
            gs += ci_g
    except Exception:
        pass
    try:
        for i in api(base + '/issues?labels=bug&state=open&per_page=8'):
            if 'pull_request' in i: continue
            gs.append({'n': ('#%d %s' % (i['number'], i['title']))[:60], 't': 'issue', 'f': 'issues', 'l': i['number'],
                       'c': (i.get('body') or i['title'])[:160].replace('\n', ' '), 'cm': '#%d' % i['number'], 'au': i['user']['login'], 'd': age(i['created_at'])})
    except Exception:
        pass
    if tests:
        ts, note = run_tests(d, sha, au)
        gs += ts
        if note: notes.append(note)
    gs.sort(key=lambda g: (-(g.get('sev') or SEV[g['t']]), g['f'], g['l']))
    ans, cur = [], None
    for ln in git(d, 'log', '-80', '-i', '-E', '--grep=(^|[^a-z])(fix|fixes|fixed|bugfix|hotfix)([^a-z]|$)', '--format=@%h|%an|%ct|%s', '--name-only').splitlines():
        if ln.startswith('@'):
            if len(ans) >= 4: break
            h, a_, ct, s_ = ln[1:].split('|', 3)
            cur = {'n': s_[:60], 't': 'angel', 'f': '?', 'l': 1, 'c': s_, 'cm': h, 'au': a_, 'd': int((time.time() - int(ct)) / 86400)}
            ans.append(cur)
        elif ln and cur and cur['f'] == '?':
            cur['f'] = ln
    if not TOK: notes.append('بدون توکن، لاگ CI خونده نمی‌شه')
    return done(gs, ans, files, {'name': '%s/%s' % (o, r), 'url': 'https://github.com/%s/%s' % (o, r), 'ci': ci, 'total': scanned,
                                 't2': ['فایل بررسی‌شده', str(scanned)], 'note': ' · '.join(notes)}, healthy)


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
    tests = '--tests' in a
    a = [x for x in a if x != '--tests']
    cmd = a[0] if a else ''
    try:
        r = db().execute("select v from settings where k='token'").fetchone()
        TOK = os.environ.get('GITHUB_TOKEN') or (r[0] if r else '')
        if cmd == 'scan':
            q = a[1] if len(a) > 1 else ''
            if not q:
                raise Exception('لینک ریپوی گیت‌هاب رو بالا وارد کن و اسکن رو بزن')
            d = scan_gh(q, tests) if 'github.com' in q else scan_junit(q, a[2] if len(a) > 2 and a[2] else '.')
            gs = [s for s in d['S'] if s['t'] != 'angel']
            health = round(100 * 30 / (30 + sum(d['F'][s['fam']]['sev'] for s in gs)))
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
        elif cmd == 'last':
            row = db().execute('select data from scans order by id desc limit 1').fetchone()
            if not row:
                raise Exception('هنوز اسکنی نکردی؛ لینک ریپو رو بذار و اسکن رو بزن')
            d = json.loads(row[0]); d['cached'] = True
            out(d)
        elif cmd == 'gettoken':
            print(TOK)
        elif cmd == 'history':
            out([dict(zip(('repo', 'ts', 'ghosts', 'angels', 'health'), x)) for x in
                 db().execute('select repo,ts,ghosts,angels,health from scans order by id desc limit 10')])
        else:
            out({'error': 'دستور ناشناخته: scan | repos | settoken | history'})
    except Exception as e:
        out({'error': str(e)[:200]})
