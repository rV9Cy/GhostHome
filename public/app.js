document.querySelectorAll('.tb').forEach(function(tb){tb.querySelectorAll('button').forEach(function(b){b.onclick=function(){
tb.querySelectorAll('button').forEach(function(x){x.classList.toggle('on',x===b)});
tb.parentNode.querySelectorAll('.pane').forEach(function(p){p.hidden=p.id!=b.dataset.p})}})});
var DEPS={
'src/auth/token.py':{in:['src/auth/session.py','src/payment/gateway.py','tests/test_token.py'],out:['src/db/pool.py']},
'src/auth/session.py':{in:['src/cart/cart.py','tests/test_token.py'],out:['src/auth/token.py','src/db/pool.py']},
'src/cart/cart.py':{in:['tests/test_cart.py','src/payment/gateway.py'],out:['src/cart/pricing.py','src/auth/session.py','src/db/pool.py']},
'src/cart/pricing.py':{in:['src/cart/cart.py','tests/test_cart.py'],out:[]},
'src/payment/gateway.py':{in:['tests/test_payment.py'],out:['src/cart/cart.py','src/auth/token.py']},
'src/db/pool.py':{in:['src/auth/session.py','src/cart/cart.py','tests/test_db.py'],out:[]}
};
function dep(s){
var d=DEPS[s.f]||{in:[],out:[]},L=d.in.slice(0,5),Rt=d.out.slice(0,5);
if(!L.length&&!Rt.length){$('dep').innerHTML='<div class="mut">وابستگی‌ای برای این فایل پیدا نشد.</div>';return}
var n=Math.max(L.length,Rt.length),H=n*38+8,cy=H/2;
function nm(f){var x=f.split('/').pop();return x.length>15?x.slice(0,14)+'…':x}
function nd(x,y,f,cl){
var g=S.find(function(q){return q.f==f&&q.t!='angel'}),a=S.find(function(q){return q.f==f&&q.t=='angel'}),t=g||a;
return '<g class="nd '+cl+'"'+(t&&cl!='cen'?' onclick="show('+t.id+')" style="cursor:pointer"':'')+'><rect x="'+x+'" y="'+(y-14)+'" width="100" height="28" rx="8"/><text x="'+(x+50)+'" y="'+(y+4)+'" text-anchor="middle">'+nm(f)+'</text>'+
(t?'<circle cx="'+(x+96)+'" cy="'+(y-12)+'" r="5" fill="'+(g?'var(--red)':'var(--grn)')+'"/>':'')+'</g>'}
var svg='<svg viewBox="0 0 360 '+H+'" width="100%" role="img" aria-label="گراف وابستگی">',body='';
L.forEach(function(f,i){var y=(i+.5)*H/L.length;svg+='<path class="ln" stroke="#4db3ff" d="M100 '+y+' C118 '+y+' 112 '+cy+' 130 '+cy+'"/>';body+=nd(0,y,f,'in')});
Rt.forEach(function(f,i){var y=(i+.5)*H/Rt.length;svg+='<path class="ln" stroke="#e0a82e" d="M230 '+cy+' C248 '+cy+' 242 '+y+' 260 '+y+'"/>';body+=nd(260,y,f,'out')});
body+=nd(130,cy,s.f,'cen');
$('dep').innerHTML='<div class="mut" style="display:flex;gap:14px;margin-bottom:6px"><span><b style="color:#4db3ff">●</b> کی ازش استفاده می‌کنه</span><span><b style="color:#e0a82e">●</b> خودش از کی استفاده می‌کنه</span></div>'+svg+body+'</svg>'+
'<div class="mut" style="margin-top:4px">نقطه‌ی قرمز یا سبز یعنی اون فایل روح یا فرشته داره؛ روش بزن.</div>';
}

