"""Ghost House inspector: تحلیل واقعی کد ریپو (بدون اجرای کد)."""
import ast, json, os, re, shutil, subprocess, time

SKIP = re.compile(r'(^|/)(\.git|node_modules|dist|build|venv|\.venv|__pycache__|vendor|\.next|coverage|site-packages)(/|$)')
CODE = ('.py', '.js', '.cjs', '.mjs', '.jsx', '.ts', '.tsx', '.java', '.kt', '.go', '.rs', '.rb', '.php', '.c', '.cpp', '.cs', '.dart', '.swift', '.sh', '.lua', '.vue', '.svelte')
SECRET = re.compile(r"""(?i)\b(api[_-]?key|secret|passwd|password|token|private[_-]?key)\b\s*[:=]\s*['"]([^'"\s]{8,})['"]""")
PLACE = re.compile(r'(?i)(example|your|xxx|change|placeholder|dummy|sample|test|<|\$\{|\{\{|environ|getenv|process\.env|\*\*\*)')
BADFILE = re.compile(r'(^|/)(\.env|id_rsa|id_dsa|[^/]*\.pem|[^/]*\.p12|credentials\.json|[^/]*\.keystore)$')
ISTEST = re.compile(r'(^|/)(tests?|__tests__|spec)/|(^|/)test_[^/]*\.py$|_test\.(py|go)$|\.(test|spec)\.(js|jsx|ts|tsx)$')
ESM_OK = re.compile(r'Cannot use import|Unexpected token .export|await is only valid|import\.meta|Unexpected identifier .from')


def F(rule, t, sev, ttl, line, msg, fx):
    return {'rule': rule, 't': t, 'sev': sev, 'ttl': ttl, 'n': ttl, 'l': line, 'c': msg[:160], 'fx': fx}


def py_checks(src, is_test, init):
    try:
        tree = ast.parse(src)
    except SyntaxError as e:
        return [F('syntax', 'assert', 3, 'خطای سینتکس', e.lineno or 0, str(e.msg), 'خط رو اصلاح کن؛ پایتون نمی‌تونه این فایل رو بخونه')]
    out, imps = [], []
    names = {n.id for n in ast.walk(tree) if isinstance(n, ast.Name)}
    for n in ast.walk(tree):
        if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)):
            cx = 1 + sum(isinstance(x, (ast.If, ast.For, ast.While, ast.Try, ast.BoolOp, ast.ExceptHandler, ast.IfExp, ast.comprehension)) for x in ast.walk(n))
            ln = (n.end_lineno or n.lineno) - n.lineno + 1
            if cx > 12 or ln > 80:
                out.append(F('complex', 'timeout', 2, 'تابع خیلی پیچیده یا بلند', n.lineno, '%s: پیچیدگی %d، %d خط' % (n.name, cx, ln), 'تابع رو به چند تابع کوچیک بشکن'))
            for d in n.args.defaults + [x for x in n.args.kw_defaults if x]:
                if isinstance(d, (ast.List, ast.Dict, ast.Set)):
                    out.append(F('mutdef', 'assert', 2, 'آرگومان پیش‌فرض قابل‌تغییر', d.lineno, n.name + ': مقدار بین فراخوانی‌ها مشترک می‌مونه', 'پیش‌فرض رو None بذار و داخل تابع بساز'))
        elif isinstance(n, ast.ExceptHandler):
            if n.type is None:
                out.append(F('bare-except', 'null', 2, 'except خالی که همه‌ی خطاها رو می‌گیره', n.lineno, 'حتی Ctrl+C هم گرفته می‌شه', 'نوع خطا رو مشخص کن'))
            elif len(n.body) == 1 and isinstance(n.body[0], ast.Pass):
                out.append(F('swallow', 'null', 2, 'خطا بی‌صدا نادیده گرفته می‌شه', n.lineno, 'except ...: pass', 'حداقل خطا رو لاگ کن'))
        elif isinstance(n, ast.Call):
            if isinstance(n.func, ast.Name) and n.func.id in ('eval', 'exec'):
                out.append(F('eval', 'issue', 3, 'استفاده از eval یا exec', n.lineno, n.func.id + '() روی ورودی خطرناکه', 'از ast.literal_eval یا یه پارسر امن استفاده کن'))
            for k in n.keywords:
                if k.arg == 'shell' and isinstance(k.value, ast.Constant) and k.value.value is True:
                    out.append(F('shell', 'issue', 3, 'اجرای shell با shell=True', n.lineno, 'ریسک تزریق دستور', 'لیست آرگومان بده و shell=True رو حذف کن'))
                if k.arg == 'verify' and isinstance(k.value, ast.Constant) and k.value.value is False:
                    out.append(F('ssl', 'issue', 3, 'بررسی گواهی SSL خاموشه', n.lineno, 'verify=False', 'گواهی رو درست تنظیم کن و verify=False رو حذف کن'))
        elif isinstance(n, ast.Compare):
            if any(isinstance(o, (ast.Eq, ast.NotEq)) for o in n.ops) and any(isinstance(c, ast.Constant) and c.value is None for c in n.comparators):
                out.append(F('none-eq', 'null', 1, 'مقایسه با None به‌جای is', n.lineno, 'x == None', 'از is None یا is not None استفاده کن'))
        elif isinstance(n, ast.Import):
            imps += [((a.asname or a.name).split('.')[0], n.lineno) for a in n.names]
        elif isinstance(n, ast.ImportFrom) and n.module != '__future__':
            imps += [(a.asname or a.name, n.lineno) for a in n.names if a.name != '*']
    un = [(a, l) for a, l in imps if a not in names]
    if not init and un:
        out.append(F('unused-import', 'null', 1, 'import بلااستفاده', un[0][1], '%d مورد: %s' % (len(un), ', '.join(a for a, _ in un[:5])), 'importهای بلااستفاده رو پاک کن'))
    if is_test:
        m = list(re.finditer(r'\b(time\.sleep|random\.\w+|datetime\.now|time\.time)\(', src))
        if m:
            out.append(F('flaky-test', 'flaky', 2, 'تست وابسته به زمان یا تصادف', src.count('\n', 0, m[0].start()) + 1, '%d مورد: %s' % (len(m), m[0].group(1)), 'زمان و random رو mock کن یا seed ثابت بذار'))
    return out


