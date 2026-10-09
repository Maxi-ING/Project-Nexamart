"""Reconstruye el informe PBIR y un modelo PBIP corregido; no modifica el PBIX binario."""
import base64
import csv
import json
from pathlib import Path
import zipfile

ROOT = Path(__file__).resolve().parents[1]
DEST = ROOT / 'powerbi' / 'NexaMart_corregido'
REPORT = DEST / 'NexaMart.Report'
MODEL = DEST / 'NexaMart.SemanticModel'

def write_json(path, obj):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')

def measure(name, expression, fmt='#,0.00', folder='Indicadores'):
    return dict(name=name, expression=expression, formatString=fmt, displayFolder=folder)

F = "'nexamart factventas'"
P = "'nexamart dimproducto'"
V = "'nexamart dimvendedor'"
MEASURES = [
    measure('Ventas Brutas', f'CALCULATE(SUM({F}[precio_total]), KEEPFILTERS({F}[es_devolucion] = FALSE()))'),
    measure('Importe Devoluciones', f'COALESCE(-CALCULATE(SUM({F}[precio_total]), KEEPFILTERS({F}[es_devolucion] = TRUE())), 0)'),
    measure('Ventas Netas', f'SUM({F}[precio_total])'),
    measure('Pedidos Venta', f'CALCULATE(DISTINCTCOUNT({F}[order_id]), KEEPFILTERS({F}[es_devolucion] = FALSE()))', '#,0'),
    measure('Total Eventos', f'DISTINCTCOUNT({F}[order_id])', '#,0', 'Calidad'),
    measure('Ticket Promedio', 'DIVIDE([Ventas Brutas], [Pedidos Venta])'),
    measure('Unidades Vendidas', f'CALCULATE(SUM({F}[cantidad]), KEEPFILTERS({F}[es_devolucion] = FALSE()))', '#,0'),
    measure('Unidades Netas', f'SUM({F}[cantidad])', '#,0'),
    measure('Total Devoluciones', f'CALCULATE([Total Eventos], KEEPFILTERS({F}[es_devolucion] = TRUE()))', '#,0', 'Calidad'),
    measure('Proporción Eventos Devolución', 'DIVIDE([Total Devoluciones], [Total Eventos])', '0.00%', 'Calidad'),
    measure('Ventas Mes Anterior', 'CALCULATE([Ventas Netas], DATEADD(DimCalendario[Date], -1, MONTH))', folder='Tiempo'),
    measure('% Crecimiento MoM', 'IF(NOT ISBLANK([Ventas Netas]) && NOT ISBLANK([Ventas Mes Anterior]), DIVIDE([Ventas Netas] - [Ventas Mes Anterior], [Ventas Mes Anterior]))', '0.00%', 'Tiempo'),
    measure('Ventas YTD', 'IF(NOT ISBLANK([Ventas Netas]), TOTALYTD([Ventas Netas], DimCalendario[Date]))', folder='Tiempo'),
    measure('Ranking Vendedor', f'''VAR IdActual = SELECTEDVALUE({V}[vendedor_id])
VAR Candidatos = FILTER(ALL({V}[vendedor_id], {V}[nombre_vendedor]), {V}[vendedor_id] <> -1)
RETURN IF(NOT ISBLANK(IdActual) && IdActual <> -1 && NOT ISBLANK([Ventas Netas]), RANKX(Candidatos, CALCULATE([Ventas Netas]), [Ventas Netas], DESC, SKIP))''', '0', 'Rankings'),
    measure('Ranking Producto en Categoría', f'''VAR CategoriaActual = SELECTEDVALUE({P}[categoria])
VAR IdActual = SELECTEDVALUE({P}[producto_id])
VAR ImporteActual = [Ventas Netas]
VAR Candidatos = FILTER(ALL({P}), {P}[categoria] = CategoriaActual)
VAR Puesto = RANKX(Candidatos, CALCULATE([Ventas Netas]), ImporteActual, DESC, SKIP)
VAR Desempate = COUNTROWS(FILTER(Candidatos, CALCULATE([Ventas Netas]) = ImporteActual && {P}[producto_id] < IdActual))
RETURN IF(NOT ISBLANK(IdActual) && NOT ISBLANK(ImporteActual), Puesto + Desempate)''', '0', 'Rankings'),
]