var S=[
{id:1,n:'test_parse_expired_token',t:'assert',f:'src/auth/token.py',l:48,c:'انتظار می‌رفت TokenExpired پرتاب بشه ولی None برگشت',cm:'a3f91c2',au:'سارا',d:9,fam:'F1'},
{id:2,n:'test_refresh_token_rotation',t:'assert',f:'src/auth/token.py',l:77,c:'توکن جدید با همون زمان انقضای قدیمی ساخته می‌شه',cm:'a3f91c2',au:'سارا',d:9,fam:'F1'},
{id:3,n:'test_cart_total_with_coupon',t:'assert',f:'src/cart/pricing.py',l:31,c:'جمع سبد 19.98999 شد به‌جای 19.99 (خطای اعشار)',cm:'7e20bd9',au:'نیما',d:3,fam:'F2'},
{id:4,n:'test_checkout_timeout',t:'timeout',f:'src/payment/gateway.py',l:112,c:'درگاه بعد از ۳۰ ثانیه جواب نداد و تلاش دوباره‌ای وجود نداره',cm:'1c4a6f3',au:'مینا',d:14,fam:'F3'},
{id:5,n:'test_apply_discount_none',t:'null',f:'src/cart/cart.py',l:59,c:'خطای NoneType: سبد خالی قبل از استفاده چک نمی‌شه',cm:'d92b0a1',au:'علی',d:5,fam:'F4'},
{id:6,n:'test_inventory_sync',t:'flaky',f:'src/db/pool.py',l:23,c:'رِیس‌کاندیشن موقع ساخت pool؛ تقریباً از هر ۴ اجرا ۱ بار می‌شکنه',cm:'5fa83e7',au:'نیما',d:21,fam:'F5'},
{id:7,n:'test_login_ok',t:'angel',f:'src/auth/session.py',l:20,c:'کوکی session حالا بعد از لاگین درست ست می‌شه',cm:'b81d0e4',au:'علی',d:1},
{id:8,n:'test_cart_empty',t:'angel',f:'src/cart/cart.py',l:14,c:'سبد خالی دیگه خطا نمی‌ده',cm:'3ac19d8',au:'سارا',d:2},
{id:9,n:'test_db_reconnect',t:'angel',f:'src/db/pool.py',l:61,c:'بعد از قطع شدن، اتصال دوباره برقرار می‌شه',cm:'e7740b2',au:'مینا',d:6}
];
var F={
F1:{t:'منطق parse_token خراب شده',sev:3,fx:'بررسی زمان انقضا رو قبل از decode برگردون؛ کامیت a3f91c2 حذفش کرده'},
F2:{t:'خطای اعشار در محاسبه‌ی قیمت',sev:2,fx:'به‌جای float از Decimal استفاده کن و با quantize گرد کن'},
F3:{t:'نبود retry در درگاه پرداخت',sev:3,fx:'retry با backoff نمایی اضافه کن و timeout رو قابل‌تنظیم کن'},
F4:{t:'نبود چک None در سبد خرید',sev:2,fx:'قبل از دسترسی به items یه شرط محافظ بذار'},
F5:{t:'رِیس‌کاندیشن در ساخت pool دیتابیس',sev:1,fx:'ساخت pool رو پشت یه lock بذار'}
};
var T=[[0,'src/'],[1,'auth/'],[2,'token.py','src/auth/token.py'],[2,'session.py','src/auth/session.py'],[1,'cart/'],[2,'cart.py','src/cart/cart.py'],[2,'pricing.py','src/cart/pricing.py'],[1,'payment/'],[2,'gateway.py','src/payment/gateway.py'],[1,'db/'],[2,'pool.py','src/db/pool.py'],[0,'tests/'],[1,'test_token.py'],[1,'test_cart.py'],[1,'test_payment.py'],[1,'test_db.py'],[0,'.github/workflows/'],[1,'ci.yml'],[0,'README.md'],[0,'requirements.txt']];
var TY={assert:['AssertionError',0xa8c5e6],timeout:['Timeout',0xf2d48a],null:['NullPointer',0xc9ccdf],flaky:['Flaky',0xc3a6f0],angel:['فرشته',0xffffff],issue:['باگ باز',0xf5a3a3]};
var SV=['','کم','متوسط','بالا'],SC=['','var(--mut)','var(--amb)','var(--red)'];
var $=function(i){return document.getElementById(i)};
var hex=function(c){return c===0xffffff?'#ffd166':'#'+c.toString(16).padStart(6,'0')};
var cur=1,follow=true,META={total:128,ci:'آخرین بیلد روی <code>main</code> شکست خورد؛ کامیت <code>a3f91c2</code>. پوشش تست: 82%. قدیمی‌ترین روح: <code>test_inventory_sync</code> با 21 روز.'};

