import fs from 'node:fs/promises';
import path from 'node:path';
import { pathToFileURL } from 'node:url';

const workspaceDir = 'D:/Henry/School/NTUST/Project/cybersecai2026.github.io';
const SKILL_DIR = 'C:/Users/henry/.codex/plugins/cache/openai-primary-runtime/presentations/26.905.11957/skills/presentations';
const RUNTIME_PYTHON = 'C:/Users/henry/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe';
const RUNTIME_NODE_MODULES = 'C:/Users/henry/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules';
process.env.RUNTIME_NODE_MODULES ??= RUNTIME_NODE_MODULES;
process.env.RUNTIME_NODE ??= 'C:/Users/henry/.cache/codex-runtimes/codex-primary-runtime/dependencies/node/bin/node.exe';
const { Presentation, PresentationFile } = await import(pathToFileURL(
  path.join(RUNTIME_NODE_MODULES, '@oai/artifact-tool/dist/artifact_tool.mjs')).href);
const buildDir = path.join(workspaceDir, '.codex-pptx-build');
const finalPath = path.join(workspaceDir, 'artifacts', 'program-at-a-glance-editable.pptx');
const { finalizePresentation } = await import(pathToFileURL(path.join(SKILL_DIR, 'container_tools/artifact_tool_utils.mjs')).href);
await fs.mkdir(buildDir, {recursive:true});
await fs.mkdir(path.dirname(finalPath), {recursive:true});

const C={bg:'#F7F9FC',white:'#FFFFFF',ink:'#17345A',muted:'#687E99',line:'#D9E3EE',blue:'#0055A4',red:'#D62828',visit:'#E6F0FA',social:'#FDEBEA',session:'#C8DDF1',evening:'#FDEBEA',detailBlue:'#4D7095'};
const pres=Presentation.create({slideSize:{width:2400,height:2300}});
const slide=pres.slides.add();
slide.background.fill=C.bg;
const FONT='Arial';

function box(x,y,w,h,fill,outline='none',radius=false,lineWidth=1){
  return slide.shapes.add({geometry:radius?'roundRect':'rect',position:{left:x,top:y,width:w,height:h},fill,line:{fill:outline,width:outline==='none'?0:lineWidth}});
}
function label(s,x,y,w,h,size,color=C.ink,bold=false,align='left'){
  const sh=slide.shapes.add({geometry:'textbox',position:{left:x,top:y,width:w,height:h},fill:'none',line:{fill:'none',width:0}});
  sh.text=s;
  sh.text.style={typeface:FONT,fontSize:size,bold,color,alignment:align,verticalAlignment:'middle',autoFit:'shrinkText',wrap:'none',insets:{left:0,right:0,top:0,bottom:0}};
  return sh;
}
function centered(s,cx,cy,w,h,size,color=C.ink,bold=false){return label(s,cx-w/2,cy-h/2,w,h,size,color,bold,'center')}
function hr(x,y,w,color=C.line,h=2){box(x,y,w,h,color)}

label('Program At A Glance',90,51,1300,100,83,C.blue,true);
label('2026 Taiwan–France Joint Research Workshop on Cybersecurity & AI',90,158,1800,46,33,C.muted);
label('3–6 November 2026  ·  Provisional program updated 6 October 2026',90,210,1800,35,25,C.muted);
box(90,260,740,9,C.blue);box(830,260,740,9,C.white,C.line);box(1570,260,740,9,C.red);

const CARD_W=1092, left=90, right=1218, top=285, bottom=1135;
function card(x,y,h,day,subtitle,color){
  box(x,y,CARD_W,h,C.white,C.line,true,2);
  box(x+18,y+18,CARD_W-36,99,color,'none',true);
  label(day,x+43,y+26,900,78,58,C.white,true);
  label(subtitle,x+31,y+135,CARD_W-62,65,42,C.ink,true);
}
card(left,top,820,'TUE 3 NOV','Taipei',C.blue);
card(right,top,820,'WED 4 NOV','Academia Sinica / Hsinchu',C.red);
card(left,bottom,1060,'THU 5 NOV','Security workshop',C.blue);
card(right,bottom,1060,'FRI 6 NOV','Joint + parallel',C.red);

