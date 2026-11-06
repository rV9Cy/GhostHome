<p align="center">
  <a href="README.md"><img src="https://img.shields.io/badge/ENG-English-2563eb?style=for-the-badge" alt="ENG"></a>
  <a href="README.fa.md"><img src="https://img.shields.io/badge/FA-%D9%81%D8%A7%D8%B1%D8%B3%DB%8C-6b7280?style=for-the-badge" alt="FA"></a>
</p>

<p align="center">
  <a href="https://t.me/ArrowDeveloper"><img src="https://img.shields.io/badge/Telegram-Join%20the%20channel-26A5E4?style=for-the-badge&logo=telegram&logoColor=white" alt="Telegram"></a>
  <a href="https://donate.sudoshz.ir/u/spidey_team"><img src="https://img.shields.io/badge/Donate-Support%20the%20project-F5A623?style=for-the-badge&logo=githubsponsors&logoColor=white" alt="Donate"></a>
</p>

<p align="center"><img src="assets/poster.svg" alt="Ghost House" width="100%"></p>

<h1 align="center"><img src="assets/logo.svg" width="48" align="absmiddle"> Ghost House</h1>

<p align="center"><b>Every failing test becomes a ghost. Every fix becomes an angel.</b><br>
A 3D dashboard that scans your GitHub repos and shows what is broken, where, why, and how to fix it.</p>

---

<p align="center">
  <img src="https://img.shields.io/badge/LICENSE-MIT-2ea44f?style=for-the-badge" alt="MIT">
  <img src="https://img.shields.io/badge/NODE.JS-SERVER-339933?style=for-the-badge&logo=nodedotjs&logoColor=white" alt="Node.js">
  <img src="https://img.shields.io/badge/PYTHON-ANALYZER-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/JAVA-SCANNER-E76F00?style=for-the-badge&logo=openjdk&logoColor=white" alt="Java">
  <img src="https://img.shields.io/badge/SQLITE-DATABASE-003B57?style=for-the-badge&logo=sqlite&logoColor=white" alt="SQLite">
  <img src="https://img.shields.io/badge/HTML5-FRONTEND-E34F26?style=for-the-badge&logo=html5&logoColor=white" alt="HTML5">
  <img src="https://img.shields.io/badge/CSS3-STYLE-1572B6?style=for-the-badge&logo=css3&logoColor=white" alt="CSS3">
  <img src="https://img.shields.io/badge/JAVASCRIPT-UI-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black" alt="JavaScript">
  <img src="https://img.shields.io/badge/THREE.JS-3D-000000?style=for-the-badge&logo=threedotjs&logoColor=white" alt="Three.js">
</p>

<p align="center">
  <a href="#-quick-start-termux">Quick Start</a> ·
  <a href="#-what-you-get">Features</a> ·
  <a href="#-meet-the-spirits">Spirits</a> ·
  <a href="#-usage">Usage</a> ·
  <a href="#-project-structure">Structure</a> ·
  <a href="#-support">Support</a>
</p>

> Independent open-source project. It is not affiliated with GitHub.

## ✨ What You Get

- **3D haunted house**: a bug is an awake ghost, a healthy file is a ghost fast asleep, and a recently fixed bug is an angel. Drag to spin, tap to inspect.
- **GitHub connection**: scan any public repo by link, or connect a token to list your own (private included).
- **Full status**: health score, CI result, failing tests, open `bug` issues, and recent `fix` commits.
- **Problems grouped by root cause**, with file, line, suspect commit, author, age, and a fix hint.
- **Dependency graph** for every file: who imports it and what it imports.
- **File tree** with ghost and angel badges on every file.
- **Hot files** ranked by a Java scanner (complexity, TODO/FIXME density).
- **Scan history** stored in SQLite so you can watch the project heal over time.
- **Zero npm packages.** Built to run on a phone with Termux.

## 👻 Meet the Spirits

