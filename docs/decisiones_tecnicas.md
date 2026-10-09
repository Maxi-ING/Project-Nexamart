# NexaMart | Modelo y métricas del análisis

## Convención común SQL–Power BI

El SQL publicado y las 15 medidas del modelo editable usan la misma definición. Las fórmulas originales se conservan en powerbi/medidas_originales.dax para trazabilidad.

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
| Unidades Vendidas | Cantidades de eventos de venta | 1.037 |
| Unidades Netas | Suma firmada de cantidades | 1.026 |

El ticket anterior (137,19) dividía ventas netas entre 757 eventos, incluidas devoluciones. El nuevo ticket mide compras positivas. Las devoluciones no se relacionan con el pedido original; por eso la proporción de eventos no se presenta como tasa de pedidos devueltos.

## Modelo y calendario

La clave primaria order_id permite un producto por pedido. Una versión con varias líneas requiere otra clave de hecho. MySQL conserva cinco dimensiones y la relación adicional vendedor–tienda. El modelo PBIP tiene seis relaciones activas: cinco dimensiones más calendario, todas con filtro desde la dimensión hacia hechos. No hay relación adicional vendedor–tienda en Power BI.

El calendario corregido abarca años completos 2025–2026, tiene Date como clave y categoría de tabla Time. Año-Mes es texto y se ordena por AñoMesOrden. La tendencia se ordena ascendentemente por mes. La ampliación no agrega hechos: 2025 sigue teniendo datos solo desde septiembre y no permite YoY mensual completo.

Los rankings y porcentajes de pago usan ventas netas. El Top 3 SQL utiliza ROW_NUMBER y producto_id para desempatar; el ranking DAX aplica el mismo desempate. El ranking SQL por tienda usa la tienda del hecho, como el filtro del dashboard. No registrado conserva sus ventas, aunque queda fuera del ranking de vendedores identificados.

## Explicación comercial

Las consultas 9 y 10 descomponen la brecha Singapore–Sydney por volumen y ticket, y muestran contribuciones por categoría. La descomposición simétrica reparte la interacción entre volumen y ticket. La suma concilia con 8.690,55 netos. El desglose por categoría es otra lectura de esa misma brecha y no se añade a los factores anteriores.

La conclusión y sus recomendaciones están en [conclusion_comercial.md](conclusion_comercial.md).

## Trazabilidad y validación

El PBIX original y las diez capturas conservan sus bytes. El snapshot recuperado confirma 757 hechos, referencias a dimensiones, signos, precios y cantidades. Su manifiesto describe el archivo original; el calendario de 365 días del snapshot no es el calendario ampliado del PBIP.

El proyecto [PBIP](../powerbi/README.md) reutiliza las tres páginas y el tema original, con calendario, medidas y referencias de visuales revisados. Incluye modo Snapshot portátil y modo MySQL mediante parámetros. La conexión principal continúa siendo MySQL en modo Import.

[validacion_correcciones.json](validacion_correcciones.json) registra el alcance real: diez consultas interpretadas con dialecto MySQL y ejecutadas mediante adaptación a SQLite, conciliación independiente de resultados y validación estructural del PBIP/PBIR. No equivale a ejecutar DAX/Desktop o MySQL 8.0. La apertura, actualización y guardado del PBIX final requieren Desktop.

Los datos son simulados y los importes no tienen conversión de divisas documentada. Sin costos, stock, tráfico u horas no se infiere rentabilidad, causalidad o productividad. Seis devoluciones no bastan para atribuir fallas sistemáticas. El mapa original muestra presencia geográfica.

La preparación en Python se documentó en el origen. El CSV sucio y el ETL original no se recuperaron; la reproducción comienza en los datos importados del PBIX. Ese alcance no impide revisar las consultas comerciales.