def js_checks(src, is_test):
    out = []
    for i, ln in enumerate(src.split('\n'), 1):
        s = ln.strip()
        if s.startswith(('//', '*', '/*')): continue
        if re.search(r'\beval\s*\(|new Function\s*\(', s):
            out.append(F('eval', 'issue', 3, 'استفاده از eval یا new Function', i, s[:100], 'جایگزین امن بنویس'))
        if re.search(r'\.innerHTML\s*=(?!=)', s) and not re.search(r"""=\s*(['"`])[^$'"`]*\1\s*;?\s*$""", s):
            out.append(F('xss', 'issue', 2, 'نوشتن HTML خام با innerHTML', i, s[:100], 'از textContent یا پاک‌سازی ورودی استفاده کن'))
        if re.search(r'document\.write\s*\(', s):
            out.append(F('docwrite', 'issue', 2, 'استفاده از document.write', i, s[:100], 'با DOM API جایگزینش کن'))
        if re.match(r'debugger\b', s):
            out.append(F('debugger', 'assert', 1, 'دستور debugger جا مونده', i, s, 'پاکش کن'))
    for m in re.finditer(r'catch\s*(?:\([^)]*\))?\s*\{\s*\}', src):
        out.append(F('swallow', 'null', 2, 'catch خالی که خطا رو می‌خوره', src.count('\n', 0, m.start()) + 1, m.group(0)[:60], 'خطا رو لاگ کن یا مدیریتش کن'))
    n = len(re.findall(r'console\.log\(', src))
    if n > 10 and not is_test:
        out.append(F('console', 'issue', 1, 'console.log زیاد', 1, '%d مورد' % n, 'لاگ‌های دیباگ رو پاک کن'))
    m = list(re.finditer(r'\b(setTimeout|Math\.random|Date\.now)\(', src))
    if is_test and m:
        out.append(F('flaky-test', 'flaky', 2, 'تست وابسته به زمان یا تصادف', src.count('\n', 0, m[0].start()) + 1, '%d مورد: %s' % (len(m), m[0].group(1)), 'از fake timers و mock استفاده کن'))
    return out


def common_checks(src, path):
    out = []
    m = re.search(r'^(<<<<<<<|>>>>>>>) ', src, re.M)
    if m:
        out.append(F('conflict', 'assert', 3, 'مارکر کانفلیکت مرج جا مونده', src.count('\n', 0, m.start()) + 1, m.group(0), 'مارکرها رو پاک کن و نسخه‌ی درست رو نگه دار'))
    if not ISTEST.search(path):
        for m in SECRET.finditer(src):
            line = src[src.rfind('\n', 0, m.start()) + 1:src.find('\n', m.end())]
            if not PLACE.search(m.group(2)) and not PLACE.search(line):
                out.append(F('secret', 'issue', 3, 'رمز یا کلید داخل کد', src.count('\n', 0, m.start()) + 1, m.group(1) + ' = ' + m.group(2)[:3] + '…', 'مقدار رو ببر توی متغیر محیطی و اگه لو رفته عوضش کن'))
                break
    m = list(re.finditer(r'\b(TODO|FIXME|HACK|XXX)\b', src))
    if len(m) >= 3 or any(x.group(1) in ('FIXME', 'HACK', 'XXX') for x in m):
        out.append(F('todo', 'issue', 1, 'TODO و FIXME باقی‌مونده', src.count('\n', 0, m[0].start()) + 1, '%d مورد' % len(m), 'کارهای باقی‌مونده رو ببند یا تبدیل به issue کن'))
    if src.count('\n') > 1000:
        out.append(F('big', 'timeout', 1, 'فایل خیلی بزرگ', 1, '%d خط' % src.count('\n'), 'فایل رو به ماژول‌های کوچیک‌تر تقسیم کن'))
    if path.endswith(('.java', '.kt')):
        for m in re.finditer(r'catch\s*\([^)]*\)\s*\{\s*\}', src):
            out.append(F('swallow', 'null', 2, 'catch خالی که خطا رو می‌خوره', src.count('\n', 0, m.start()) + 1, m.group(0)[:60], 'خطا رو لاگ کن'))
    return out


