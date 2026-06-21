#!/usr/bin/env python3
"""3과제 모니터링 대시보드 (Flask · 다크 UI).
데이터 수집은 monitor.py 함수를 재사용. 시간창 1/5/10/15/20/25/30분 선택 + 자동 갱신.

설치:  pip3 install flask   (CloudShell: pip3 install --user flask)
실행:  python3 dashboard.py --namespace app --waf-log-group aws-waf-logs-wsi2026b
       → http://<host>:8080
"""
import argparse
from flask import Flask, jsonify, request, Response
import monitor  # 같은 폴더의 monitor.py (수집/진단 로직 재사용)

app = Flask(__name__)

PAGE = r"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><title>3과제 모니터링</title>
<style>
:root{--bg:#ffffff;--bg2:#f5f6f8;--card:#ffffff;--card2:#f7f8fa;--line:#e3e6ea;--mut:#6b7280;--txt:#1a1d23;--ac:#2563eb;--gd:#15803d;--wn:#b45309;--bd:#dc2626}
*{box-sizing:border-box}html,body{margin:0}
body{background:radial-gradient(1200px 600px at 70% -10%,#eef3fb 0,var(--bg) 60%);color:var(--txt);font-family:'Segoe UI','Malgun Gothic',sans-serif;font-size:14px;min-height:100vh}
header{position:sticky;top:0;z-index:20;display:flex;align-items:center;gap:18px;padding:14px 26px;background:rgba(255,255,255,.85);backdrop-filter:blur(10px);border-bottom:1px solid var(--line)}
header h1{font-size:15px;font-weight:700;margin:0;letter-spacing:.5px;display:flex;align-items:center;gap:9px}
header h1::before{content:"";width:9px;height:9px;border-radius:50%;background:var(--gd)}
.ctl{display:flex;align-items:center;gap:7px;color:var(--mut);font-size:12.5px}
select,button{background:var(--card2);color:var(--txt);border:1px solid var(--line);border-radius:9px;padding:7px 12px;font-size:13px;cursor:pointer;outline:none}
input[type=number]{background:var(--card2);color:var(--txt);border:1px solid var(--line);border-radius:7px;padding:5px 7px;font-size:12.5px;width:72px;outline:none}
.calc th,.calc td{padding:6px 8px;white-space:nowrap}.calc input{width:66px}
select:hover,button:hover{border-color:var(--ac)}
#st{margin-left:auto;font-size:12px;color:var(--mut);display:flex;align-items:center;gap:7px}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block}
nav{display:flex;gap:3px;padding:14px 26px 0;flex-wrap:wrap}
.tab{padding:9px 17px;border-radius:11px 11px 0 0;color:var(--mut);cursor:pointer;border:1px solid transparent;font-size:13px;font-weight:500;transition:.15s}
.tab:hover{color:var(--txt)}
.tab.on{background:var(--card);border-color:var(--line);border-bottom-color:var(--card);color:var(--txt)}
main{padding:18px 26px 60px}
.grid{display:grid;gap:15px}.g2{grid-template-columns:repeat(auto-fit,minmax(420px,1fr))}.g3{grid-template-columns:repeat(auto-fit,minmax(290px,1fr))}.g4{grid-template-columns:repeat(auto-fit,minmax(195px,1fr))}
.card{background:linear-gradient(180deg,var(--card),var(--card2));border:1px solid var(--line);border-radius:16px;padding:17px;box-shadow:0 1px 0 rgba(255,255,255,.02) inset}
.card h2{margin:0 0 13px;font-size:13.5px;font-weight:600;color:#374151;display:flex;justify-content:space-between}
.lbl{font-size:10.5px;color:var(--mut);text-transform:uppercase;letter-spacing:1px;margin-bottom:7px}
.kpi{font-size:32px;font-weight:800;line-height:1;font-variant-numeric:tabular-nums}.kpi.sm{font-size:21px}
.row{display:flex;justify-content:space-between;padding:6px 0;border-bottom:1px solid var(--line);font-size:13px}.row:last-child{border:0}
.gd{color:var(--gd)}.wn{color:var(--wn)}.bd{color:var(--bd)}.mut{color:var(--mut)}
.bar{height:7px;background:#f6f7f9;border-radius:6px;overflow:hidden;margin:9px 0}.bar>div{height:100%;border-radius:6px;transition:width .5s}
table{width:100%;border-collapse:collapse;font-size:12.5px}th,td{text-align:left;padding:6px 9px;border-bottom:1px solid var(--line)}
th{color:var(--mut);font-size:10.5px;text-transform:uppercase;letter-spacing:.5px}td.n{text-align:right;font-variant-numeric:tabular-nums;color:var(--mut)}
.pill{padding:2px 9px;border-radius:20px;font-size:11px;font-weight:700}.p2{background:rgba(61,220,151,.14);color:var(--gd)}.p4{background:rgba(255,207,92,.14);color:var(--wn)}.p5{background:rgba(255,92,122,.14);color:var(--bd)}
.box{background:#f6f7f9;border:1px solid var(--line);border-radius:12px;max-height:360px;overflow:auto}
.tip{border-left:3px solid;border-radius:12px;padding:13px 16px;background:var(--card);margin-bottom:11px}
.tip.bad{border-color:var(--bd)}.tip.warn{border-color:var(--wn)}.tip.good{border-color:var(--gd)}.tip.dim{border-color:#33415c}
.tip h3{margin:0 0 6px;font-size:13.5px}.tip .why{color:#374151;font-size:13px;white-space:pre-wrap}
.tip pre{margin:8px 0 0;background:#f6f7f9;border:1px solid var(--line);border-radius:9px;padding:10px 12px;font-size:12px;white-space:pre-wrap;color:#1d4ed8;overflow-x:auto}
details.det{border-bottom:1px solid var(--line)}
details.det:last-child{border-bottom:0}
details.det>summary{padding:9px 13px;cursor:pointer;list-style:none;font-size:12.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
details.det>summary::-webkit-details-marker{display:none}
details.det>summary:hover{background:#eef1f5}
details.det[open]>summary{background:#eef1f5}
.kv{display:grid;grid-template-columns:120px 1fr;gap:6px 16px;padding:12px 15px;border-top:1px solid var(--line);background:#f6f7f9;font-size:13px;line-height:1.5}
.kk{color:var(--mut)}
.vv{color:#1a1d23;white-space:pre-wrap;word-break:break-all}
.rsn{color:var(--wn);font-size:11.5px;margin-left:4px}
</style></head><body>
<header><h1>3과제 모니터링</h1>
<span class="ctl">시간창
<select id="since">
<option value="1m">1분</option><option value="5m">5분</option><option value="10m">10분</option>
<option value="15m" selected>15분</option><option value="20m">20분</option><option value="25m">25분</option><option value="30m">30분</option>
</select></span>
<span class="ctl">자동
<select id="auto"><option value="0">수동</option><option value="5">5s</option><option value="10" selected>10s</option><option value="30">30s</option><option value="60">60s</option></select></span>
<button onclick="load()">새로고침</button>
<span id="st"></span></header>
<nav id="tabs"></nav><main id="view"></main><script>
var D=null,TAB='overview';
function cr(v,g,w){return v>=g?'gd':v>=w?'wn':'bd'}
function stp(s){s=''+s;var c=s[0]==='2'?'p2':s[0]==='4'?'p4':'p5';return '<span class="pill '+c+'">'+s+'</span>'}
function esc(s){return (''+s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;')}
function kv(pairs){return '<div class=kv>'+pairs.filter(function(p){return p[1]!==undefined&&p[1]!==null&&p[1]!==''&&p[1]!=='-'}).map(function(p){return '<div class=kk>'+p[0]+'</div><div class=vv>'+esc(p[1])+'</div>'}).join('')+'</div>'}
function tbl(rows,cols){if(!rows||!rows.length)return '<div class=mut style="padding:9px">없음</div>';
 var h='<table><tr>'+cols.map(function(c){return '<th'+(c[2]?' style="text-align:right"':'')+'>'+c[0]+'</th>'}).join('')+'</tr>';
 return h+rows.map(function(r){return '<tr>'+cols.map(function(c){return '<td'+(c[2]?' class=n':'')+'>'+c[1](r)+'</td>'}).join('')+'</tr>'}).join('')+'</table>'}
function recTbl(rows){if(!rows||!rows.length)return '<div class=mut style="padding:9px">없음</div>';
 return '<div class=box>'+rows.map(function(r){var key=r.ts+'|'+r.m+'|'+r.path+'|'+r.st+'|'+r.ip;
  return '<details class=det data-k="'+esc(key)+'"><summary><span class=mut>'+r.ts+'</span> <b>'+r.m+'</b> '+esc(r.path)+' '+stp(r.st)
   +(r.why?' <span class=rsn>'+esc(r.why)+'</span>':'')+'<span class=mut style="float:right">'+r.dur+'ms</span></summary>'
   +kv([['시각',r.ts],['메서드',r.m],['경로',r.path],['상태',r.st],['사유',r.why],['requestid',r.requestid],['uuid',r.uuid],['지연(ms)',r.dur],['클라이언트 IP',r.ip]])
   +'</details>'}).join('')+'</div>'}
function appCard(a){var s=cr(a.slo_rate,90,70),o=cr(a.ok_rate,90,70);
 return '<div class=card><div class=lbl>'+a.app+'</div><div class="kpi '+s+'">'+a.slo_rate+'%<span class=mut style="font-size:12px;font-weight:400"> SLO≤'+a.slo_ms+'ms</span></div>'
 +'<div class=bar><div class="'+s+'" style="width:'+a.slo_rate+'%;background:currentColor"></div></div>'
 +'<div class=row><span>요청수</span><b>'+a.total+'</b></div>'
 +'<div class=row><span>2xx / 4xx / 5xx</span><span><span class=gd>'+a.c2+'</span> / <span class=wn>'+a.c4+'</span> / <span class=bd>'+a.c5+'</span></span></div>'
 +'<div class=row><span>성공률</span><span class="'+o+'">'+a.ok_rate+'%</span></div>'
 +'<div class=row><span>p50/p95/p99</span><span>'+a.p50+'/'+a.p95+'/'+a.p99+'ms</span></div></div>'}
function vOverview(){var s=D.summary;
 var k='<div class="grid g4">'
 +'<div class=card><div class=lbl>통과 allow</div><div class="kpi gd">'+s.allow+'</div></div>'
 +'<div class=card><div class=lbl>차단 block·403</div><div class="kpi bd">'+s.block+'</div></div>'
 +'<div class=card><div class=lbl>2xx / 4xx / 5xx</div><div class="kpi sm"><span class=gd>'+s.c2+'</span>/<span class=wn>'+s.c4+'</span>/<span class=bd>'+s.c5+'</span></div></div>'
 +'<div class=card><div class=lbl>Pod ready · 노드</div><div class="kpi sm">'+s.pods_ready+'/'+s.pods_total+' · '+s.nodes_total+'</div></div></div>';
 var cards='<div class="grid g3" style="margin-top:15px">'+D.apps.map(appCard).join('')+'</div>';
 var diag='<div class=lbl style="margin:22px 0 9px">진단 · 원인 & 해결</div>'+D.diag.map(function(t){return '<div class="tip '+t[0]+'"><h3>'+t[1]+'</h3><div class=why>'+t[2]+'</div>'+(t[3]?'<pre>'+t[3]+'</pre>':'')+'</div>'}).join('');
 return k+cards+diag}
function vApp(a){var s=cr(a.slo_rate,90,70),o=cr(a.ok_rate,90,70);
 var k='<div class="grid g4">'
 +'<div class=card><div class=lbl>SLO ≤'+a.slo_ms+'ms</div><div class="kpi '+s+'">'+a.slo_rate+'%</div></div>'
 +'<div class=card><div class=lbl>성공률 2xx</div><div class="kpi '+o+'">'+a.ok_rate+'%</div></div>'
 +'<div class=card><div class=lbl>요청수 (+hc)</div><div class="kpi sm">'+a.total+' <span class=mut style="font-size:13px">+'+a.hc+'</span></div></div>'
 +'<div class=card><div class=lbl>p99 / max</div><div class="kpi sm">'+a.p99+' / '+a.max+'ms</div></div></div>';
 var cnt='<div class="grid g3" style="margin-top:15px"><div class=card><div class=lbl>2xx</div><div class="kpi gd">'+a.c2+'</div></div>'
 +'<div class=card><div class=lbl>4xx</div><div class="kpi wn">'+a.c4+'</div></div>'
 +'<div class=card><div class=lbl>5xx</div><div class="kpi bd">'+a.c5+'</div></div></div>';
 var pth='<div class="grid g2" style="margin-top:15px"><div class=card><h2>경로별 요청</h2>'+tbl(a.paths,[['경로',function(r){return r[0]}],['건수',function(r){return r[1]},1]])+'</div>'
 +'<div class=card><h2>에러 경로 (4xx/5xx)</h2>'+tbl(a.err_paths,[['상태',function(r){return stp(r[0][1])}],['경로',function(r){return r[0][0]}],['건수',function(r){return r[1]},1]])+'</div></div>';
 var rec='<div class="grid g3" style="margin-top:15px">'
 +'<div class=card><h2 class=gd>최근 2xx</h2>'+recTbl(a.recent2)+'</div>'
 +'<div class=card><h2 class=wn>최근 4xx</h2>'+recTbl(a.recent4)+'</div>'
 +'<div class=card><h2 class=bd>최근 5xx</h2>'+recTbl(a.recent5)+'</div></div>';
 return k+cnt+pth+rec}
function vPods(){return '<div class=card><h2>Pod ('+D.pods.length+'개)</h2><div class=box>'+tbl(D.pods,[
 ['app',function(r){return r.app}],['Pod',function(r){return r.name}],
 ['상태',function(r){return (r.phase==='Running'&&r.ready)?'<span class="pill p2">Running</span>':'<span class="pill p5">'+r.phase+(r.ready?'':'/NotReady')+'</span>'}],
 ['재시작',function(r){return r.restarts},1],['CPU',function(r){return r.cpu},1],['MEM',function(r){return r.mem},1],
 ['노드',function(r){return (r.node||'-').split('.')[0]}],['사유',function(r){return r.reason?'<span class=bd>'+r.reason+'</span>':'-'}]])+'</div></div>'}
function vNodes(){return '<div class=card><h2>노드 ('+D.nodes.length+'대)</h2>'+tbl(D.nodes,[
 ['노드',function(r){return r.name.split('.')[0]}],
 ['타입',function(r){return r.type+(r.karpenter?' <span class="pill p2">karpenter</span>':' <span class="pill p4">base</span>')}],
 ['상태',function(r){return r.ready==='Ready'?'<span class=gd>Ready</span>':'<span class=bd>'+r.ready+'</span>'}],
 ['CPU',function(r){return r.cpu+' ('+r.cpu_pct+')'}],['MEM',function(r){return r.mem+' ('+r.mem_pct+')'}]])+'</div>'
 +'<div class=card style="margin-top:15px"><h2>HPA</h2>'+tbl(D.hpa,[['이름',function(r){return r.name}],['CPU 현재/목표',function(r){return r.cur+' / '+r.tgt}],['min/max',function(r){return r.min+' / '+r.max}],['replicas',function(r){return r.replicas},1]])+'</div>'}
function vWaf(){var w=D.waf;if(!w.enabled)return '<div class="tip dim"><h3>WAF 로깅이 켜져 있지 않음</h3><div class=why>CloudWatch 로그그룹이 없어 블락(403) 데이터를 못 가져옵니다.</div><pre>terraform waf.tf 에 로깅 추가 후 apply\n또는: --waf-log-group <실제그룹명> --waf-region ap-northeast-2</pre></div>';
 var k='<div class="grid g3"><div class=card><div class=lbl>차단 403</div><div class="kpi bd">'+w.total+'</div></div>'
 +'<div class=card><div class=lbl>통과 앱도달</div><div class="kpi gd">'+D.summary.allow+'</div></div>'
 +'<div class=card><h2>차단 메서드</h2>'+tbl(w.by_method,[['M',function(r){return r[0]}],['건수',function(r){return r[1]},1]])+'</div></div>';
 var t='<div class="grid g3" style="margin-top:15px"><div class=card><h2>차단 사유 (룰)</h2>'+tbl(w.by_reason||w.by_rule,[['사유',function(r){return r[0]}],['건수',function(r){return r[1]},1]])+'</div>'
 +'<div class=card><h2>차단 IP</h2>'+tbl(w.by_ip,[['IP',function(r){return r[0]}],['건수',function(r){return r[1]},1]])+'</div>'
 +'<div class=card><h2>차단 URI</h2>'+tbl(w.by_uri,[['URI',function(r){return r[0]}],['건수',function(r){return r[1]},1]])+'</div></div>';
 var rec=w.recent.map(function(r){var key=r.ts+'|'+(r.url||r.uri)+'|'+r.ip+'|'+r.reason;
  return '<details class=det data-k="'+esc(key)+'"><summary>'
  +'<span class=mut>'+r.ts+'</span> <b>'+r.m+'</b> '+esc(r.url||r.uri)
  +' <span class="pill p5">'+esc(r.reason)+'</span><span class=mut style="float:right">'+r.ip+(r.country&&r.country!=='?'?' · '+r.country:'')+'</span>'
  +'</summary>'+kv([['차단 사유',r.reason],['메서드',r.m],['요청 URL',r.url||r.uri],['국가',r.country],['IP',r.ip],['User-Agent',r.ua],['X-Forwarded-For',r.xff]])+'</details>'}).join('')
  || '<div class=mut style="padding:9px">차단 없음</div>';
 return k+t+'<div class=card style="margin-top:15px"><h2>최근 차단 — 누르면 요청 전문 · 왜 차단됐는지</h2><div class=box>'+rec+'</div></div>'}
function vDiag(){return D.diag.map(function(t){return '<div class="tip '+t[0]+'"><h3>'+t[1]+'</h3><div class=why>'+t[2]+'</div>'+(t[3]?'<pre>'+t[3]+'</pre>':'')+'</div>'}).join('')}

// ---- 계산 탭: 라이브 데이터로 자동 판정 (줄여/늘려/유지) ----
function cpuM(s){if(s===undefined||s===null||s==='')return 0;s=''+s;return s.slice(-1)==='m'?parseInt(s):Math.round(parseFloat(s)*1000)}
function pctn(s){var n=parseInt((''+(s||'')).replace('%',''));return isNaN(n)?null:n}
function hpaOf(n){return (D.hpa||[]).find(function(h){return h.name===n})||{}}
function vCalc(){
 var apps=D.apps||[];var ALLOC=1900;var sMin=0,sMax=0,sMinCpu=0;
 var cards=apps.map(function(a){
  var n=a.app,h=hpaOf(n);
  var cpu=cpuM(a.cpu_req),util=pctn(h.tgt)||55,mn=+h.min||0,mx=+h.max||0,rep=+h.replicas||mn,cur=pctn(h.cur);
  var perf=a.slo_rate,avail=a.ok_rate,p95=a.p95,slo=a.slo_ms;
  var dir,cls,rcpu=cpu,rutil=util,rmn=mn,note;
  if(a.total===0){dir='관측 필요';cls='mut';note='요청이 없어 판단 불가 — loadtest로 부하를 준 뒤 보세요.';}
  else if(avail<99){dir='늘려 ↑';cls='bd';rcpu=Math.round(cpu*1.5/50)*50;rmn=mn+1;rutil=Math.max(40,util-5);note='가용성 '+avail+'% (<99) → cpu·min 늘려 (게이트 최우선)';}
  else if(perf<95||(slo&&p95>slo)){dir='늘려 ↑';cls='wn';rcpu=Math.round(cpu*1.4/50)*50;rutil=Math.max(40,util-10);note='성능 '+perf+'% / p95 '+p95+'ms > SLO '+slo+'ms (꼬리지연) → cpu 늘리고 util 낮춰(빨리 스케일)';}
  else if(perf>=99.5&&((cur!==null&&cur<Math.max(15,util*0.4))||(cur===null&&slo&&p95<=slo*0.4))){dir='줄여 ↓';cls='gd';rcpu=Math.max(100,Math.round(cpu*0.75/50)*50);rutil=Math.min(75,util+10);if(mn>2)rmn=mn-1;note='성능 '+perf+'% 여유 + 현재CPU '+(cur===null?'낮음':cur+'%')+' ≪ 목표 '+util+'% → cpu·util'+(mn>2?'·min':'')+' 줄여 비용↓ (과투자)';}
  else{dir='유지';cls='mut';note='균형 (perf '+perf+'%, 현재CPU '+(cur===null?'-':cur+'%')+'/목표'+util+'%)';}
  rmn=Math.max(1,rmn);sMin+=rmn;sMax+=mx;sMinCpu+=rmn*rcpu;
  var ch=[];
  if(rcpu!==cpu)ch.push('requests.cpu <b>'+cpu+'m → '+rcpu+'m</b> '+(rcpu>cpu?'↑':'↓')+' <span class=mut>('+(rcpu>cpu?'파드 1개를 더 세게 → 꼬리지연↓ (노드↑)':'파드당 cpu 낮춰 → 노드↓ (비용↓)')+')</span>');
  if(rutil!==util)ch.push('HPA averageUtilization <b>'+util+'% → '+rutil+'%</b> '+(rutil>util?'↑':'↓')+' <span class=mut>('+(rutil>util?'느긋하게 스케일 → 비용↓':'더 빨리·자주 파드 늘림 → 성능↑')+')</span>');
  if(rmn!==mn)ch.push('min_replicas <b>'+mn+' → '+rmn+'</b> '+(rmn>mn?'↑':'↓')+' <span class=mut>('+(rmn>mn?'부하 초반부터 여유 → 가용성↑':'유휴 파드 줄여 → 비용↓')+')</span>');
  var how=ch.length?ch.map(function(x){return '<div style="padding:3px 0">• '+x+'</div>'}).join(''):'<div class=mut>변경 없음 — 현상 유지</div>';
  var cmds='';
  if(ch.length){
   var patch=JSON.stringify({spec:{minReplicas:rmn,maxReplicas:mx,metrics:[{type:"Resource",resource:{name:"cpu",target:{type:"Utilization",averageUtilization:rutil}}}]}});
   var c='kubectl -n app set resources deploy/'+n+' --requests=cpu='+rcpu+'m\n'
    +'kubectl -n app patch hpa '+n+' --type=merge -p \''+patch+'\'\n'
    +'kubectl -n app rollout status deploy/'+n;
   cmds='<div class=lbl style="margin-top:9px;margin-bottom:4px">즉시 적용 명령 (임시 · 재배포 시 사라짐)</div>'
    +'<pre style="margin:0;background:#f6f7f9;border:1px solid var(--line);border-radius:8px;padding:9px 11px;font-size:11.5px;white-space:pre-wrap;color:#1a1d23;overflow-x:auto">'+esc(c)+'</pre>';
  }
  return '<div class=card><div class=lbl>'+n+' &nbsp;<span class='+cls+' style="font-weight:700">'+dir+'</span></div>'
   +'<div class=row><span class=mut>현재</span><span>cpu <b>'+cpu+'m</b> · util '+util+'% · min '+mn+' · max '+mx+' · 파드 '+rep+'</span></div>'
   +'<div class=row><span class=mut>측정</span><span>perf '+perf+'% · avail '+avail+'% · p95 '+p95+'ms · 현재CPU '+(cur===null?'-':cur+'%')+'</span></div>'
   +'<div style="margin-top:9px"><div class=lbl style="margin-bottom:4px">이렇게 바꿔 (k8s_apps.tf)</div><div style="font-size:12.5px">'+how+'</div></div>'
   +cmds
   +'<div class=mut style="font-size:12px;margin-top:8px">근거: '+note+'</div></div>';
 }).join('');
 var nMin=Math.ceil(sMinCpu/ALLOC);
 var summary='<div class="grid g4" style="margin-bottom:15px">'
  +'<div class=card><div class=lbl>권장 정상시 pod 합</div><div class="kpi sm">'+sMin+'</div></div>'
  +'<div class=card><div class=lbl>현재 파드 수</div><div class="kpi sm">'+D.summary.pods_total+'</div></div>'
  +'<div class=card><div class=lbl>권장 정상시 노드(추정)</div><div class="kpi sm">'+nMin+'</div></div>'
  +'<div class=card><div class=lbl>현재 노드</div><div class="kpi sm">'+D.summary.nodes_total+'</div></div></div>';
 return '<div class=lbl style="margin-bottom:9px">라이브 자동 판정 — 부하(loadtest/실트래픽) 도는 중에 봐야 정확합니다</div>'
  +summary+'<div class="grid g3">'+cards+'</div>'
  +'<div class=mut style="margin-top:12px;font-size:12px">권장값을 k8s_apps.tf의 각 앱 requests.cpu / HPA averageUtilization / min_replicas 에 반영 후 apply. 노드 추정 = ⌈Σ(min×cpu)/1900m⌉ (t3.medium). 「줄여 ↓」=과투자(비용↓ 가능), 「늘려 ↑」=성능/가용성 부족.</div>';}

function tabs(){var t=[['overview','개요']].concat(D.apps.map(function(a){return [a.app,a.app]})).concat([['pods','Pod'],['nodes','노드'],['waf','WAF'],['calc','계산'],['diag','진단']]);
 document.getElementById('tabs').innerHTML=t.map(function(x){return '<div class="tab'+(x[0]===TAB?' on':'')+'" onclick="setTab(\''+x[0]+'\')">'+x[1]+'</div>'}).join('')}
function render(){if(!D)return;var v=document.getElementById('view');
 // 자동 갱신 시 열어둔 상세 패널을 유지 (새 항목은 위에 쌓이고, 보던 건 그대로 열림)
 var ok={};document.querySelectorAll('details.det[open]').forEach(function(d){ok[d.dataset.k]=1});
 if(TAB==='overview')v.innerHTML=vOverview();else if(TAB==='pods')v.innerHTML=vPods();else if(TAB==='nodes')v.innerHTML=vNodes();
 else if(TAB==='waf')v.innerHTML=vWaf();else if(TAB==='calc')v.innerHTML=vCalc();else if(TAB==='diag')v.innerHTML=vDiag();
 else{var a=D.apps.find(function(x){return x.app===TAB});v.innerHTML=a?vApp(a):''}
 document.querySelectorAll('details.det').forEach(function(d){if(ok[d.dataset.k])d.open=true});}
function setTab(t){TAB=t;tabs();render()}
function setSt(x,c){document.getElementById('st').innerHTML='<span class=dot style="background:'+c+'"></span>'+x}
async function load(){setSt('불러오는 중','#ffcf5c');var s=document.getElementById('since').value;
 try{var r=await fetch('/api/data?since='+s);D=await r.json();tabs();render();setSt('갱신 '+D.ts,'#3ddc97')}catch(e){setSt('연결 오류','#ff5c7a')}}
var tm=null;function setAuto(){if(tm)clearInterval(tm);var s=+document.getElementById('auto').value;if(s)tm=setInterval(load,s*1000)}
document.getElementById('auto').onchange=setAuto;document.getElementById('since').onchange=load;
load();setAuto();
</script></body></html>"""


@app.route("/")
def index():
    return Response(PAGE, mimetype="text/html")


@app.route("/api/data")
def api_data():
    since = request.args.get("since", "15m")
    return jsonify(monitor.build_data(since, monitor._mins(since)))


def main():
    ap = argparse.ArgumentParser(description="3과제 모니터링 대시보드 (Flask)")
    ap.add_argument("--port", type=int, default=8080)
    ap.add_argument("--host", default="0.0.0.0")
    ap.add_argument("--namespace", default="app")
    ap.add_argument("--waf-log-group", default="aws-waf-logs-wsi2026")
    ap.add_argument("--waf-region", default="us-east-1")
    a = ap.parse_args()
    monitor.CFG["ns"] = a.namespace
    monitor.CFG["waf_group"] = a.waf_log_group
    monitor.CFG["waf_region"] = a.waf_region
    print("3과제 모니터링(Flask)  http://%s:%d  (Ctrl+C 종료)" % (a.host, a.port))
    app.run(host=a.host, port=a.port, threaded=True)


if __name__ == "__main__":
    main()