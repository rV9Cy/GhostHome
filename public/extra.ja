(function () {
  var E = function (s) { return document.getElementById(s); };
  var ROW = 'style="width:auto;flex:1;direction:ltr;text-align:left"';

  function repos() {
    fetch('api/repos').then(function (r) { return r.json(); }).then(function (d) {
      if (d.error) { E('tmsg').textContent = d.error; return; }
      E('rl').innerHTML = d.map(function (r) {
        return '<a class="ch an" style="text-decoration:none" href="?repo=' + encodeURIComponent(r.url) + '">' + r.name + '</a>';
      }).join('');
      E('tmsg').textContent = d.length + ' ریپو پیدا شد؛ روی هر کدوم بزن تا اسکن بشه.';
    }).catch(function () {});
  }

  function hist() {
    fetch('api/history').then(function (r) { return r.json(); }).then(function (d) {
      if (!d.length) return;
      E('hist').innerHTML = d.map(function (r) {
        return '<div class="kv"><span ' + ROW + '>' + r.repo + '</span><span>' + new Date(r.ts * 1000).toLocaleDateString('fa-IR') +
          ' · ' + r.ghosts + ' روح · ' + r.angels + ' فرشته · سلامت ' + r.health + '</span></div>';
      }).join('');
    }).catch(function () {});
  }

  E('svt').onclick = function (e) {
    e.preventDefault();
    var t = E('tok').value.trim();
    if (!t) { E('tmsg').textContent = 'اول توکن رو وارد کن.'; return; }
    fetch('api/token', { method: 'POST', body: JSON.stringify({ token: t }) }).then(function (r) { return r.json(); }).then(function (d) {
      E('tok').value = '';
      E('tmsg').textContent = d.ok ? 'ذخیره شد.' : d.error;
      if (d.ok) repos();
    });
  };

  document.addEventListener('scan', function (e) {
    var m = e.detail.metrics;
    if (m && m.length) {
      E('hot').innerHTML = m.map(function (x) {
        return '<div class="kv"><span ' + ROW + '><code>' + x.f + '</code></span><span>' + x.loc + ' خط · پیچیدگی ' + x.cx + ' · TODO ' + x.todo + '</span></div>';
      }).join('');
    }
    hist();
  });
  repos();
  hist();
})();