function cu(e){var n=+e.dataset.n,s=e.dataset.s||'',t0=performance.now();(function f(t){var k=Math.min(1,(t-t0)/900);e.textContent=Math.round(n*(1-Math.pow(1-k,3)))+s;if(k<1)requestAnimationFrame(f)})(t0)}
function show(id){
cur=id;follow=true;
var s=S.find(function(x){return x.id==id}),ty=TY[s.t],an=s.t=='angel',f=F[s.fam];
$('det').classList.remove('fade');void $('det').offsetWidth;$('det').classList.add('fade');$('det').innerHTML='<div class="sb" style="background:'+(an?'var(--gb)':'var(--rb)')+';color:'+(an?'var(--grn)':'var(--red)')+'">'+(an?'فرشته: این تست نجات پیدا کرده':s.t=='issue'?'باگ باز: هنوز حل نشده':'روح: این تست هنوز شکسته')+'</div>'+
'<div style="display:flex;gap:8px;align-items:center;justify-content:space-between"><b style="font-weight:500;overflow-wrap:anywhere">'+s.n+'</b><span class="tag" style="border:1px solid '+hex(ty[1])+'">'+ty[0]+'</span></div>'+
'<p class="mut" style="margin:4px 0"><code>'+s.f+':'+s.l+'</code></p>'+
'<p style="margin:6px 0">'+s.c+'</p>'+
'<p class="mut" style="margin:6px 0">'+(an?'نجات‌دهنده':'مشکوک')+': <code>'+s.cm+'</code> · '+s.au+' · '+(an?s.d+' روز پیش':s.d+' روزه')+'</p>'+
(f?'<div class="fx">'+f.fx+'</div>':'');
dep(s);
document.querySelectorAll('.pb').forEach(function(e){e.classList.toggle('on',e.dataset.f==s.fam)});
document.querySelectorAll('.ch').forEach(function(e){e.classList.toggle('on',e.dataset.i==id)});
}

