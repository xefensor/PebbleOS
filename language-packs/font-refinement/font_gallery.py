import sys,base64,io,html,hashlib,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from font_work import Font
out=Path('language-packs/font-refinement')
parts=[]
samples=['ÁÉÍÓÚÝ ČĎĚŇŘŠŤŽ Ů','áéíóúý čďěňřšťž ů','Příliš žluťoučký kůň úpěl ďábelské ódy.','ší ŠÍ čí ří ží ďá ťá íí ÚTERÝ ČTVRTEK']
for path in sorted((out/'before').glob('*.pbf')):
 name=path.stem;parts.append('<section><h2>'+name+'</h2>')
 for text in samples:
  parts.append('<div class="sample">')
  for ver,label in [('previous','Předchozí'),('after','Vyvážené')]:
   im=Font((out/ver/path.name).read_bytes()).render(text);buf=io.BytesIO();im.save(buf,format='PNG');data=base64.b64encode(buf.getvalue()).decode();parts.append(f'<div class="row"><b>{label}</b><img alt="{html.escape(text)}" data-w="{im.width}" data-h="{im.height}" src="data:image/png;base64,{data}"></div>')
  parts.append('</div>')
 parts.append('</section>')
prefix='''<!doctype html><html lang="cs"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Čeština – úprava diakritiky</title><style>body{font:16px system-ui;margin:24px;background:#f4f4f4;color:#171717}h1{font-size:26px}header{position:sticky;top:0;background:#f4f4f4;padding:12px 0;z-index:1}section{background:white;padding:16px;margin:24px 0;border-radius:8px}h2{font-size:18px}.sample{overflow:auto;margin:16px 0;border-top:1px solid #ddd}.row{display:flex;align-items:center;gap:20px;margin:10px 0;width:max-content}.row b{width:80px;font-size:14px}.row img{image-rendering:pixelated}input{vertical-align:middle}aside{max-width:900px;line-height:1.5}</style><h1>České fonty: háčky a čárky před úpravou a po ní</h1><aside>Skutečné bitmapy z PBF, bez vyhlazování. Čárky a háčky mají vyváženou výšku a tloušťku podle konkrétního fontu. Porovnání s předchozím návrhem s dlouhými čárkami. <strong>Pozor: běžný firmware preferuje existující latinské znaky vestavěného fontu. Samotný balíček proto tuto úpravu nevynutí na všech obrazovkách.</strong> Podrobnosti v README.md. <a href="online-comparison/index.html">Porovnání s online Raster Gothic a ukázkami Pebble</a>.</aside><header><label>Zvětšení <input id="scale" type="range" min="1" max="6" value="3"> <output id="value">3×</output></label></header>'''
suffix='''<script>const s=document.getElementById('scale');function resize(){document.getElementById('value').textContent=s.value+'×';document.querySelectorAll('img').forEach(i=>{i.style.width=(i.dataset.w*s.value)+'px';i.style.height=(i.dataset.h*s.value)+'px'})}s.addEventListener('input',resize);resize();</script></html>'''
(out/'index.html').write_text(prefix+''.join(parts)+suffix)
sha=hashlib.sha256(Path('language-packs/cs_CZ-refined-fonts.pbl').read_bytes()).hexdigest();(out/'package-sha256.txt').write_text(sha+'  cs_CZ-refined-fonts.pbl\n');print('Gallery ready;',sha)
