#!/usr/bin/env python3
"""Testes de ponta a ponta das novidades dos jogos de blocos:
 1) o cartão «Novo conceito» aparece na primeira missão do ciclo que usa «repetir», «enquanto» ou «se/senão» (e só aí);
 2) o «Modo teclado» deixa completar uma missão só escrevendo o programa (Ctrl+Enter), sem arrastar blocos.
Uso:  python3 tests/e2e-jogos.py     (código 1 se algo falhar)"""
import pathlib,sys
from playwright.sync_api import sync_playwright
ROOT=pathlib.Path(__file__).resolve().parent.parent/'blocos'
LIST='''(g)=>{const o=[];for(let c=0;c<CY.length;c++)for(let l=0;l<CY[c].lv.length;l++){cy=c;LV=CY[c].lv;lv=l;VB.intro({game:g,cy:c,lv:l,parsePy,BL,conds:CONDS,whiles:WHILES,open:OPEN,before:document.getElementById('bw')});const e=document.getElementById('vbi');if(e)o.push([c+1,l+1,e.querySelector('b').textContent.replace('Novo: ','')])}return o}'''
# 1.ª missão de cada ciclo que usa cada conceito (1.º ciclo não usa nenhum)
ESPERADO={'fabrica':[[2,1,'🔁 Repetir'],[3,1,'🔁 Repetir'],[4,1,'🔁 Repetir'],[4,4,'🔄 Enquanto'],[4,5,'🔀 Se … senão']],
 'natal':[[2,1,'🔁 Repetir'],[3,1,'🔁 Repetir'],[4,1,'🔄 Enquanto'],[4,2,'🔀 Se … senão']],
 'casa-cao':[[2,1,'🔁 Repetir'],[3,1,'🔁 Repetir'],[4,1,'🔄 Enquanto'],[4,2,'🔁 Repetir']]}
bad=0
def ok(c,m):
    global bad
    print('✓' if c else '✗',m); bad+=0 if c else 1
with sync_playwright() as p:
    b=p.chromium.launch(args=['--use-gl=swiftshader','--enable-unsafe-swiftshader','--ignore-gpu-blocklist'])
    for g,esp in ESPERADO.items():
        pg=b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.add_init_script('window.requestAnimationFrame=()=>0')
        pg.goto((ROOT/f'{g}.html').as_uri(),wait_until='domcontentloaded',timeout=90000); pg.wait_for_timeout(2500)
        got=pg.evaluate(LIST,g); ok(got==esp,f'{g}: cartões de conceito {got}'); ok(not errs,f'{g}: sem erros JS {errs[:1]}'); pg.close()
    pg=b.new_page(viewport={'width':1000,'height':720}); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
    pg.goto((ROOT/'casa-cao.html').as_uri(),wait_until='domcontentloaded',timeout=90000); pg.wait_for_timeout(3000)
    pg.evaluate("()=>{window.setLight=()=>{}}"); pg.click('#kb'); pg.wait_for_timeout(300)
    ok(pg.evaluate("getComputedStyle(document.getElementById('pyb')).display!=='none'"),'modo teclado: editor de texto disponível no 1.º ciclo')
    ok(pg.get_attribute('#msg','aria-live')=='polite','mensagens anunciadas a leitores de ecrã (aria-live)')
    pg.fill('#py',pg.evaluate('VB_SOL["casa-cao"][0][0]')); pg.keyboard.press('Control+Enter')
    try: pg.wait_for_selector('.vbc-btn',timeout=200000); res=True
    except Exception: res=False
    ok(res and 'Missão cumprida' in pg.inner_text('#msg'),'modo teclado: missão completada só com texto + Ctrl+Enter'); ok(not errs,'modo teclado: sem erros JS')
    # ajuda que cresce com os erros (Cão Robô, ciclo 2, missão 5): 1.º erro sem ajuda, 2.º dica, 3.º primeiros passos, 5.º solução
    pg2=b.new_page(viewport={'width':1000,'height':900}); errs2=[]; pg2.on('pageerror',lambda e:errs2.append(str(e)))
    pg2.goto((ROOT/'casa-cao.html').as_uri(),wait_until='domcontentloaded',timeout=90000); pg2.wait_for_timeout(3000)
    pg2.evaluate("()=>{window.setLight=()=>{};light=false;VBA.post.on=false}")
    pg2.evaluate('([c,l])=>{cy=c;LV=CY[c].lv;lv=l;clear();levels();render()}',[1,4])
    esperado={1:[],2:['tip'],3:['tip','start'],4:['tip','start'],5:['tip','start','full']}
    for n in range(1,6):
        pg2.evaluate('(py)=>{prog=parsePy(py);render()}','andar()\nandar()')
        pg2.click('#go'); pg2.wait_for_function("()=>/❌|💥/.test(document.getElementById('msg').textContent)",timeout=150000); pg2.wait_for_timeout(250)
        got=pg2.evaluate("[...document.querySelectorAll('#msg .vbh-b button')].map(b=>b.getAttribute('data-a'))")
        ok(got==esperado[n],f'ajuda no erro {n}: botões {got}')
    ok(not errs2,'ajuda: sem erros JS')
    b.close()
sys.exit(1 if bad else 0)
