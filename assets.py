"""대시보드 화면(CSS·JS). build.py 가 읽는다."""

CSS = """
:root{--bg:#f5f6f8;--card:#fff;--ink:#1b2130;--mute:#667085;--line:#e4e7ec;--ok:#15803d;--okbg:#dcfce7;--wait:#b45309;--waitbg:#fef3c7;
--bad:#b91c1c;--badbg:#fee2e2;--acc:#2563eb;--accbg:#dbeafe;--today:#fff7ed;--ig:#c026d3;--tt:#0f766e;--pt:#fff}
@media(prefers-color-scheme:dark){:root{--bg:#0f1218;--card:#171b24;--ink:#e6e8ee;--mute:#9aa3b2;--line:#2a3140;--ok:#4ade80;--okbg:#14301f;
--wait:#fbbf24;--waitbg:#3a2a0a;--bad:#f87171;--badbg:#3a1414;--acc:#60a5fa;--accbg:#172554;--today:#2a1f12;--ig:#e879f9;--tt:#2dd4bf;--pt:#0b1220}}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font:14px/1.55 "Malgun Gothic","Apple SD Gothic Neo",Pretendard,system-ui,sans-serif}
.top{position:sticky;top:0;z-index:5;background:var(--card);border-bottom:1px solid var(--line)}
.topin{max-width:1180px;margin:0 auto;padding:10px 16px 0;display:flex;flex-wrap:wrap;align-items:flex-end;gap:0 18px}
.top h1{font-size:17px;margin:0 0 6px}.top .gen{color:var(--mute);font-size:12px;margin:0 0 7px auto}
.tabs{display:flex;gap:4px;width:100%;overflow-x:auto}
.tab{border:0;background:none;color:var(--mute);font:inherit;font-size:15px;font-weight:700;padding:9px 16px;border-bottom:3px solid transparent;cursor:pointer;white-space:nowrap}
.tab.on{color:var(--acc);border-bottom-color:var(--acc)}
.tab .c{font-size:11px;font-weight:600;background:var(--accbg);color:var(--acc);border-radius:9px;padding:1px 7px;margin-left:6px}
.tab .c.z{background:var(--line);color:var(--mute)}
.wrap{max-width:1180px;margin:0 auto;padding:16px}
.pane{display:none}.pane.on{display:block}
.hero h2{font-size:22px;margin:4px 0 2px}.sub{color:var(--mute);font-size:13px}
h3.sec{font-size:16px;margin:26px 0 8px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:10px;margin:14px 0}
.tile{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px}
.tile .n{font-size:22px;font-weight:700}.tile .l{color:var(--mute);font-size:12px}
.box{background:var(--card);border:1px solid var(--line);border-radius:10px;padding:12px 14px;margin:10px 0}
.box.warn{border-color:#f59e0b88;background:var(--today)}.scroll{overflow-x:auto}
.how{margin:6px 0 0 18px;padding:0}.how li{margin:3px 0}
.day{background:var(--card);border:1px solid var(--line);border-radius:12px;margin:12px 0;overflow:hidden}
.day.today{border-color:#f59e0b;box-shadow:0 0 0 2px #f59e0b44}.wk .day.past{opacity:.7}
.dh{display:flex;flex-wrap:wrap;gap:6px 10px;align-items:center;padding:10px 14px}
.dh .d{font-weight:700;font-size:17px}.dh .k{color:var(--mute);font-size:12px}.dh .da{margin-left:auto;display:flex;flex-wrap:wrap;gap:6px}
.path{font:12px/1.4 Consolas,"D2Coding",monospace;color:var(--mute);word-break:break-all;padding:6px 14px;background:var(--bg);
border-top:1px solid var(--line);border-bottom:1px solid var(--line)}
.slots{display:grid;grid-template-columns:repeat(auto-fill,minmax(320px,1fr));gap:10px;padding:12px}
.slot{display:flex;gap:10px;border:1px solid var(--line);border-radius:10px;padding:10px;background:var(--bg);min-width:0}
.th{width:66px;height:117px;object-fit:cover;border-radius:7px;flex:none;background:var(--line)}
.th.none{display:flex;align-items:center;justify-content:center;text-align:center;font-size:10px;color:var(--mute);padding:4px}
.sb{min-width:0;flex:1}.s1{display:flex;flex-wrap:wrap;gap:5px;align-items:center}
.tm{font-size:17px;font-weight:700}.pl{font-size:12px;font-weight:700}.pl.ig{color:var(--ig)}.pl.tt{color:var(--tt)}
.ti{font-weight:700;margin-top:2px;overflow-wrap:anywhere}
.fn{font:11.5px/1.45 Consolas,monospace;color:var(--mute);margin-top:3px;overflow-wrap:anywhere}
.note{font-size:12px;color:var(--wait);margin-top:3px}.kpi{font-size:12px;margin-top:4px}
.act{display:flex;flex-wrap:wrap;gap:6px;margin-top:7px}
.btn{display:inline-block;border:1px solid var(--line);background:var(--card);color:var(--ink);border-radius:7px;padding:5px 10px;
font:inherit;font-size:12px;text-decoration:none;cursor:pointer;white-space:nowrap}
.btn.p{background:var(--acc);border-color:var(--acc);color:var(--pt)}.btn:hover{filter:brightness(.95)}
.tag{display:inline-block;border-radius:6px;padding:1px 7px;font-size:11.5px;font-weight:700;white-space:nowrap}
.ok{background:var(--okbg);color:var(--ok)}.wait{background:var(--waitbg);color:var(--wait)}
.bad{background:var(--badbg);color:var(--bad)}.acc{background:var(--accbg);color:var(--acc)}
.late:not(:empty){background:var(--badbg);color:var(--bad);border-radius:6px;padding:1px 7px;font-size:11.5px;font-weight:700}
.capd{margin-top:6px}.capd summary,.wk>summary{cursor:pointer}.capd summary{color:var(--acc);font-size:12px}
pre.cap{white-space:pre-wrap;overflow-wrap:anywhere;margin:6px 0 0;padding:8px;border:1px dashed var(--line);border-radius:6px;
font:12px/1.5 inherit;background:var(--card)}
pre.cap .mk{color:var(--mute);font-style:italic}
.wk{margin:6px 0}.wk>summary{font-size:15px;font-weight:700;padding:10px 14px;background:var(--card);border:1px solid var(--line);border-radius:10px}
table{width:100%;border-collapse:collapse;font-size:13px}
th,td{padding:6px 8px;border-top:1px solid var(--line);text-align:left;vertical-align:top}
tr:first-child>th,tr:first-child>td{border-top:0}th{color:var(--mute);font-weight:600;font-size:12px}
.mono{font:12px Consolas,monospace;word-break:break-all}.nw{white-space:nowrap}
code{font:12px Consolas,monospace;background:var(--bg);padding:1px 4px;border-radius:4px}
a{color:var(--acc)}.empty{color:var(--mute);padding:14px;background:var(--card);border:1px dashed var(--line);border-radius:10px}
.toast{position:fixed;bottom:18px;left:50%;transform:translateX(-50%);background:#111;color:#fff;padding:8px 14px;border-radius:8px;
font-size:13px;opacity:0;transition:.2s;pointer-events:none;max-width:90vw;z-index:9}
.toast.on{opacity:1}body.web .local{display:none}
@media(max-width:640px){.slots{grid-template-columns:1fr;padding:10px}.dh .da{margin-left:0;width:100%}.tab{padding:9px 12px}}
"""

