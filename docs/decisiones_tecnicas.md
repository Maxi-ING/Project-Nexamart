# NexaMart | Modelo y métricas del análisis

## Convención común SQL–Power BI

El SQL publicado y el PBIX actualizado usan las mismas definiciones de bruto, importe devuelto, neto, compras y ticket. El archivo actual contiene 14 medidas; el PBIP alternativo tiene 15. Las fórmulas extraídas están en powerbi/medidas_actuales.dax; las originales se conservan para trazabilidad.

| Métrica | Definición | Resultado |
|---|---|---:|
| Ventas Brutas | Importe de eventos es_devolucion = false | 104.718,63 |
| Importe Devoluciones | Negativo de la suma de los eventos de devolución | 866,89 |
| Ventas Netas | Suma firmada de todos los importes; equivale a bruto − devuelto | 103.851,74 |
| Pedidos Venta | DISTINCTCOUNT(order_id) solo en ventas | 751 |
| Ticket Promedio | Ventas Brutas / Pedidos Venta | 139,44 |
| Total Eventos | Todas las claves order_id | 757 |
| Total Devoluciones | Eventos es_devolucion = true | 6 |
| Proporción Eventos Devolución | Total Devoluciones / Total Eventos | 0,79 % |
| Unidades Vendidas (nombre en PBIX actual) | Suma firmada: representa unidades netas | 1.026 |

El ticket anterior (137,19) dividía ventas netas entre 757 eventos, incluidas devoluciones. El nuevo ticket mide compras positivas. Las devoluciones no se relacionan con el pedido original; por eso la proporción de eventos no se presenta como tasa de pedidos devueltos.

## Modelo y calendario

La clave primaria order_id permite un producto por pedido. Una versión con varias líneas requiere otra clave de hecho. MySQL conserva cinco dimensiones y la relación adicional vendedor–tienda. Tanto el PBIX actual como el PBIP alternativo tienen seis relaciones activas: cinco dimensiones más calendario, todas con filtro desde la dimensión hacia hechos. No hay relación adicional vendedor–tienda en Power BI.

El calendario del PBIX actual abarca años completos 2025–2026. La propuesta PBIP añade la configuración explícita de Date como clave, categoría de tabla Time y Año-Mes como texto ordenado por AñoMesOrden, con tendencia ascendente por mes. La ampliación no agrega hechos: 2025 sigue teniendo datos solo desde septiembre y no permite YoY mensual completo.

Los rankings y porcentajes de pago usan ventas netas. El Top 3 SQL utiliza ROW_NUMBER y producto_id para desempatar; el PBIP alternativo aplica el mismo desempate. El PBIX actual conserva RANKX sin desempate; los primeros puestos mostrados coinciden y no tienen empates. El ranking SQL por tienda usa la tienda del hecho, como el filtro del dashboard. No registrado conserva sus ventas, aunque queda fuera del ranking de vendedores identificados.

## Explicación comercial

Las consultas 9 y 10 descomponen la brecha Singapore–Sydney por volumen y ticket, y muestran contribuciones por categoría. La descomposición simétrica reparte la interacción entre volumen y ticket. La suma concilia con 8.690,55 netos. El desglose por categoría es otra lectura de esa misma brecha y no se añade a los factores anteriores.

La conclusión y sus recomendaciones están en [conclusion_comercial.md](conclusion_comercial.md).

## Trazabilidad y validación

El PBIX inicial se conserva en powerbi/historico. Se actualizaron cuatro capturas con la evidencia del 9 de octubre. Las seis tablas de origen no cambiaron; el snapshot confirma 757 hechos, referencias, signos, precios y cantidades. Su manifiesto describe el archivo inicial; su calendario de 365 días difiere de los 730 del PBIX actual.

El proyecto [PBIP](../powerbi/README.md) reutiliza las tres páginas y el tema original, con calendario, medidas y referencias de visuales revisados. Incluye modo Snapshot portátil y modo MySQL mediante parámetros. La conexión principal continúa siendo MySQL en modo Import.

[validacion_correcciones.json](validacion_correcciones.json) registra el alcance real: diez consultas interpretadas con dialecto MySQL y ejecutadas mediante adaptación a SQLite, conciliación independiente de resultados y validación estructural del PBIP/PBIR. No equivale a ejecutar DAX/Desktop o MySQL 8.0. El autor aportó un nuevo PBIX guardado y capturas de Desktop que muestran los KPIs corregidos. La ejecución local del PBIP alternativo sigue pendiente; este entorno inspecciona el archivo y no evalúa DAX.

Los datos son simulados y los importes no tienen conversión de divisas documentada. Sin costos, stock, tráfico u horas no se infiere rentabilidad, causalidad o productividad. Seis devoluciones no bastan para atribuir fallas sistemáticas. El mapa original muestra presencia geográfica.

La preparación en Python se documentó en el origen. El CSV sucio y el ETL original no se recuperaron; la reproducción comienza en los datos importados del PBIX. Ese alcance no impide revisar las consultas comerciales.

## Relación entre los modelos y corrección de extracción

[modelo_mysql_powerbi.md](modelo_mysql_powerbi.md) compara el esquema físico con las relaciones semánticas, con ambas capturas. La relación calendario–ventas estaba activa en el archivo inicial y en el actualizado. PBIXRay.relationships la omitía por el filtro SystemFlags=0; se corrigió el extractor para incluir tablas calculadas. El archivo actual conserva Año-Mes como fecha y el criterio PBIR de orden por importe; la guía recoge cómo guardar la configuración mensual explícita.
