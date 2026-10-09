"""Control reproducible de SQL (adaptado a SQLite), definiciones PBIP y conciliación.

No ejecuta DAX ni sustituye a MySQL 8.0/Power BI Desktop.
"""
import base64
import csv
import json
from pathlib import Path
import sqlite3
import urllib.request
import urllib.error
import zipfile
import pandas as pd
import sqlglot
import jsonschema

ROOT=Path(__file__).resolve().parents[1]
PBIP=ROOT/'powerbi/NexaMart_corregido'

def main():
    db=sqlite3.connect(':memory:')
    for p in (ROOT/'data/snapshot').glob('*.csv'):
        pd.read_csv(p).to_sql(p.stem,db,index=False)
    source=(ROOT/'sql/consultas_analiticas.sql').read_text()
    expressions=sqlglot.parse(source,read='mysql')
    results=[]
    for expr in expressions:
        if isinstance(expr,sqlglot.exp.Use):continue
        adapted=expr.sql(dialect='sqlite').replace('CREATE OR REPLACE VIEW','CREATE VIEW')
        result=db.execute(adapted)
        if result.description:
            keys=[x[0] for x in result.description]
            results.append([dict(zip(keys,row)) for row in result.fetchall()])
    assert len(results)==10
    stores=results[0]
    assert round(sum(r['ventas_netas'] for r in stores),2)==103851.74
    assert sum(r['pedidos_venta'] for r in stores)==751
    assert results[1][0]['nombre_vendedor']=='Cristian Santos'
    assert round(results[1][0]['ventas_netas'],2)==16345.58
    assert len(results[2])==15
    assert len({(r['categoria'],r['posicion']) for r in results[2]})==15
    assert round(sum(r['porcentaje_ventas_netas'] for r in results[3]),2)==100
    months=results[4]
    assert [r['mes'] for r in months]==sorted(r['mes'] for r in months)
    assert len(months)==12 and round(sum(r['ventas_netas'] for r in months),2)==103851.74
    assert len(results[5])==10 and all(r['segmento']=='VIP' for r in results[5])
    assert sum(r['num_devoluciones'] for r in results[6])==6
    kpi=results[7][0]
    expected={'ventas_brutas':104718.63,'importe_devoluciones':866.89,'ventas_netas':103851.74,'pedidos_venta':751,'ticket_promedio':139.44,'total_eventos':757,'eventos_devolucion':6}
    for key,value in expected.items():assert round(kpi[key],2)==value,(key,kpi[key])
    gap=results[8][0]
    assert gap['residual']==0 and round(gap['brecha_neta'],2)==8690.55
    assert round(gap['efecto_volumen']+gap['efecto_ticket']+gap['efecto_devoluciones'],2)==8690.55
    cats=results[9]
    assert round(sum(r['contribucion_brecha'] for r in cats),2)==8690.55
    assert cats[0]['categoria']=='Sports & Fitness' and round(cats[0]['contribucion_brecha'],2)==5688.99
    assert cats[0]['pedidos_singapore']==cats[0]['pedidos_sydney']==37
    assert db.execute('SELECT COUNT(*) FROM vw_ventas_analitico').fetchone()[0]==757
    assert db.execute('SELECT ROUND(SUM(importe_venta_bruta-importe_devuelto-precio_total),2) FROM vw_ventas_analitico').fetchone()[0]==0
    # Comprobación independiente por categoría y tienda desde los CSV.
    f=pd.read_csv(ROOT/'data/snapshot/factventas.csv').merge(pd.read_csv(ROOT/'data/snapshot/dimtienda.csv'),on='tienda_id').merge(pd.read_csv(ROOT/'data/snapshot/dimproducto.csv'),on='producto_id')
    g=f.groupby(['ciudad','categoria']).precio_total.sum()
    for row in cats:
        assert round(g['Singapore',row['categoria']]-g['Sydney',row['categoria']],2)==round(row['contribucion_brecha'],2)
    model=json.loads((PBIP/'NexaMart.SemanticModel/model.bim').read_text())['model']
    tables={t['name']:t for t in model['tables']}
    measures={m['name']:m for m in tables['Medidas']['measures']}
    assert len(model['relationships'])==6
    rel=next(r for r in model['relationships'] if r['name']=='ventas_calendario')
    assert rel['isActive'] and rel['crossFilteringBehavior']=='oneDirection' and rel['toColumn']=='Date' and rel['fromColumn']=='fecha'
    date=next(c for c in tables['DimCalendario']['columns'] if c['name']=='Date')
    assert date['isKey'] and tables['DimCalendario']['dataCategory']=='Time'
    yearmonth=next(c for c in tables['DimCalendario']['columns'] if c['name']=='Año-Mes')
    assert yearmonth['dataType']=='string' and yearmonth['sortByColumn']=='AñoMesOrden'
    assert measures['Ticket Promedio']['expression']=='DIVIDE([Ventas Brutas], [Pedidos Venta])'
    assert 'FALSE()' in measures['Pedidos Venta']['expression']
    assert '[Total Eventos]' in measures['Proporción Eventos Devolución']['expression']
    assert 'DATE(2025,1,1)' in tables['DimCalendario']['partitions'][0]['source']['expression']
    # Los datos portátiles incorporados deben coincidir exactamente con los CSV.
    for name,t in tables.items():
        if not name.startswith('nexamart '):continue
        expr=t['partitions'][0]['source']['expression']
        payload=expr.split('Binary.FromText("',1)[1].split('"',1)[0]
        rows=json.loads(base64.b64decode(payload))
        csvrows=list(csv.DictReader((ROOT/'data/snapshot'/f'{name.split()[1]}.csv').open(encoding='utf-8-sig')))
        assert len(rows)==len(csvrows)
        keys=[c['name'] for c in t['columns']]
        for row,original in zip(rows,csvrows):
            for val,key in zip(row,keys):
                s=original[key]
                if isinstance(val,bool):assert val==(s.lower() in ('true','1'))
                elif isinstance(val,(int,float)):assert abs(val-float(s))<1e-9
                elif val is None:assert s==''
                else:assert val==s[:10] if key=='fecha' else val==s
    # Referencias de cada visual: no puede quedar ningún campo inexistente.
    def fields(obj):
        if isinstance(obj,dict):
            for typ in ('Column','Measure'):
                if typ in obj:
                    field=obj[typ];entity=field.get('Expression',{}).get('SourceRef',{}).get('Entity')
                    if entity:yield typ,entity,field['Property']
            for v in obj.values():yield from fields(v)
        elif isinstance(obj,list):
            for v in obj:yield from fields(v)
    visuals=list((PBIP/'NexaMart.Report').rglob('visual.json'))
    for p in visuals:
        obj=json.loads(p.read_text())
        for typ,table,prop in fields(obj):
            assert table in tables,(p,table)
            names={x['name'] for x in tables[table].get('measures' if typ=='Measure' else 'columns',[])}
            assert prop in names,(p,table,prop)
        if obj['visual']['visualType']=='lineChart':
            sort=obj['visual']['query']['sortDefinition']['sort'][0]
            assert sort['direction']=='Ascending' and sort['field']['Column']['Property']=='Año-Mes'
    schema_cache={}
    def retrieve(url):
        if url not in schema_cache:
            try:
                data=urllib.request.urlopen(url,timeout=30).read()
            except urllib.error.HTTPError as e:
                if e.code!=404 or not url.endswith('/schema.embedded.json'):raise
                # Algunos esquemas oficiales referencian una variante embedded
                # no publicada. Se usa la versión pública de la misma estructura.
                data=urllib.request.urlopen(url.replace('/schema.embedded.json','/schema-embedded.json'),timeout=30).read()
            schema_cache[url]=json.loads(data)
        return schema_cache[url]
    schema_count=0
    for p in PBIP.rglob('*'):
        if not p.is_file() or p.suffix not in ('.json','.pbip','.pbir','.pbism'):continue
        obj=json.loads(p.read_text())
        if '$schema' not in obj:continue
        schema=retrieve(obj['$schema'])
        resolver=jsonschema.RefResolver(base_uri=obj['$schema'],referrer=schema,handlers={'https':retrieve})
        jsonschema.Draft7Validator(schema,resolver=resolver).validate(obj)
        schema_count+=1
    # El motor local usa floats; presentar importes y porcentajes con dos decimales.
    for rows in results:
        for row in rows:
            for key,value in row.items():
                if isinstance(value,float):row[key]=round(value,2)
    archive=ROOT/'powerbi/NexaMart_corregido.zip'
    with zipfile.ZipFile(archive) as z:
        assert z.testzip() is None
        for p in PBIP.rglob('*'):
            if p.is_file():assert z.read(str(p.relative_to(PBIP.parent)))==p.read_bytes()
    evidence={'alcance_validacion':'SQL interpretado desde MySQL con sqlglot y ejecutado en SQLite; comprobación independiente de datos; esquemas oficiales PBIP/PBIR. No ejecuta MySQL ni el motor DAX/Desktop.', 'consultas_validadas':10,'json_validados_con_esquema_oficial':schema_count,'visuales_referenciados':len(visuals),'relaciones':6,'medidas':len(measures),'metricas':expected,'comparacion_tiendas':gap,'mezcla_categorias':cats,'pendiente':'Abrir PBIP, actualizar datos y comprobar visuales/DAX en Power BI Desktop; guardar como PBIX. Ejecutar SQL en MySQL 8.0.'}
    (ROOT/'docs/validacion_correcciones.json').write_text(json.dumps(evidence,ensure_ascii=False,indent=2)+'\n')
    out=ROOT/'data/resultados';out.mkdir(exist_ok=True)
    for name,rows in [('metricas',results[7]),('comparacion_tiendas',results[8]),('mezcla_categorias',results[9]),('ventas_mensuales',results[4])]:
        with (out/f'{name}.csv').open('w',newline='',encoding='utf-8') as fp:
            w=csv.DictWriter(fp,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
    print(json.dumps({'consultas':10,'metricas':expected,'brecha':gap,'esquemas':schema_count,'visuales':len(visuals)},ensure_ascii=False))

if __name__=='__main__':main()
