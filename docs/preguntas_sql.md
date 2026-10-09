# NexaMart | Diez preguntas comerciales respondidas con SQL

Cada pregunta corresponde al número de consulta en `sql/consultas_analiticas.sql`. Los resultados abarcan las cuatro tiendas y todo el período; las consultas 9 y 10 profundizan una comparación concreta.

| Consulta y pregunta | Respuesta del análisis | Para qué sirve | Técnica SQL |
|---|---|---|---|
| **1. ¿Qué tiendas generan más ventas?** | Singapore: 30.973,16 netos; London: 26.854,34; New York: 23.741,63; Sydney: 22.282,61. | Comparar tiendas y elegir dónde profundizar. | JOIN, SUM y CASE |
| **2. ¿Quién lidera globalmente y por tienda?** | Cristian Santos ocupa el primer puesto global y en Singapore, con 16.345,58 netos. | Identificar referentes y preparar una revisión del desempeño comercial. | CTE + RANK con particiones |
| **3. ¿Qué tres productos destacan por categoría?** | Foldable Treadmill lidera Sports & Fitness; Tablet 10-inch, Electronics; Robot Vacuum Cleaner, Smart Home; Running Sneakers Lightweight, Fashion; Electric Trimmer Kit, Beauty & Personal Care. | Priorizar la revisión del surtido dentro de cada categoría. | CTE + ROW_NUMBER |
| **4. ¿Qué participación tiene cada método de pago?** | Credit Card: 31,26 %; Digital Wallet: 26,70 %; Debit Card: 20,14 %; PayPal: 13,43 %; Cash: 8,47 % del importe neto. | Dar seguimiento a los medios de pago de mayor peso. | JOIN + subconsulta escalar |
| **5. ¿Cómo evolucionan ventas y pedidos?** | Agosto de 2026 es el mes de mayor importe neto: 10.384,06, con 69 compras. La consulta devuelve los 12 meses. | Localizar períodos destacados y revisar su composición. | Agrupación por mes |
| **6. ¿Qué clientes VIP acumulan mayor gasto?** | Adrian Ferguson lidera el Top 10 VIP con 1.849,90 netos y seis compras. | Identificar clientes para una propuesta de fidelización. | CTE + segmentación + LIMIT |
| **7. ¿Qué categorías presentan más devoluciones?** | Fashion: 2/133 eventos (1,50 %); Electronics: 3/208 (1,44 %); Sports & Fitness: 1/144 (0,69 %). | Revisar casos concretos y observar su evolución. | CASE + agregación condicional |
| **8. ¿Concilian los indicadores?** | 104.718,63 brutos − 866,89 devueltos = 103.851,74 netos. Son 751 compras; el ticket es 139,44. | Comparar SQL y Power BI con definiciones consistentes. | CASE + conteo distinto |
| **9. ¿Qué explica la brecha Singapore–Sydney?** | Diferencia neta de 8.690,55: 6.160,11 de contribución del ticket, 2.857,39 del volumen y −326,95 de devoluciones. | Distinguir cantidad de compras e importe por compra antes de decidir. | CTEs + descomposición |
| **10. ¿Qué categorías concentran esa brecha?** | Sports & Fitness aporta 5.688,99 (65,46 %), con 37 compras en cada tienda. Smart Home aporta 2.619,79. | Enfocar una revisión de catálogo y disponibilidad en Sydney. | CASE + ventanas de participación |

## Del resultado a la decisión

El dashboard permite explorar tiendas, productos, vendedores, fechas y pagos. La comparación Singapore–Sydney ilustra cómo profundizar una diferencia: primero localizarla, después separar volumen y ticket y finalmente identificar categorías para investigar.

La conclusión breve está en `docs/conclusion_comercial.md`; el informe está en `powerbi/NexaMart.pbix`.

## Cómo interpretar las cifras

Rankings y participaciones utilizan ventas netas. Las compras excluyen eventos de devolución; el ticket es ventas brutas / compras. La proporción de devolución mide eventos, no pedidos originales devueltos. Los datos son simulados y las acciones propuestas no demuestran causas, productividad o rentabilidad.

Los resultados completos están en `data/resultados/respuestas_sql.json`. Se obtuvieron adaptando el SQL MySQL a SQLite sobre los datos del informe; esta comprobación no sustituye la ejecución nativa en MySQL.
