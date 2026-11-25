// Verifica, sem navegador, que a solução de referência de CADA missão (fábrica, Natal e Cão Robô) resolve a missão,
// cumpre o limite de blocos e tem o nº de blocos igual ao OPT (que define as 3 estrelas).  Corre com:  node tests/verificar-missoes.js
const fs=require('fs'),path=require('path');
const R=p=>fs.readFileSync(path.join(__dirname,'..',p),'utf8');
const w={};new Function('window',R('blocos/vb-core.js'))(w);const VB=w.VB;
const w2={};new Function('window',R('blocos/vb-solucoes.js'))(w2);
let bad=0,tot=0;const fail=(...a)=>{bad++;console.log('✗',...a)};
const cut=(h,a,b)=>h.slice(h.indexOf(a),h.indexOf(b));
function check(g,E,sim){
  const SOL=w2.VB_SOL[g];
  if(SOL.length!==E.CY.length||SOL.some((c,i)=>c.length!==E.CY[i].lv.length)){fail(g+': nº de soluções difere do nº de missões');return}
  E.CY.forEach((C,ci)=>C.lv.forEach((L,li)=>{
    tot++;let prog;E.set(ci,[]);
    try{prog=E.parsePy(SOL[ci][li])}catch(err){fail(g,ci+1,li+1,'solução não converte:',err.message);return}
    E.set(ci,prog);const cnt=prog.filter(k=>k.k!=='end').length,tests=L.tests||(sim.cao?[{}]:[null]);
    const win=()=>tests.every(t=>sim.win(E,L,t));
    let tag=null;
    if(!win())tag='a solução NÃO resolve a missão';else if(L.max&&cnt>L.max)tag=`excede o limite (${cnt}>${L.max})`;else if(cnt!==E.OPT[ci][li])tag=`${cnt} blocos mas OPT=${E.OPT[ci][li]}`;
    if(!tag&&L.pre){E.set(ci,JSON.parse(JSON.stringify(L.pre)));if(win())tag='o programa com erro já resolve a missão'}
    if(tag)fail(g,'ciclo',ci+1,'missão',li+1,tag);
  }));
}
for(const g of ['fabrica','natal']){
  const h=R('blocos/'+g+'.html');
  const body='let cy=0,prog=[];'+cut(h,'const x=(n,k)=>','const FAILS=')+h.match(/const OPT=\[\[.*?\]\];/)[0]+'\n'+cut(h,'const OPEN=','const BL=')+'\nreturn {CY,OPT,expand,parsePy,set:(c,p)=>{cy=c;prog=p}}';
  const E=new Function('VB',body)(VB);
  check(g,E,{win:(E,L,t)=>{const nz=a=>L.free?a.map(k=>'RBGY'.includes(k)?'P':k):a;
    return nz(E.expand(t?{...t}:null).map(a=>a.k)).join()===nz(L.x?L.x(t):L.g).join()}});
}
{
  const h=R('blocos/casa-cao.html');
  const lg=cut(h,'/*LOGIC*/','/*ENDLOGIC*/'),pp=cut(h,'function parsePy','let sel=-1;');
  const E2=new Function('VB','let cy=0;'+lg+'\n'+pp+'\nreturn {CY,OPT,mk,simulate,won,parsePy,set:(c,p)=>{cy=c;prog=p}}')(VB);
  check('casa-cao',E2,{cao:1,win:(E,L,t)=>{const X=E.mk(L,t),r=E.simulate(X);return !r.st.stop&&E.won(X,r.st)}});
}
console.log(bad?`${bad} problema(s) em ${tot} missões`:`${tot}/${tot} missões OK (soluções, limites e estrelas)`);
process.exit(bad?1:0);
