# NexaMart | Decisiones técnicas y definición de métricas

## Evidencia y trazabilidad

La publicación combina el resumen del autor, el DDL y las siete consultas compartidas, diez capturas y el PBIX original. Se recuperaron seis tablas de origen, calendario, **once medidas DAX**, relaciones y paleta con PBIXRay 0.15.5.

El [manifiesto](../data/snapshot/manifest.json) registra el SHA-256 del PBIX, conteos, controles e importes en centavos. El archivo publicado conserva los bytes del adjunto. La extracción inspecciona datos y metadatos; no ejecuta el motor DAX ni equivale a abrir Power BI Desktop.

## 1. ETL documentado y datos comprobados

El proceso descrito usa Python y Faker, normaliza tres formatos de fecha y texto, elimina cinco duplicados y aparta tres cantidades atípicas. La conciliación descrita es **765 − 5 − 3 = 757**.

El PBIX confirma 757 hechos, 31 productos, cuatro tiendas, cinco métodos de pago, 171 miembros de cliente y nueve de vendedor. Clientes y vendedores incluyen «No registrado». Diez hechos usan cliente -1, seis usan vendedor -1 y seis son devoluciones.

Se verificaron claves únicas, referencias a las cinco dimensiones, tiendas de vendedores, signos de devolución y precio × cantidad = importe. Los importes se conciliaron en centavos.

El snapshot no recupera el CSV sucio, duplicados retirados, outliers apartados, generador, semillas ni ETL original. Esos archivos siguen pendientes; la reproducción disponible comienza en el estado importado.

## 2. Grano y modelo

La clave primaria order_id permite un producto por pedido. Una ampliación a pedidos con varias líneas requeriría una clave independiente de línea.

MySQL conserva cinco dimensiones y una relación adicional vendedor-tienda. El modelo extraído del PBIX contiene **cinco relaciones base activas**, de muchos a uno y filtro único desde dimensiones hacia hechos. No conserva la relación vendedor-tienda.

Los nombres físicos de tablas SQL se publican en minúsculas para coincidir con las consultas MySQL del PBIX y evitar diferencias de mayúsculas entre entornos.

## 3. Calendario y diferencias entre versiones

La expresión original de DimCalendario usa CALENDAR entre septiembre de 2025 y agosto de 2026: **365 días**. El calendario y su expresión se publican.

**La captura muestra una relación de calendario a ventas que falta en los metadatos del PBIX adjunto.** Antes de validar tendencia, MoM y YTD, debe crearse una relación activa DimCalendario[Date] (1) → nexamart factventas[fecha] (*), con filtro desde calendario, y marcar la tabla de fechas.

El gráfico de tendencia registra orden por ventas descendente; debe ajustarse a fecha ascendente. El calendario operativo no contiene años naturales completos: YTD de 2025 solo dispone de septiembre-diciembre. No hay YoY mensual completo.

El mapa original usa ciudad como ubicación, sin una medida de ventas en el tamaño de puntos; se interpreta como presencia geográfica.

## 4. DAX original

Las expresiones están en [medidas_originales.dax](../powerbi/medidas_originales.dax).

| Medida | Regla |
|---|---|
| Ventas Totales | SUM(precio_total), con devoluciones |
| Unidades Vendidas | SUM(cantidad), unidades netas |
| Total Pedidos | DISTINCTCOUNT(order_id), incluye devoluciones |
| Ticket Promedio | Ventas Totales / Total Pedidos |
| Ventas Mes Anterior | CALCULATE y DATEADD |
| % Crecimiento MoM | Variación respecto del mes anterior |
| Ventas YTD | TOTALYTD |
| Ranking Vendedor | RANKX con ALL(nombre_vendedor) |
| Ranking Producto en Categoría | RANKX con ALLEXCEPT(..., categoria) |
| Total Devoluciones | Conteo de pedidos con booleano TRUE() |
| % Tasa Devolución | Total Devoluciones / Total Pedidos |

SQL compara es_devolucion con 1; Power BI lo importa como booleano. RANKX depende del contexto y puede asignar puestos empatados; ROW_NUMBER con desempate limita a tres filas. No se reescribieron las medidas originales.

## 5. Métricas conciliadas

| Indicador | Valor |
|---|---:|
| Eventos y order_id distintos | 757 |
| Eventos de venta / devolución | 751 / 6 |
| Ventas sin devoluciones | 104.718,63 |
| Importe de devoluciones | −866,89 |
| Ventas netas | 103.851,74 |
| Unidades netas | 1.026 |
| Ticket original: neto / 757 | 137,19 |
| Ticket de ventas positivas: 104.718,63 / 751 | 139,44 |
| Proporción de devoluciones: 6 / 757 | 0,79 % |

**104.718,63 − 866,89 = 103.851,74.** El DAX original suma importes negativos; el SQL comercial los excluye.

Smartwatch Series X tiene una devolución de **249,99**, que explica **10.499,58 − 249,99 = 10.249,59**. Esta causa se comprobó en los registros del PBIX.

El ticket original divide neto entre eventos, incluidas devoluciones. La tasa mide eventos de devolución sobre todos los eventos; no unidades ni pedidos originales devueltos. No existe un vínculo entre devolución y compra original.

Los importes son unidades monetarias de simulación. No se documentaron divisas ni conversión entre países. Sin costos, metas o inventario no se infiere rentabilidad.

## 6. SQL y validación

El esquema parte del DDL compartido. La nueva carga se generó con los datos importados del PBIX, respetando claves y dependencias. **No es la carga original del ETL.** Los INSERT se agrupan hasta en 100 filas y no borran ni reemplazan datos.

Las siete consultas conservan las preguntas originales, con agrupación por identificador, desempates y NULLIF. El ranking por tienda usa la asignación de vendedor; la movilidad histórica requeriría otro modelo.

La vista vw_ventas_analitico es una definición propuesta; el DDL original no se recibió. Usa LEFT JOIN y conserva devoluciones. CREATE VIEW evita sobrescribir una vista existente.

Los conteos, claves, signos e importes se verificaron mediante extracción y controles locales. La ejecución en MySQL y la evaluación DAX en Desktop requieren validación local. Las capturas SQL respaldan la versión original.

## 7. Hallazgos e identidad visual

- Singapore concentra **30.973,16 netos**.
- Cristian Santos lidera entre vendedores identificados con **16.345,58 netos**.
- Foldable Treadmill concentra **16.399,59 netos**, el mayor importe por producto.
- La captura filtrada por Electronics muestra a Abigail Shaffer liderando.
- Se observan seis devoluciones y mayor proporción en Fashion.

Los hallazgos orientan preguntas comerciales; no prueban productividad ajustada por horas ni causas de devolución. Seis casos son una muestra pequeña para atribuir problemas sistemáticos.

La paleta extraída recupera ocho dataColors. El diseño completo permanece en el PBIX; no se inventaron estilos adicionales. La entrega incorpora PBIX, DAX, calendario, relaciones, paleta, siete CSV, manifiesto, carga SQL, controles y utilidad de extracción.
