# NexaMart | Criterios del modelo y las métricas

**SQL y Power BI comparten las mismas definiciones para comparar resultados con claridad.** Separé ventas, devoluciones y compras para que cada indicador responda una pregunta concreta.

## Métricas del análisis

| Indicador | Cómo lo interpreto | Resultado |
|---|---|---:|
| Ventas brutas | Importe de las ventas antes de descontar devoluciones | 104.718,63 |
| Importe devuelto | Valor de las devoluciones, presentado positivo | 866,89 |
| Ventas netas | Ventas brutas menos importe devuelto | 103.851,74 |
| Compras | Pedidos de venta, sin eventos de devolución | 751 |
| Ticket promedio | Ventas brutas divididas entre compras | 139,44 |
| Total de eventos | Ventas y devoluciones registradas | 757 |
| Devoluciones | Eventos identificados como devolución | 6 |
| Proporción de devoluciones | Devoluciones divididas entre eventos | 0,79 % |
| Unidades netas | Cantidades vendidas menos cantidades devueltas | 1.026 |

Los rankings y la participación de pagos utilizan **ventas netas**. El ticket mide el importe medio de una compra; las devoluciones quedan fuera de su denominador. La proporción de devoluciones mide eventos, porque no existe un vínculo con el pedido original.

## Modelo y comparaciones

En esta versión, `order_id` identifica un evento con un producto. Un pedido con varias líneas necesitaría otra clave de detalle.

MySQL contiene ventas y cinco dimensiones. Power BI conecta esas dimensiones y el calendario a ventas, con seis relaciones activas. La asignación vendedor–tienda permanece en MySQL; en el informe, ambas dimensiones filtran ventas directamente.

El calendario abarca 2025–2026, pero las ventas cubren septiembre de 2025 a agosto de 2026. Por eso no hay un año anterior completo para comparar.

SQL utiliza `ROW_NUMBER` con identificador de producto para resolver empates. El PBIX utiliza `RANKX`; los primeros puestos actuales coinciden. Los registros sin identificación se conservan, aunque “No registrado” queda fuera del ranking de vendedores.

Las consultas 9 y 10 profundizan la diferencia Singapore–Sydney. Volumen y ticket explican la brecha; las categorías muestran dónde se concentra. Son dos lecturas del mismo resultado y no se suman entre sí.

## Trazabilidad y validación

- **Origen:** datos recuperados del PBIX; las seis tablas base y los 757 eventos se conservaron. El archivo inicial está en `powerbi/historico/`.
- **Comprobación:** concilié las diez consultas mediante adaptación a SQLite y revisé datos, fórmulas, relaciones y capturas. Este control no ejecuta MySQL ni DAX/Desktop.
- **Respaldo:** `docs/revision_pbix_actualizado.json` registra el PBIX actual; `docs/validacion_correcciones.json`, el proyecto PBIP alternativo. Este último se validó estructuralmente.

## Alcance del caso

Los datos son simulados. Sin costos, stock o tráfico, las recomendaciones orientan una revisión comercial y no demuestran rentabilidad o causas. La reproducción parte de los datos importados; el CSV sucio y el ETL original no están incluidos.

Los diagramas y la corrección de la revisión del calendario están explicados en `docs/modelo_mysql_powerbi.md`. Las fórmulas actuales están en `powerbi/medidas_actuales.dax` y la conclusión breve en `docs/conclusion_comercial.md`.