JS = r"""
(function(){
if(location.protocol!=='file:')document.body.classList.add('web');
function toast(m){const x=document.getElementById('toast');x.textContent=m;x.classList.add('on');setTimeout(()=>x.classList.remove('on'),1800)}
function fb(t,m){const ta=document.createElement('textarea');ta.value=t;document.body.appendChild(ta);ta.select();
 try{document.execCommand('copy');toast(m)}catch(e){prompt('복사하세요',t)}ta.remove()}
document.addEventListener('click',ev=>{const b=ev.target.closest('[data-cp]');if(!b)return;const t=b.dataset.cp,m=b.dataset.msg||('복사됨: '+t);
 if(navigator.clipboard&&navigator.clipboard.writeText)navigator.clipboard.writeText(t).then(()=>toast(m),()=>fb(t,m));else fb(t,m)});
const now=new Date(),p=n=>String(n).padStart(2,'0'),ymd=now.getFullYear()+'-'+p(now.getMonth()+1)+'-'+p(now.getDate()),
 hm=ymd+'T'+p(now.getHours())+':'+p(now.getMinutes());
document.querySelectorAll('.slot').forEach(s=>{if(s.dataset.track==='1'&&s.dataset.url==='0'&&s.dataset.dt&&s.dataset.dt<hm)
 s.querySelector('.late').textContent='시각 지남 · URL 미기록'});
document.querySelectorAll('.pane').forEach(pane=>{const days=[...pane.querySelectorAll('.day')];let n=0;
 days.forEach(el=>{const x=el.dataset.date;if(x===ymd)el.classList.add('today');else if(x<ymd)el.classList.add('past')});
 const box=pane.querySelector('.todaybox'),t=days.find(el=>el.dataset.date===ymd),nx=days.find(el=>el.dataset.date>ymd);
 if(box){if(t){box.appendChild(t.cloneNode(true));n=t.querySelectorAll('.slot').length}
  else box.innerHTML='<div class="empty">오늘('+ymd+')은 올릴 것이 없습니다.'+(nx?' 다음 일정: '+nx.dataset.date:'')+'</div>';
  if(nx){const h=document.createElement('h3');h.className='sec';h.textContent=(t?'다음 날 미리 보기':'다음 일정');box.appendChild(h);
   const c=nx.cloneNode(true);c.classList.add('next');box.appendChild(c)}}
 const c=document.querySelector('.tab[data-t="'+pane.id+'"] .c');if(c){c.textContent='오늘 '+n;if(!n)c.classList.add('z')}});
function show(id){if(!document.getElementById(id))id=document.body.dataset.default||'park';
 document.querySelectorAll('.pane').forEach(x=>x.classList.toggle('on',x.id===id));
 document.querySelectorAll('.tab').forEach(x=>x.classList.toggle('on',x.dataset.t===id));
 try{history.replaceState(null,'','#'+id)}catch(e){}}
document.querySelectorAll('.tab').forEach(b=>b.addEventListener('click',()=>{show(b.dataset.t);window.scrollTo(0,0)}));
show((location.hash||'').slice(1)||document.body.dataset.default||'park');
})();
"""
