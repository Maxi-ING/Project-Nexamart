# Snapshot recuperado de Power BI

Los CSV se extrajeron del modelo importado de `powerbi/NexaMart.pbix`. Conservan los datos del informe; no son el CSV crudo ni una exportación del ETL original.

| Archivo | Grano | Filas |
|---|---|---:|
| dimtienda.csv | Una tienda | 4 |
| dimvendedor.csv | Un vendedor; incluye «No registrado» | 9 |
| dimproducto.csv | Un producto | 31 |
| dimcliente.csv | Un cliente; incluye «No registrado» | 171 |
| dimmetodopago.csv | Un método | 5 |
| factventas.csv | Un evento con un producto y order_id único | 757 |
| dimcalendario.csv | Un día del período operativo | 365 |

Los importes tienen dos decimales; las fechas, formato ISO. es_devolucion se conserva como booleano en CSV y se convierte a 0/1 en la carga MySQL.

El manifiesto registra SHA-256 del PBIX y controles de claves, integridad dimensional, signos, precio por cantidad y conciliación. El script de extracción permite repetir el proceso. Los datos y correos son simulados, según el contexto del autor.

El calendario de este snapshot conserva los 365 días originales. El modelo PBIP revisado genera años completos 2025–2026 y utiliza los mismos 757 hechos. Las métricas actuales están en [decisiones_tecnicas.md](../../docs/decisiones_tecnicas.md).