TYPES = {
    'dimtienda': [('tienda_id','int64'),('nombre_tienda','string'),('ciudad','string'),('pais','string'),('region','string')],
    'dimvendedor': [('vendedor_id','int64'),('nombre_vendedor','string'),('tienda_id','int64')],
    'dimproducto': [('producto_id','int64'),('nombre_producto','string'),('categoria','string'),('precio_unitario','decimal')],
    'dimcliente': [('cliente_id','int64'),('nombre_cliente','string'),('email','string'),('segmento','string')],
    'dimmetodopago': [('metodo_pago_id','int64'),('nombre_metodo','string')],
    'factventas': [('order_id','int64'),('fecha','dateTime'),('tienda_id','int64'),('vendedor_id','int64'),('cliente_id','int64'),('producto_id','int64'),('metodo_pago_id','int64'),('cantidad','int64'),('precio_unitario','decimal'),('precio_total','decimal'),('es_devolucion','boolean')],
}

def make_table(name, cols):
    rows = []
    with (ROOT/'data/snapshot'/f'{name}.csv').open(encoding='utf-8-sig', newline='') as fp:
        for r in csv.DictReader(fp):
            row = []
            for c,t in cols:
                s=r[c]
                row.append(None if s == '' else int(s) if t=='int64' else float(s) if t=='decimal' else s.lower() in ('true','1') if t=='boolean' else s[:10] if t=='dateTime' else s)
            rows.append(row)
    encoded=base64.b64encode(json.dumps(rows,ensure_ascii=False,separators=(',',':')).encode()).decode()
    mtypes={'int64':'Int64.Type','decimal':'Currency.Type','string':'type text','dateTime':'type date','boolean':'type logical'}
    colnames=json.dumps([c for c,_ in cols],ensure_ascii=False).replace('[','{').replace(']','}')
    transforms=', '.join('{"'+c+'", '+mtypes[t]+'}' for c,t in cols)
    expr=f'''let
    Fuente = if pModo = "MySQL" then MySQL.Database(pServidor, pBase, [ReturnSingleDatabase=true]){{[Schema=pBase, Item="{name}"]}}[Data]
             else Table.FromRows(Json.Document(Binary.FromText("{encoded}", BinaryEncoding.Base64)), {colnames}),
    Tipos = Table.TransformColumnTypes(Fuente, {{{transforms}}}, "en-US")
in
    Tipos'''
    columns=[]
    for c,t in cols:
        col=dict(name=c,dataType=t,sourceColumn=c,summarizeBy='none')
        if c.endswith('_id'): col['isHidden']=True
        if t=='decimal': col['formatString']='#,0.00'
        if t=='dateTime': col['formatString']='yyyy-MM-dd'
        if c in ('ciudad','pais'): col['dataCategory']='City' if c=='ciudad' else 'Country'
        columns.append(col)
    return dict(name='nexamart '+name,columns=columns,partitions=[dict(name=name,mode='import',source=dict(type='m',expression=expr))])

def rename(obj):
    replacements={'Ventas Totales':'Ventas Netas','Total Pedidos':'Pedidos Venta','% Tasa Devolución':'Proporción Eventos Devolución','Tasa de devolución':'Proporción de eventos de devolución'}
    if isinstance(obj,dict):return {k:rename(v) for k,v in obj.items()}
    if isinstance(obj,list):return [rename(v) for v in obj]
    if isinstance(obj,str):
        for a,b in replacements.items():obj=obj.replace(a,b)
    return obj