function day3Row(x,y,time,name,detail,kind='plain'){
  const fill=kind==='visit'?C.visit:kind==='social'?C.social:C.white;
  const accent=kind==='visit'?C.blue:kind==='social'?C.red:C.muted;
  box(x+25,y,CARD_W-50,56,fill,kind==='plain'?C.line:'none',true);
  box(x+25,y+8,6,40,accent);
  label(time,x+48,y+6,225,44,27,accent,true);
  if(name.toLowerCase().includes('lunch')) centered(name,x+CARD_W/2,y+28,300,50,30,C.ink,true);
  else label(name,x+285,y+5,295,46,30,C.ink,true);
  if(detail) label(detail,x+(name.toLowerCase().includes('lunch')?765:585),y+6,305,44,23,C.muted);
}
[
 ['09:20','Meet','Academia Sinica main gate','plain'],
 ['09:20–10:00','Transfer','To NTU','plain'],
 ['10:00–12:00','Visit','','visit'],
 ['12:00–12:30','Transfer','To lunch venue','plain'],
 ['12:30–14:00','Lunch','At NTU','plain'],
 ['14:00–15:30','Visit','To be confirmed','visit'],
 ['15:30–16:00','Transfer','','plain'],
 ['16:00–18:00','Social Event','','social'],
].forEach((r,i)=>day3Row(left,top+200+i*60,...r));

const colW=(CARD_W-50-18)/2, lx=right+25, rx=lx+colW+18, headY=top+205, rowsY=headY+63;
box(lx,headY,colW,51,C.visit,'none',true);box(rx,headY,colW,51,C.social,'none',true);
label('MAIN GROUP',lx+18,headY+3,colW-25,45,26,C.blue,true);
label("PROF. MARION'S GROUP",rx+18,headY+3,colW-25,45,26,C.red,true);
function groupRow(i,time,name,kind){
  const y=rowsY+i*60,fill=kind==='visit'?C.visit:kind==='social'?C.social:kind==='break'?'#F1F5F9':C.white;
  const accent=kind==='visit'?C.blue:kind==='social'?C.red:C.muted;
  box(lx,y,colW,56,fill,kind==='plain'?C.line:'none',true);
  box(lx,y+8,6,40,accent);
  label(time,lx+16,y+6,175,44,22,accent,true);
  if(name.toLowerCase().includes('lunch')||name.toLowerCase().includes('break')) centered(name,lx+colW/2,y+28,225,47,25,C.ink,true);
  else label(name,lx+190,y+6,colW-202,44,25,C.ink,true);
}
[
 ['09:00','Meet','plain'],['09:00–09:30','Transfer','plain'],
 ['09:30–11:00','Social Event','social'],['11:00–13:00','Lunch & transfer','plain'],
 ['13:00–15:00','Visit','visit'],['15:00–15:30','Transfer / break','break'],
 ['15:30–16:30','Visit','visit'],['16:30–18:00','Return / free time','plain'],
].forEach((r,i)=>groupRow(i,...r));
box(rx,rowsY,colW,476,C.social,'none',true);box(rx,rowsY+14,7,448,C.red);
label('ALL DAY',rx+32,rowsY+11,colW-55,55,26,C.red,true);
label('Academic exchange',rx+32,rowsY+100,colW-55,65,34,C.ink,true);
label('Academia Sinica',rx+32,rowsY+160,colW-55,55,27,C.muted);
label('Program details TBC',rx+32,rowsY+398,colW-55,55,25,C.muted);

