// Ghost House backend (Node.js, بدون هیچ پکیج اضافه)
const http = require('http'), fs = require('fs'), path = require('path'), { execFile } = require('child_process');
const PORT = process.env.PORT || 8080, ROOT = __dirname, PUB = path.join(ROOT, 'public');
const MIME = { '.html': 'text/html; charset=utf-8', '.css': 'text/css; charset=utf-8', '.js': 'text/javascript; charset=utf-8' };

const run = (cmd, args, input) => new Promise(res => {
  const ch = execFile(cmd, args, { cwd: ROOT, timeout: 600000, maxBuffer: 20e6 },
    (e, out, err) => res({ ok: !e, out: out || '', err: (err || '') + (e ? e.message : '') }));
  if (input !== undefined) ch.stdin.end(input);
});
const py = (args, input) => run('python3', ['analyzer.py', ...args], input);
const parse = (r, fallback) => { try { return JSON.parse(r.out); } catch { return fallback || { error: 'تحلیل‌گر پایتون جواب نداد: ' + r.err.slice(0, 200) }; } };

// کلون رو analyzer.py می‌سازه؛ اینجا فقط مسیرش رو برمی‌گردونیم
function cloneDir(url) {
  const m = url.match(/github\.com[/:]([\w.-]+)\/([\w.-]+?)(?:\.git)?(?:[/#?]|$)/);
  const dir = m && path.join(ROOT, 'cache', m[1] + '__' + m[2]);
  return dir && fs.existsSync(dir) ? dir : null;
}

const SKIPD = /^(\.git|node_modules|dist|build|venv|__pycache__)$/;
function walk(d, b = '') {
  let o = [];
  for (const e of fs.readdirSync(path.join(d, b), { withFileTypes: true })) {
    if (SKIPD.test(e.name)) continue;
    const r = b ? b + '/' + e.name : e.name;
    if (e.isDirectory()) o = o.concat(walk(d, r)); else o.push(r);
  }
  return o;
}
function deps(dir, want) {
  const files = walk(dir).filter(f => /\.(js|cjs|mjs|jsx|ts|tsx|py)$/.test(f)).slice(0, 3000), set = new Set(files), g = {};
  const node = k => (g[k] = g[k] || { in: [], out: [] });
  const EX = ['', '.js', '.cjs', '.mjs', '.jsx', '.ts', '.tsx', '.py', '/index.js', '/index.ts', '/__init__.py'];
  for (const f of files) {
    let t = ''; try { t = fs.readFileSync(path.join(dir, f), 'utf8'); } catch { continue; }
    const base = path.posix.dirname(f), cand = [];
    if (f.endsWith('.py')) {
      for (const m of t.matchAll(/^\s*(?:from\s+(\.*)([\w.]*)\s+import|import\s+([\w.]+))/gm)) {
        const mod = (m[3] !== undefined ? m[3] : m[2]).replace(/\./g, '/');
        if (m[1]) cand.push(path.posix.join(base, ...Array(Math.max(0, m[1].length - 1)).fill('..'), mod));
        else cand.push(mod, path.posix.join(base, mod), path.posix.join('src', mod));
      }
    } else for (const m of t.matchAll(/(?:from\s+|require\(\s*|import\s*\(?\s*)['"](\.[^'"]*)['"]/g)) cand.push(path.posix.join(base, m[1]));
    for (const c of cand) {
      const hit = EX.map(x => c + x).find(x => x !== f && set.has(x));
      if (hit && !node(f).out.includes(hit)) { node(f).out.push(hit); node(hit).in.push(f); }
    }
  }
  const o = {};
  for (const k of want) if (g[k]) o[k] = { in: g[k].in.slice(0, 5), out: g[k].out.slice(0, 5) };
  return o;
}

async function scan(repo, dir, tests) {
  const args = repo || dir ? (dir ? ['scan', repo, dir] : ['scan', repo]) : ['last'];
  if (tests && args[0] === 'scan') args.push('--tests');
  const d = parse(await py(args));
  const url = (d.meta && d.meta.url) || '';
  if (d.error || !/github\.com/.test(url)) return d;
  const cdir = cloneDir(url);
  if (cdir) {
    const j = await run('java', ['SourceScanner.java', cdir]);
    if (j.ok) d.metrics = parse(j, []);
    try { d.deps = deps(cdir, new Set(d.S.concat(d.sleep || []).map(s => s.f))); } catch (e) {}
  }
  return d;
}

http.createServer(async (req, res) => {
  const u = new URL(req.url, 'http://x'), p = u.pathname;
  const send = (o, c = 200) => { res.writeHead(c, { 'Content-Type': 'application/json; charset=utf-8' }); res.end(JSON.stringify(o)); };
  try {
    if (p === '/api/scan') return send(await scan(u.searchParams.get('repo') || '', u.searchParams.get('dir') || '', u.searchParams.get('tests') === '1'));
    if (p === '/api/repos') return send(parse(await py(['repos'])));
    if (p === '/api/history') return send(parse(await py(['history']), []));
    if (p === '/api/token' && req.method === 'POST') {
      let b = ''; for await (const c of req) b += c;
      const t = (JSON.parse(b || '{}').token || '').trim();
      if (!t) return send({ error: 'توکن خالیه' }, 400);
      return send(parse(await py(['settoken'], t)));
    }
    const f = path.join(PUB, p === '/' ? 'index.html' : p);
    if (!f.startsWith(PUB) || !fs.existsSync(f) || fs.statSync(f).isDirectory()) { res.writeHead(404); return res.end('404'); }
    res.writeHead(200, { 'Content-Type': MIME[path.extname(f)] || 'application/octet-stream' });
    fs.createReadStream(f).pipe(res);
  } catch (e) { send({ error: String(e).slice(0, 200) }, 500); }
}).listen(PORT, '127.0.0.1', () => console.log('Ghost House روشنه: http://localhost:' + PORT));