def ginfo(d, f):
    try:
        r = subprocess.run(['git', '-C', d, 'log', '-1', '--format=%h|%an|%ct', '--', f], capture_output=True, text=True, timeout=15).stdout.strip()
        h, a, ct = (r + '||').split('|')[:3]
        return h or '-', a or '-', int((time.time() - int(ct)) / 86400) if ct.isdigit() else 0
    except Exception:
        return '-', '-', 0


def inspect_repo(d, files, limit=60):
    """خروجی: (فهرست مشکل‌ها، تعداد فایل‌های بررسی‌شده، فایل‌های سالم)"""
    res, scanned, nodes, has_test, locs = [], 0, shutil.which('node'), False, {}
    files = [f for f in files if not SKIP.search(f)]
    for f in files:
        if ISTEST.search(f): has_test = True
        if BADFILE.search(f):
            res.append(dict(F('secret-file', 'issue', 3, 'فایل حساس توی ریپو کامیت شده', 1, f, 'از ریپو حذفش کن، به .gitignore اضافه کن و کلیدها رو عوض کن'), f=f))
    for f in files[:1500]:
        p = os.path.join(d, f)
        ext = os.path.splitext(f)[1].lower()
        if ext not in CODE and ext != '.json': continue
        try:
            if os.path.getsize(p) > 1500000: continue
            src = open(p, encoding='utf-8', errors='replace').read()
        except OSError:
            continue
        if len(src) > 5000 and src.count('\n') < len(src) / 400: continue  # minified
        scanned += 1
        found = []
        if ext in CODE and not ISTEST.search(f): locs[f] = src.count('\n') + 1
        if ext == '.json':
            if not re.search(r'(tsconfig|jsconfig|\.vscode)', f):
                try: json.loads(src)
                except ValueError as e:
                    found.append(F('syntax', 'assert', 3, 'JSON نامعتبر', getattr(e, 'lineno', 1), str(e)[:100], 'کاما یا کوتیشن اضافه یا کم رو درست کن'))
        else:
            test = bool(ISTEST.search(f))
            found += common_checks(src, f)
            if ext == '.py': found += py_checks(src, test, f.endswith('__init__.py'))
            elif ext in ('.js', '.cjs', '.mjs', '.jsx', '.ts', '.tsx'):
                found += js_checks(src, test)
                if nodes and ext in ('.js', '.cjs', '.mjs') and scanned < 150:
                    try:
                        r = subprocess.run([nodes, '--check', p], capture_output=True, text=True, timeout=10)
                        if r.returncode and 'SyntaxError' in r.stderr and not ESM_OK.search(r.stderr):
                            ln = re.search(r':(\d+)\n', r.stderr)
                            found.append(F('syntax', 'assert', 3, 'خطای سینتکس', int(ln[1]) if ln else 0, r.stderr.split('SyntaxError:')[-1].strip()[:100], 'خط رو اصلاح کن؛ Node نمی‌تونه این فایل رو بخونه'))
                    except Exception:
                        pass
        seen = {}
        for x in found:
            seen[x['rule']] = seen.get(x['rule'], 0) + 1
            if seen[x['rule']] <= 5: res.append(dict(x, f=f))
    code_files = [f for f in files if os.path.splitext(f)[1].lower() in CODE and not ISTEST.search(f)]
    if not has_test and len(code_files) >= 5:
        res.append(dict(F('no-tests', 'null', 2, 'هیچ تستی پیدا نشد', 0, '%d فایل کد و صفر فایل تست' % len(code_files), 'برای بخش‌های مهم تست بنویس (pytest یا Jest)'), f='tests/'))
    res.sort(key=lambda g: (-g['sev'], g['f'], g['l']))
    res = res[:limit]
    cache = {}
    for g in res:
        g['cm'], g['au'], g['d'] = cache.setdefault(g['f'], ginfo(d, g['f'] if g['f'] != 'tests/' else '.'))
    bad = {g['f'] for g in res}
    healthy = sorted(([{'f': f, 'loc': n} for f, n in locs.items() if f not in bad]), key=lambda x: -x['loc'])[:14]
    return res, scanned, healthy
