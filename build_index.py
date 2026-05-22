# -*- coding: utf-8 -*-
import os, json, re

base = os.path.dirname(os.path.abspath(__file__))
data = {}

for name in sorted(os.listdir(base)):
    folder = os.path.join(base, name)
    if not os.path.isdir(folder):
        continue
    files = sorted([f for f in os.listdir(folder) if f.endswith('.html')])
    if not files:
        continue
    data[name] = {}
    for fname in files:
        date = fname.replace('.html', '')
        fpath = os.path.join(folder, fname)
        with open(fpath, 'r', encoding='utf-8') as f:
            content = f.read()
        m = re.search(r'<body[^>]*>(.*?)</body>', content, re.DOTALL)
        body = m.group(1).strip() if m else content
        body = re.sub(r'<h2[^>]*>.*?</h2>', '', body, flags=re.DOTALL).strip()
        data[name][date] = body

data_json = json.dumps(data, ensure_ascii=False)

TEMPLATE = '''<!DOCTYPE html>
<html lang="ko">
<head>
<meta charset="UTF-8">
<title>주간업무보고 뷰어</title>
<style>
*{box-sizing:border-box;margin:0;padding:0}
body{font-family:"맑은 고딕",sans-serif;font-size:13px;display:flex;height:100vh;background:#f0f2f5}
#sidebar{width:145px;min-width:145px;background:#1e3a5f;color:white;display:flex;flex-direction:column;overflow-y:auto}
#sidebar h1{font-size:11px;padding:13px 8px;background:#152d4a;text-align:center;line-height:1.5;letter-spacing:.5px}
.person-btn{padding:11px 14px;cursor:pointer;border-bottom:1px solid #2a4f7a;font-size:13px;transition:background .15s}
.person-btn:hover{background:#2a4f7a}
.person-btn.active{background:#3a7bd5;font-weight:bold}
#main{flex:1;display:flex;flex-direction:column;overflow:hidden}
#tab-bar{background:white;border-bottom:2px solid #3a7bd5;display:flex;flex-wrap:wrap;gap:4px;padding:7px 12px;align-items:center;min-height:46px}
.date-tab{padding:4px 11px;border-radius:4px;cursor:pointer;background:#e8eef8;font-size:12px;border:1px solid #c0cfe8;transition:background .15s;white-space:nowrap}
.date-tab:hover{background:#c8d8f0}
.date-tab.active{background:#3a7bd5;color:white;border-color:#3a7bd5;font-weight:bold}
.date-tab.edited::after{content:" ●";color:#ff6b35;font-size:9px}
.date-tab.active.edited::after{color:#ffe082}
#toolbar{background:#fff;border-bottom:1px solid #dde;padding:7px 14px;display:flex;align-items:center;gap:8px}
#toolbar h2{font-size:14px;color:#1e3a5f;flex:1}
#status{font-size:11px;color:#27ae60;min-width:120px;text-align:right}
.btn{padding:6px 13px;border-radius:4px;border:none;cursor:pointer;font-size:12px;font-family:inherit;font-weight:bold}
.btn-save{background:#3a7bd5;color:white}
.btn-save:hover{background:#2a6bc5}
.btn-export{background:#27ae60;color:white}
.btn-export:hover{background:#219a52}
.btn-reset{background:#e74c3c;color:white}
.btn-reset:hover{background:#c0392b}
.btn-reset-all{background:#7f8c8d;color:white}
.btn-reset-all:hover{background:#636e72}
#editor-wrap{flex:1;overflow-y:auto;padding:14px}
#editor{background:white;border-radius:6px;box-shadow:0 1px 4px rgba(0,0,0,.1);padding:20px;min-height:100%;outline:none;line-height:1.7}
#editor:focus{box-shadow:0 0 0 2px #3a7bd5}
#editor table{border-collapse:collapse;width:100%;margin:6px 0}
#editor td,#editor th{border:1px solid #bbb;padding:6px 8px;vertical-align:top}
#editor th,#editor thead td{background:#ddeeff;font-weight:bold;text-align:center}
#editor tbody td{background:#fff}
#editor table:not(:has(thead)) tr:first-child td{background:#ddeeff;font-weight:bold;text-align:center}
#edit-hint{text-align:center;padding:5px;background:#fff8e1;font-size:11px;color:#999;border-top:1px solid #ffe082}
</style>
</head>
<body>
<div id="sidebar">
  <h1>📋 주간업무보고</h1>
  <div id="person-list"></div>
</div>
<div id="main">
  <div id="tab-bar"><span style="color:#aaa;font-size:12px">← 담당자를 선택하세요</span></div>
  <div id="toolbar">
    <h2 id="doc-title">담당자를 선택하세요</h2>
    <span id="status"></span>
    <button class="btn btn-save" onclick="saveToStorage()" title="Ctrl+S">💾 저장</button>
    <button class="btn btn-export" onclick="exportFile()">📥 파일 내보내기</button>
    <button class="btn btn-reset" onclick="resetCurrent()">↩ 원본복원</button>
    <button class="btn btn-reset-all" onclick="resetAll()" title="전체 편집 내용 삭제">🗑 전체초기화</button>
  </div>
  <div id="editor-wrap">
    <div id="editor" contenteditable="true"><p style="color:#bbb;text-align:center;padding:60px">담당자와 날짜를 선택하세요</p></div>
  </div>
  <div id="edit-hint">클릭하면 바로 편집 가능 &nbsp;|&nbsp; 💾 저장(Ctrl+S) &nbsp;|&nbsp; 📥 파일 내보내기로 영구 저장</div>
</div>
<script>
// ===DATA_START===
const ORIGINAL = __DATA_JSON__;
// ===DATA_END===

const LS_KEY = 'weeklyReport_v2';
function loadEdits(){try{return JSON.parse(localStorage.getItem(LS_KEY)||'{}')}catch(e){return{}}}
function saveEdits(e){localStorage.setItem(LS_KEY,JSON.stringify(e))}

let curPerson=null, curDate=null;

const personList=document.getElementById('person-list');
Object.keys(ORIGINAL).forEach(name=>{
  const btn=document.createElement('div');
  btn.className='person-btn';
  btn.textContent=name;
  btn.onclick=()=>selectPerson(name);
  btn.id='pb-'+name;
  personList.appendChild(btn);
});

function selectPerson(name){
  if(curPerson&&curDate) autoSave();
  curPerson=name; curDate=null;
  document.querySelectorAll('.person-btn').forEach(b=>b.classList.remove('active'));
  document.getElementById('pb-'+name).classList.add('active');
  const edits=loadEdits();
  const tabBar=document.getElementById('tab-bar');
  tabBar.innerHTML='';
  const dates=Object.keys(ORIGINAL[name]).sort();
  dates.forEach(date=>{
    const tab=document.createElement('div');
    tab.className='date-tab'+(edits[name]&&edits[name][date]?' edited':'');
    tab.textContent=date;
    tab.id='tab-'+date;
    tab.onclick=()=>selectDate(name,date);
    tabBar.appendChild(tab);
  });
  selectDate(name,dates[dates.length-1]);
}

function selectDate(name,date){
  if(curPerson===name&&curDate===date) return;
  if(curPerson&&curDate) autoSave();
  curPerson=name; curDate=date;
  document.querySelectorAll('.date-tab').forEach(t=>t.classList.remove('active'));
  const tab=document.getElementById('tab-'+date);
  if(tab) tab.classList.add('active');
  document.getElementById('doc-title').textContent=name+' — '+date+' 주간업무보고';
  const edits=loadEdits();
  const content=(edits[name]&&edits[name][date])?edits[name][date]:ORIGINAL[name][date];
  document.getElementById('editor').innerHTML=content;
  setStatus('');
}

function autoSave(){
  if(!curPerson||!curDate) return;
  const content=document.getElementById('editor').innerHTML;
  const edits=loadEdits();
  if(!edits[curPerson]) edits[curPerson]={};
  edits[curPerson][curDate]=content;
  saveEdits(edits);
  const tab=document.getElementById('tab-'+curDate);
  if(tab) tab.classList.add('edited');
}

function saveToStorage(){
  autoSave();
  setStatus('저장됨 ✓ '+timeStr());
}

function resetCurrent(){
  if(!curPerson||!curDate) return;
  if(!confirm(curPerson+' '+curDate+' 를 원본으로 되돌리겠습니까?')) return;
  const edits=loadEdits();
  if(edits[curPerson]) delete edits[curPerson][curDate];
  saveEdits(edits);
  document.getElementById('editor').innerHTML=ORIGINAL[curPerson][curDate];
  const tab=document.getElementById('tab-'+curDate);
  if(tab) tab.classList.remove('edited');
  setStatus('원본으로 복원됨');
}

function resetAll(){
  if(!confirm('전체 담당자의 모든 편집 내용을 삭제하고 원본으로 되돌리겠습니까?')) return;
  localStorage.removeItem(LS_KEY);
  document.querySelectorAll('.date-tab').forEach(t=>t.classList.remove('edited'));
  if(curPerson&&curDate){
    document.getElementById('editor').innerHTML=ORIGINAL[curPerson][curDate];
  }
  setStatus('전체 원본으로 복원됨 ✓');
}

function exportFile(){
  autoSave();
  const edits=loadEdits();
  const merged=JSON.parse(JSON.stringify(ORIGINAL));
  for(const n of Object.keys(edits))
    for(const d of Object.keys(edits[n]))
      if(merged[n]&&merged[n][d]!==undefined) merged[n][d]=edits[n][d];
  // 현재 HTML 소스의 DATA 마커 사이를 새 데이터로 교체
  const src=document.documentElement.outerHTML;
  const newData=JSON.stringify(merged);
  const newSrc=src.replace(
    /\/\/ ===DATA_START===[\s\S]*?\/\/ ===DATA_END===/,
    '// ===DATA_START===\\nconst ORIGINAL = '+newData+';\\n// ===DATA_END==='
  );
  const blob=new Blob([newSrc],{type:'text/html;charset=utf-8'});
  const a=document.createElement('a');
  a.href=URL.createObjectURL(blob);
  a.download='index.html';
  a.click();
  setStatus('내보내기 완료 ✓ '+timeStr());
}

function setStatus(msg){document.getElementById('status').textContent=msg}
function timeStr(){const n=new Date();return n.getHours().toString().padStart(2,'0')+':'+n.getMinutes().toString().padStart(2,'0')}

let _timer=null;
document.getElementById('editor').addEventListener('input',()=>{
  clearTimeout(_timer);
  setStatus('편집 중...');
  _timer=setTimeout(()=>{autoSave();setStatus('자동저장됨 '+timeStr())},3000);
});
document.addEventListener('keydown',e=>{
  if((e.ctrlKey||e.metaKey)&&e.key==='s'){e.preventDefault();saveToStorage();}
});
</script>
</body>
</html>'''

html = TEMPLATE.replace('__DATA_JSON__', data_json)

out_path = r'D:\Temp\주간업무정리\index.html'
with open(out_path, 'w', encoding='utf-8') as f:
    f.write(html)

size_kb = os.path.getsize(out_path) // 1024
print(f'생성 완료: {out_path}')
print(f'파일 크기: {size_kb} KB')
print(f'담당자: {len(data)}명, 총 {sum(len(v) for v in data.values())}개 보고서')