function init(){
var gh=S.filter(function(s){return s.t!='angel'}),an=S.filter(function(s){return s.t=='angel'});
var health=Math.max(0,100-2*gh.reduce(function(a,s){return a+F[s.fam].sev},0));
var hc=health>=80?'var(--grn)':health>=60?'var(--amb)':'var(--red)';
var t2=META.t2||['سالم',(META.total-gh.length)+'/'+META.total];
$('stats').innerHTML=
'<div class="st"><span class="mut">سلامت</span><b class="cu" data-n="'+health+'" data-s="/100" style="color:'+hc+'">0</b></div>'+
'<div class="st"><span class="mut">'+t2[0]+'</span><b>'+t2[1]+'</b></div>'+
'<div class="st"><span class="mut">ارواح</span><b class="cu" data-n="'+gh.length+'" style="color:var(--red)">0</b></div>'+
'<div class="st"><span class="mut">فرشته‌ها</span><b class="cu" data-n="'+an.length+'" style="color:var(--grn)">0</b></div>';
$('hb').style.background=hc;setTimeout(function(){$('hb').style.width=health+'%'},200);document.querySelectorAll('.cu').forEach(cu);
$('ci').innerHTML=META.ci;

$('tree').innerHTML=T.map(function(r){
var d=r[0],n=r[1],p=r[2],dir=n.slice(-1)=='/';
var g=p?S.filter(function(s){return s.f==p&&s.t!='angel'}).length:0,a=p?S.filter(function(s){return s.f==p&&s.t=='angel'}).length:0;
var first=p&&S.find(function(s){return s.f==p});
return '<div class="row'+(first?' c':'')+'" style="padding-left:'+d*16+'px"'+(first?' onclick="show('+first.id+')"':'')+'><span>'+(dir?'▾':'·')+'</span><span>'+n+'</span>'+
(g?'<span class="tag" style="background:var(--rb);color:var(--red)">'+g+' روح</span>':'')+
(a?'<span class="tag" style="background:var(--gb);color:var(--grn)">'+a+' فرشته</span>':'')+'</div>';
}).join('');

$('pbs').innerHTML=Object.keys(F).sort(function(a,b){return F[b].sev-F[a].sev}).map(function(k){
var ts=S.filter(function(s){return s.fam==k}),f=F[k],s0=ts[0];
return '<div class="pb" data-f="'+k+'" onclick="show('+s0.id+')"><div style="display:flex;justify-content:space-between;gap:8px"><b style="font-weight:500">'+f.t+'</b><span class="tag" style="color:'+SC[f.sev]+';border:1px solid currentColor">'+SV[f.sev]+'</span></div>'+
'<p class="mut"><code>'+s0.f+':'+s0.l+'</code> · '+ts.length+' تست شکسته</p><p>'+f.fx+'</p></div>';
}).join('');

$('chips').innerHTML=S.map(function(s){var g=s.t!='angel';return '<button class="ch '+(g?'gh':'an')+'" data-i="'+s.id+'" onclick="show('+s.id+')"><span class="dot" style="width:9px;height:9px;background:'+(g?'var(--red)':'var(--grn)')+'"></span>'+(g?'روح · ':'فرشته · ')+s.n.replace(/^test_/,'').slice(0,18)+'</button>'}).join('');
show(S[0].id);

try{
var el=$('stage'),W=el.clientWidth,H=el.clientHeight||300,RM=matchMedia('(prefers-reduced-motion: reduce)').matches,AM=RM?.25:1;
var scene=new THREE.Scene(),cam=new THREE.PerspectiveCamera(45,W/H,.1,100);
var r=new THREE.WebGLRenderer({antialias:true,alpha:true});r.setSize(W,H);r.setPixelRatio(Math.min(devicePixelRatio,2));el.appendChild(r.domElement);
scene.add(new THREE.AmbientLight(0xffffff,.65));
var dl=new THREE.DirectionalLight(0xffffff,.85);dl.position.set(3,6,5);scene.add(dl);
var pl=new THREE.PointLight(0x8f6bff,.9,14);pl.position.set(0,2.5,0);scene.add(pl);
var fl=new THREE.Mesh(new THREE.CircleGeometry(4.5,48),new THREE.MeshBasicMaterial({color:0x1d2038}));fl.rotation.x=-Math.PI/2;fl.position.y=-.76;scene.add(fl);
var rg=new THREE.Mesh(new THREE.TorusGeometry(4.5,.03,8,72),new THREE.MeshBasicMaterial({color:0x6d4fd8}));rg.rotation.x=Math.PI/2;rg.position.y=-.75;scene.add(rg);

var N=70,pg=new THREE.BufferGeometry(),pa=new Float32Array(N*3),pv=[];
for(var i=0;i<N;i++){var a0=Math.random()*6.28,rr=.8+Math.random()*3.8;pa[i*3]=Math.cos(a0)*rr;pa[i*3+1]=Math.random()*4-.7;pa[i*3+2]=Math.sin(a0)*rr;pv.push(.15+Math.random()*.3)}
pg.setAttribute('position',new THREE.BufferAttribute(pa,3));
scene.add(new THREE.Points(pg,new THREE.PointsMaterial({color:0xffe9a8,size:.08,transparent:true,opacity:.75})));

var SP=new THREE.SplineCurve([[.9,-.7],[.86,-.45],[.74,-.1],[.62,.22],[.55,.45],[.52,.7],[.4,.92],[.2,1.02],[.001,1.05]].map(function(q){return new THREE.Vector2(q[0],q[1])})).getPoints(30).map(function(v){return new THREE.Vector2(Math.max(v.x,.001),v.y)});
var NP=SP.length;
var eyeG=new THREE.SphereGeometry(.085,14,12),hiG=new THREE.SphereGeometry(.03,8,8),armG=new THREE.SphereGeometry(.12,12,10),wingG=new THREE.SphereGeometry(.5,16,12);
var dark=new THREE.MeshBasicMaterial({color:0x23233a}),white=new THREE.MeshBasicMaterial({color:0xffffff}),pink=new THREE.MeshBasicMaterial({color:0xff9db1,transparent:true,opacity:.6});
function mat(c,o){return new THREE.MeshPhongMaterial({color:c,emissive:c,emissiveIntensity:.18,transparent:o<1,opacity:o,side:THREE.DoubleSide,shininess:70})}
function spr(t,col){var c=document.createElement('canvas');c.width=c.height=64;var x=c.getContext('2d');x.font='bold 44px sans-serif';x.fillStyle=col;x.textAlign='center';x.textBaseline='middle';x.fillText(t,32,34);
var m=new THREE.Sprite(new THREE.SpriteMaterial({map:new THREE.CanvasTexture(c),transparent:true}));m.scale.set(.7,.7,1);m.position.y=1.65;return m}

function mk(s){
var g=new THREE.Group(),t=s.t,col=TY[t][1],isA=t=='angel',op=t=='null'?.45:t=='flaky'?.65:1,m=mat(col,op),ha=null;
var bg=new THREE.LatheGeometry(SP,32);g.add(new THREE.Mesh(bg,m));
var f=new THREE.Group(),eyes=[],arms=[],wings=[];g.add(f);
function eye(x,sy){var e=new THREE.Group(),b=new THREE.Mesh(eyeG,dark);b.scale.set(.8,sy||1.25,.5);var h=new THREE.Mesh(hiG,white);h.position.set(.03,.06,.05);e.add(b,h);e.position.set(x,.46,.5);f.add(e);eyes.push(e)}
function arc(x,y,z,rz,rad){var a=new THREE.Mesh(new THREE.TorusGeometry(rad,.025,8,14,Math.PI),dark);a.position.set(x,y,z);a.rotation.z=rz;f.add(a)}
function ring(x,rad){var a=new THREE.Mesh(new THREE.TorusGeometry(rad,.025,8,16),dark);a.position.set(x,.46,.52);f.add(a)}
function mouth(sx,sy){var q=new THREE.Mesh(new THREE.SphereGeometry(.06,10,8),dark);q.scale.set(sx,sy,.4);q.position.set(0,.25,.58);f.add(q)}
function brow(x,rz){var b=new THREE.Mesh(new THREE.BoxGeometry(.17,.03,.03),dark);b.position.set(x,.64,.52);b.rotation.z=rz;f.add(b)}
if(isA){arc(-.2,.44,.52,0,.09);arc(.2,.44,.52,0,.09);arc(0,.3,.58,Math.PI,.09)}
else if(t=='timeout'){arc(-.2,.5,.52,Math.PI,.09);arc(.2,.5,.52,Math.PI,.09);mouth(1.3,1.7)}
else if(t=='null'){ring(-.2,.09);ring(.2,.09);mouth(1,1.3)}
else if(t=='issue'){[-.2,.2].forEach(function(x){[.8,-.8].forEach(function(rz){var b=new THREE.Mesh(new THREE.BoxGeometry(.2,.035,.03),dark);b.position.set(x,.46,.52);b.rotation.z=rz;f.add(b)})});mouth(1.4,.5)}
else if(t=='assert'){eye(-.2);eye(.2);brow(-.2,-.35);brow(.2,.35);mouth(1.6,.35);var mo=new THREE.Mesh(new THREE.TorusGeometry(.14,.02,8,24),dark);mo.position.set(.2,.46,.54);f.add(mo)}
else{eye(-.2,1.5);eye(.2,.8);mouth(1,1)}
if(t!='null')[-1,1].forEach(function(sx){var c=new THREE.Mesh(new THREE.CircleGeometry(.07,16),pink);c.position.set(sx*.33,.32,.5);c.rotation.y=sx*.6;f.add(c)});
if(t=='null')g.add(spr('?','#c9ccdf'));if(t=='timeout')g.add(spr('zZ','#f2d48a'));if(t=='flaky')g.add(spr('~','#c3a6f0'));if(t=='issue')g.add(spr('!','#f5a3a3'));
[-1,1].forEach(function(sx){var sh=new THREE.Group(),a=new THREE.Mesh(armG,m);a.scale.set(1,2.2,1);a.position.y=-.22;sh.add(a);sh.position.set(sx*.62,.05,0);sh.userData.sx=sx;g.add(sh);arms.push(sh)});
if(isA){ha=new THREE.Mesh(new THREE.TorusGeometry(.35,.05,10,32),new THREE.MeshBasicMaterial({color:0xffd166}));ha.rotation.x=Math.PI/2;ha.position.y=1.35;g.add(ha);
[-1,1].forEach(function(sx){var wg=new THREE.Group(),w=new THREE.Mesh(wingG,mat(0xffffff,1));w.scale.set(.15,.8,.5);w.position.x=sx*.4;wg.add(w);wg.position.set(sx*.3,.4,-.3);wg.userData.sx=sx;g.add(wg);wings.push(wg)})}
g.userData.id=s.id;
var ar=bg.attributes.position.array;
return {g:g,s:s,m:m,bg:bg,eyes:eyes,arms:arms,wings:wings,halo:ha,y0:ar[1],y1:ar[NP*0+4],ph:Math.random()*6.28};
}
function wave(p,t){var pos=p.bg.attributes.position,a=pos.array;for(var i=0;i<=32;i++){var k=Math.sin(i/32*Math.PI*10+t*3+p.ph)*.1*AM;a[i*NP*3+1]=p.y0+k;a[(i*NP+1)*3+1]=p.y1+k*.4}pos.needsUpdate=true}

var R=new THREE.Group();scene.add(R);
var sp=S.map(function(s,i){
var p=mk(s);p.ang=i/S.length*Math.PI*2;p.base=s.t=='angel'?1.2:.15;p.k=1;
var gx=Math.sin(p.ang)*3,gz=Math.cos(p.ang)*3;p.g.position.x=gx;p.g.position.z=gz;R.add(p.g);
var dc=new THREE.Mesh(new THREE.CircleGeometry(.75,28),new THREE.MeshBasicMaterial({color:s.t=='angel'?0x3ddc84:0xff5a4d,transparent:true,opacity:.4}));dc.rotation.x=-Math.PI/2;dc.position.set(gx,-.73,gz);R.add(dc);p.dc=dc;return p});

var cv=r.domElement,ray=new THREE.Raycaster(),mv=new THREE.Vector2(),down=null,moved=0;
cv.style.touchAction='pan-y';
cv.addEventListener('pointerdown',function(e){down=e.clientX;moved=0;try{cv.setPointerCapture(e.pointerId)}catch(x){}});
cv.addEventListener('pointermove',function(e){if(down===null)return;var dx=e.clientX-down;down=e.clientX;moved+=Math.abs(dx);R.rotation.y+=dx*.01;follow=false});
cv.addEventListener('pointercancel',function(){down=null});
cv.addEventListener('pointerup',function(e){
down=null;if(moved>6)return;
var b=cv.getBoundingClientRect();mv.set((e.clientX-b.left)/b.width*2-1,-((e.clientY-b.top)/b.height)*2+1);
ray.setFromCamera(mv,cam);var hs=ray.intersectObjects(R.children,true);
if(hs.length){var o=hs[0].object;while(o&&!(o.userData&&o.userData.id))o=o.parent;if(o)show(o.userData.id)}
});
window.addEventListener('resize',function(){var w=el.clientWidth,h=el.clientHeight;r.setSize(w,h);cam.aspect=w/h;cam.updateProjectionMatrix()});

var last=performance.now()/1000,T0=last;
(function loop(){
var t=performance.now()/1000,dt=Math.min(.05,t-last);last=t;
cam.position.set(0,2.8+Math.sin(t*.5)*.1*AM,9.2);cam.lookAt(0,.6,0);
if(follow){var c0=sp.find(function(p){return p.s.id==cur});var d=((-c0.ang-R.rotation.y+Math.PI)%(2*Math.PI)+2*Math.PI)%(2*Math.PI)-Math.PI;R.rotation.y+=d*.08}
sp.forEach(function(p,i){
var sel=p.s.id==cur,e=Math.min(1,Math.max(0,(t-T0-i*.12)/.7)),x=e-1,ease=1+2.7*x*x*x+1.7*x*x;
p.k+=((sel?1.28:1)-p.k)*.12;
p.g.position.y=p.base+Math.sin(t*1.6+p.ph)*.1*AM+(sel?Math.abs(Math.sin(t*3))*.14*AM:0)-(1-e)*2;
p.g.rotation.y=-R.rotation.y;p.g.rotation.z=Math.sin(t*1.2+p.ph)*.07*AM;
p.g.scale.setScalar(Math.max(.001,p.k*ease));
wave(p,t);
p.arms.forEach(function(a,j){a.rotation.z=a.userData.sx*(.65+.4*AM*Math.sin(t*2.6+p.ph+j))});
p.wings.forEach(function(w){w.rotation.y=w.userData.sx*(.55+.35*AM*Math.sin(t*5+p.ph))});
if(p.halo)p.halo.scale.setScalar(1+.06*Math.sin(t*3+p.ph));
var bl=((t+p.ph)%4)<.12?.1:1;p.eyes.forEach(function(e2){e2.scale.y=bl});
p.dc.material.opacity=sel?.85:.4;p.dc.scale.setScalar(sel?1+.12*Math.sin(t*4):1);
if(p.s.t=='flaky')p.m.opacity=.3+.4*Math.abs(Math.sin(t*3+p.ph));
});
for(var q=0;q<N;q++){pa[q*3+1]+=pv[q]*dt;if(pa[q*3+1]>3.6)pa[q*3+1]=-.7}
pg.attributes.position.needsUpdate=true;
r.render(scene,cam);requestAnimationFrame(loop);
})();
}catch(e){$('stage').innerHTML='<p style="color:#ccc;padding:16px">نمایش سه‌بعدی روی این دستگاه بالا نیومد.</p>'}

}
var q=new URLSearchParams(location.search).get('repo');
if(q)$('url').value=q;
fetch('api/scan'+(q?'?repo='+encodeURIComponent(q):'')).then(function(r){return r.json()}).then(function(d){
if(d&&d.S&&d.S.length){S=d.S;F=d.F;T=d.T;META=d.meta;DEPS=d.deps||{};document.dispatchEvent(new CustomEvent('scan',{detail:d}));if(d.meta.url){$('url').value=d.meta.url;$('gh').href=d.meta.url}$('src').innerHTML='<span class="badge" style="background:var(--gb);color:var(--grn)">داده‌ی واقعی</span> '+d.meta.name}
else if(d&&d.error){$('src').innerHTML='<span class="badge" style="background:var(--rb);color:var(--red)">پیام</span> '+d.error+' (داده‌ی نمایشی)'}
}).catch(function(){}).then(init);
$('scan').addEventListener('click',function(e){e.preventDefault();location.href='?repo='+encodeURIComponent($('url').value.trim())});
$('url').addEventListener('input',function(e){var v=e.target.value.trim();$('gh').href=/^https?:\/\//.test(v)?v:'https://'+v});