def main():
    tables=[make_table(n,cs) for n,cs in TYPES.items()]
    calendar='''ADDCOLUMNS(CALENDAR(DATE(2025,1,1), DATE(2026,12,31)),
    "Año", YEAR([Date]), "Mes Número", MONTH([Date]),
    "Mes Nombre", FORMAT([Date], "MMMM"), "Año-Mes", FORMAT([Date], "yyyy-MM"),
    "AñoMesOrden", YEAR([Date]) * 100 + MONTH([Date]))'''
    calcols=[]
    for n,t in [('Date','dateTime'),('Año','int64'),('Mes Número','int64'),('Mes Nombre','string'),('Año-Mes','string'),('AñoMesOrden','int64')]:
        c=dict(type='calculatedTableColumn',name=n,dataType=t,isNameInferred=False,isDataTypeInferred=False,sourceColumn='['+n+']',summarizeBy='none')
        if n=='Date':c.update(isKey=True,formatString='yyyy-MM-dd')
        if n=='Año-Mes':c['sortByColumn']='AñoMesOrden'
        if n=='Mes Nombre':c['sortByColumn']='Mes Número'
        if n=='AñoMesOrden':c['isHidden']=True
        calcols.append(c)
    tables.append(dict(name='DimCalendario',dataCategory='Time',columns=calcols,partitions=[dict(name='DimCalendario',mode='import',source=dict(type='calculated',expression=calendar))]))
    tables.append(dict(name='Medidas',columns=[dict(type='calculatedTableColumn',name='Column',dataType='int64',isHidden=True,isNameInferred=False,isDataTypeInferred=False,sourceColumn='[Column]')],partitions=[dict(name='Medidas',mode='import',source=dict(type='calculated',expression='ROW("Column", BLANK())'))],measures=MEASURES))
    relationships=[]
    for n,key in [('dimtienda','tienda_id'),('dimvendedor','vendedor_id'),('dimproducto','producto_id'),('dimcliente','cliente_id'),('dimmetodopago','metodo_pago_id')]:
        relationships.append(dict(name='ventas_'+key,fromTable='nexamart factventas',fromColumn=key,toTable='nexamart '+n,toColumn=key,fromCardinality='many',toCardinality='one',crossFilteringBehavior='oneDirection',isActive=True))
    relationships.append(dict(name='ventas_calendario',fromTable='nexamart factventas',fromColumn='fecha',toTable='DimCalendario',toColumn='Date',fromCardinality='many',toCardinality='one',crossFilteringBehavior='oneDirection',isActive=True))
    expressions=[dict(name='pModo',kind='m',expression='"Snapshot" meta [IsParameterQuery=true, List={"Snapshot", "MySQL"}, DefaultValue="Snapshot", Type="Text", IsParameterQueryRequired=true]'),dict(name='pServidor',kind='m',expression='"localhost:3306" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]'),dict(name='pBase',kind='m',expression='"nexamart" meta [IsParameterQuery=true, Type="Text", IsParameterQueryRequired=true]')]
    model=dict(name='NexaMart',compatibilityLevel=1601,model=dict(culture='es-PE',defaultPowerBIDataSourceVersion='powerBI_V3',sourceQueryCulture='en-US',tables=tables,relationships=relationships,expressions=expressions,annotations=[dict(name='__PBI_TimeIntelligenceEnabled',value='0')]))
    write_json(MODEL/'model.bim',model)
    write_json(MODEL/'definition.pbism',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/semanticModel/definitionProperties/1.0.0/schema.json','version':'1.0','settings':{'qnaEnabled':False}})
    write_json(DEST/'NexaMart.pbip',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/pbip/pbipProperties/1.0.0/schema.json','version':'1.0','artifacts':[{'report':{'path':'NexaMart.Report'}}],'settings':{'enableAutoRecovery':True}})
    write_json(REPORT/'definition.pbir',{'$schema':'https://developer.microsoft.com/json-schemas/fabric/item/report/definitionProperties/2.0.0/schema.json','version':'4.0','datasetReference':{'byPath':{'path':'../NexaMart.SemanticModel'}}})
    with zipfile.ZipFile(ROOT/'powerbi/NexaMart.pbix') as z:
        for n in z.namelist():
            if not n.startswith('Report/'):continue
            dst=REPORT/n.removeprefix('Report/')
            if n.endswith('.json'):
                obj=rename(json.loads(z.read(n)))
                if n.endswith('pages.json'):obj['activePageName']=obj['pageOrder'][0]
                if n.endswith('visual.json') and obj.get('visual',{}).get('visualType')=='lineChart':
                    obj['visual']['query']['sortDefinition']={'sort':[{'field':{'Column':{'Expression':{'SourceRef':{'Entity':'DimCalendario'}},'Property':'Año-Mes'}},'direction':'Ascending'}],'isDefaultSort':False}
                if n.endswith('visual.json') and obj.get('visual',{}).get('visualType')=='barChart' and 'dimtienda.nombre_tienda' in json.dumps(obj) and 'Series' not in obj['visual']['query']['queryState']:
                    obj['visual']['query']['queryState']['Tooltips']={'projections':[{'field':{'Measure':{'Expression':{'SourceRef':{'Entity':'Medidas'}},'Property':m}},'queryRef':'Medidas.'+m,'nativeQueryRef':m} for m in ['Ventas Brutas','Importe Devoluciones','Pedidos Venta','Ticket Promedio']]}
                write_json(dst,obj)
            else:dst.parent.mkdir(parents=True,exist_ok=True);dst.write_bytes(z.read(n))
    # Cinco KPIs explícitos; se conserva la distribución de tres páginas.
    page=REPORT/'definition/pages/b3378b6972cd49c06c0e/visuals'
    net=page/'f9a112b04cd7c5bb5580/visual.json'
    prototype=json.loads(net.read_text())
    ids=['kpi_brutas','kpi_devoluciones','f9a112b04cd7c5bb5580','bf817f2997de384a4831','dd907bf58ba6c8ac6a39']
    for i,(id_,name) in enumerate(zip(ids,['Ventas Brutas','Importe Devoluciones','Ventas Netas','Pedidos Venta','Ticket Promedio'])):
        card=json.loads(json.dumps(prototype));card['name']=id_;card['position'].update(x=756,y=103+i*72,width=451,height=66,z=i*1000,tabOrder=i*1000)
        card['visual']['query']['queryState']['Values']['projections']=[{'field':{'Measure':{'Expression':{'SourceRef':{'Entity':'Medidas'}},'Property':name}},'queryRef':'Medidas.'+name,'nativeQueryRef':name}]
        title=name+' (UM)' if name not in ('Pedidos Venta',) else name
        card['visual']['visualContainerObjects']['title'][0]['properties']['text']['expr']['Literal']['Value']="'"+title+"'"
        card['visual']['objects']['labels'][0]['properties']['fontSize']={'expr':{'Literal':{'Value':'22D'}}}
        card['visual']['visualContainerObjects']['title'][0]['properties']['fontSize']={'expr':{'Literal':{'Value':'12D'}}}
        write_json(page/id_/'visual.json',card)
    (DEST/'.gitignore').write_text('**/.pbi/localSettings.json\n**/.pbi/cache.abf\n',encoding='utf-8')
    (ROOT/'powerbi/medidas_corregidas.dax').write_text('// Modelo corregido: mismas definiciones que sql/consultas_analiticas.sql.\n\n'+'\n\n'.join(m['name']+' =\n'+m['expression'] for m in MEASURES)+'\n',encoding='utf-8')
    write_json(ROOT/'powerbi/relaciones_corregidas.json',relationships)
    with zipfile.ZipFile(ROOT/'powerbi/NexaMart_corregido.zip','w',zipfile.ZIP_DEFLATED) as z:
        for p in sorted(DEST.rglob('*')):
            if p.is_file():z.write(p,p.relative_to(DEST.parent))
    print('PBIP generado:',DEST,'; medidas:',len(MEASURES),'; relaciones:',len(relationships))

if __name__=='__main__':main()