function workshopRow(x,y,time,name,detail,kind){
  const h=kind==='session'?96:kind==='break'?42:kind==='poster'?50:54;
  const isMeal=kind==='break'||kind==='poster';
  const fill=kind==='session'?C.session:isMeal?C.red:kind==='evening'?C.evening:C.white;
  const accent=kind==='session'?C.blue:isMeal?'#F5DCE0':kind==='evening'?C.red:C.muted;
  box(x+25,y,CARD_W-50,h,fill,kind==='plain'?C.line:'none',true);
  box(x+25,y+8,6,h-16,accent);
  label(time,x+48,y+3,220,h-6,isMeal?24:27,isMeal?C.white:kind==='session'?C.blue:kind==='evening'?C.red:C.muted,true);
  if(isMeal) centered(name,x+CARD_W/2,y+h/2,390,h-4,26,C.white,true);
  else centered(name,x+435,y+h/2,300,h-4,30,C.ink,true);
  if(detail) label(detail,x+(isMeal?765:585),y+4,isMeal?300:470,h-8,isMeal?21:23,isMeal?'#F8E8EA':kind==='session'?C.detailBlue:C.muted);
  return y+h+4;
}
function parallelRow(x,y,time,name,topic,ai){
  const h=96;
  label(name,x+48,y+14,195,34,21,C.blue,true);
  label(time,x+48,y+47,205,40,27,C.blue,true);
  const b1=x+260,b2=x+671;
  box(b1,y,399,h,C.session,'none',true);box(b2,y,CARD_W-25-671,h,C.session,'none',true);
  box(b1,y+8,6,h-16,C.blue);box(b2,y+8,6,h-16,C.blue);
  centered(topic,b1+199.5,y+h/2,375,h-6,25,C.ink,true);
  centered(ai,b2+(CARD_W-25-671)/2,y+h/2,370,h-6,30,C.ink,true);
  return y+h+4;
}
let y5=bottom+200;
[
 ['09:00–09:30','Registration','Poster set-up','plain'],
 ['09:30–10:10','Opening','Ceremony & group photo','plain'],
 ['10:10–10:40','Session 1','Malware Analysis','session'],
 ['10:40–11:00','Tea break','','break'],
 ['11:00–12:00','Session 2','Malware & Threat Detection','session'],
 ['12:00–13:30','Lunch & TACC Poster','','poster'],
 ['13:30–14:45','Session 3','Trustworthy Systems & AI Threats','session'],
 ['14:45–15:15','Tea break','','break'],
 ['15:15–16:45','Session 4','Malware & Cyber Threats','session'],
 ['16:45–17:00','Closing','','plain'],
 ['19:00–21:30','Banquet','','evening'],
].forEach(r=>{y5=workshopRow(left,y5,...r)});
let y6=bottom+200;
[
 ['09:00–09:30','Registration','Poster set-up','plain'],
 ['09:30–09:50','Opening','Ceremony & group photo','plain'],
 ['09:50–10:50','Joint session','AI Security · 20-minute talks','session'],
 ['10:50–11:15','Tea break','Tracks split','break'],
 ['11:15–12:00','Parallel 1','AI Security','AI (1)','parallel'],
 ['12:00–13:30','Lunch & posters','TACC Research Posters','poster'],
 ['13:30–14:45','Parallel 2','Cybersecurity & Wireless','AI (2)','parallel'],
 ['14:45–15:15','Tea break','','break'],
 ['15:15–16:45','Parallel 3','Hardware & Crypto','AI (3)','parallel'],
 ['16:45–17:00','Closing','Joint ceremony','plain'],
 ['19:00–21:30','Farewell party','','evening'],
].forEach(r=>{y6=r[4]==='parallel'?parallelRow(right,y6,r[0],r[1],r[2],r[3]):workshopRow(right,y6,r[0],r[1],r[2],r[3])});

hr(90,2230,2220);label('Poster presenters stand by their posters 13:00–13:30 on both days.  Session and speaker details remain in the full provisional program.',90,2241,2200,47,25,C.muted);
slide.speakerNotes.textFrame.setText('Based on the provisional Taiwan–France Workshop Program updated 6 October 2026.');

const candidatePath=path.join(buildDir,'candidate.pptx');
await (await PresentationFile.exportPptx(pres)).save(candidatePath);
const preview=await pres.export({slide,format:'png',scale:1});
await fs.writeFile(path.join(buildDir,'preview.png'),new Uint8Array(await preview.arrayBuffer()));
const result=await finalizePresentation({
  workspaceDir,candidatePath,finalPath,
  pythonExecutable:RUNTIME_PYTHON,
  integrityValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_package_integrity.py'),
  layoutValidatorPath:path.join(SKILL_DIR,'container_tools/inspect_presentation_layout_geometry.py'),
  layoutArgs:['--expected-slide-size-emu','22860000,21907500','--validate-heading-fit'],
  explicitTotalSlideCount:1,
  requiredNativeTableOwnerSlides:[],requiredNativeChartOwnerSlides:[],
  fontPolicy:{basis:'design',families:[FONT]},
  verifyArtifactToolImport:true,
  receiptPath:path.join(buildDir,'validation.json'),
});
console.log(JSON.stringify({finalPath,result},null,2));