| Spirit | Means | Look |
|---|---|---|
| Assertion ghost | wrong output, assertion failed | blue, monocle, frowning |
| Timeout ghost | slow or hanging code | yellow, sleepy, `zZ` |
| NullPointer ghost | missing or empty value | see-through, `?` |
| Flaky ghost | unstable test that comes and goes | purple, flickering |
| Issue ghost | open bug issue | pink, `!` |
| Sleeping ghost | healthy file, no bug found | gray-blue, eyes closed, `zZ`, breathing |
| Angel | fixed recently | white, halo, flapping wings |

Health score = `100 - 2 x (sum of ghost severities)`.

## 🚀 Quick Start (Termux)

```bash
pkg update && pkg upgrade -y
pkg install nodejs python git openjdk-17 -y      # openjdk is optional (hot files)
git clone https://github.com/rv9cy/ghost-house.git
cd ghost-house
node Server.js
```

Open **http://localhost:8080** in your phone browser.

Another port: `PORT=3000 node Server.js`

## 🧭 Usage

1. Paste a repo link such as `https://github.com/user/repo` and tap **Scan**.
2. For your own repos, open the **GitHub** tab, paste a personal access token (read access is enough) and tap **Save**. The token stays in the local SQLite file only. With a token, Ghost House also reads your CI logs and lists the failed pytest, Jest and Go tests.
3. Tap a ghost or angel, then open the **Dependencies** tab to see its graph.

Command line:

```bash
python3 analyzer.py scan https://github.com/user/repo        # scan and save
pytest --junitxml=report.xml                                   # local project
python3 analyzer.py scan report.xml /path/to/project           # scan a pytest report
python3 analyzer.py history                                    # past scans
```

**How the scan works.** Ghost House clones the repo to your phone and inspects the real code (no guessing):

- **Errors:** Python, JavaScript and JSON syntax errors, leftover merge-conflict markers.
- **Bugs:** mutable default arguments, bare or swallowed `except` and `catch`, `== None`, leftover `debugger`.
- **Security:** `eval`, `shell=True`, disabled SSL checks, hard-coded secrets, committed `.env` or key files, raw `innerHTML`.
- **Smells:** very complex or long functions, unused imports, TODO/FIXME piles, tests that depend on time or randomness, repos with no tests.
- **CI:** failed GitHub Actions steps and open `bug` issues; with a token it also reads the CI logs (pytest, Jest, Go).
- **Run the tests:** tick **Run tests** to execute pytest, `npm test` or `go test` on your phone and turn real failures into ghosts.
- **Angels:** recent commits whose message contains `fix`.

## 🗂 Project Structure

```text
ghost-house/
├── Server.js            Node server, REST API, git clone, import graph
├── analyzer.py          clone, CI logs, test runs, SQLite storage (CLI)
├── inspector.py         real static analysis of the repo code
├── SourceScanner.java   hot-file ranking (complexity, TODOs)
├── public/
│   ├── index.html       page layout
│   ├── style.css        responsive styles
│   ├── app.js           3D scene, panels, dependency graph
│   └── extra.js         GitHub connect, hot files, history
├── assets/              poster and logo
└── data/                SQLite database (git-ignored)
```

API: `GET /api/scan?repo=` · `GET /api/repos` · `GET /api/history` · `POST /api/token`

## 🗺 Roadmap

- Jest and JUnit report support
- Auto-create GitHub issues from ghosts
- GitHub Action that comments the health score on pull requests

## 💖 Support

If Ghost House saves you time, you can support it:

- **Donate:** [https://donate.sudoshz.ir/u/spidey_team](https://donate.sudoshz.ir/u/spidey_team)
- **Telegram channel:** [https://t.me/ArrowDeveloper](https://t.me/ArrowDeveloper)
- Star the repo and share it with a friend.

## 📄 License

MIT. See [LICENSE](LICENSE).

<p align="center">Made with care by <a href="https://github.com/rv9cy"><b>Arrow</b></a></p>
