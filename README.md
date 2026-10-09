# NexaMart | Análisis comercial con SQL y Power BI

**SQL · MySQL · Power BI · DAX**

**Identifiqué dónde se concentran las ventas y qué conviene revisar.** Singapore lidera el resultado; los rankings destacan productos y vendedores, y las devoluciones señalan casos para seguimiento. Las consultas SQL respaldan estas respuestas y el dashboard permite explorarlas con filtros.

NexaMart es una cadena ficticia con tiendas en **New York, London, Singapore y Sydney**. Analicé **757 registros, 31 productos y 12 meses**, de septiembre de 2025 a agosto de 2026. Los datos son simulados con fines de portafolio.

## Las respuestas que obtuve con SQL

Desarrollé **diez consultas** con JOINs, CTEs, funciones de ventana, subconsultas y agregación condicional. Estos son algunos hallazgos:

| Pregunta de negocio | Respuesta obtenida | Técnica SQL |
|---|---|---|
| ¿Qué tienda genera más ventas? | Singapore: **30.973,16 netos**. | JOIN + agregación |
| ¿Quién lidera entre los vendedores? | Cristian Santos: **16.345,58 netos**. | CTE + RANK global y por tienda |
| ¿Qué productos destacan en cada categoría? | Top 3 por categoría; Foldable Treadmill lidera en Sports & Fitness. | CTE + ROW_NUMBER particionado |
| ¿Qué mes tuvo mayores ventas? | Agosto de 2026: **10.384,06 netos**. | Agrupación temporal |
| ¿Qué medio de pago tiene mayor peso? | Credit Card: **31,26 %** del importe neto. | Subconsulta + porcentaje |
| ¿Dónde revisar devoluciones? | Fashion y Electronics reúnen **cinco de los seis casos**. | CASE + agregación condicional |

Las diez preguntas y sus respuestas están en `docs/preguntas_sql.md`; el código está en `sql/consultas_analiticas.sql`.

<details>
<summary>Ejemplo SQL: ranking global y por tienda</summary>

Una CTE reúne las ventas por vendedor. Este fragmento de la consulta 2 calcula ambos rankings sobre ese resultado:

```sql
SELECT *,
    RANK() OVER (ORDER BY ventas_netas DESC) AS ranking_global,
    RANK() OVER (
        PARTITION BY tienda_id ORDER BY ventas_netas DESC
    ) AS ranking_en_tienda
FROM ventas_por_vendedor;
```

La consulta completa está en `sql/consultas_analiticas.sql`; su evidencia original está en `capturas/04_ranking_vendedores_sql.png`.

</details>

## Cómo usaría el dashboard para decidir

### Resumen ejecutivo

Comparo tiendas y evolución mensual. Singapore supera a Sydney en **8.690,55 netos**; Sports & Fitness concentra **65,46 % de la brecha**. Empezaría por revisar surtido y disponibilidad de esa categoría en Sydney.

![Resumen ejecutivo](capturas/06_resumen_ejecutivo.png)

### Productos y vendedores

Identifico qué impulsa las ventas. Foldable Treadmill genera **16.399,59 netos** y Cristian Santos lidera entre vendedores identificados. Revisaría la disponibilidad de los productos destacados y contrastaría prácticas comerciales de los vendedores.

![Productos y vendedores](capturas/07_productos_vendedores.png)

### Regional y calidad

Vigilo pagos y devoluciones. Credit Card concentra **31,26 % del importe neto** y Fashion y Electronics reúnen cinco de los seis casos de devolución. Revisaría esos casos y mantendría seguimiento por período.

![Regional y calidad](capturas/08_regional_calidad.png)

## Cómo interpretar el resultado

**103.851,74 netos · 751 compras · Ticket promedio de 139,44.**

Las ventas netas descuentan devoluciones. El ticket es ventas brutas divididas entre compras, excluyendo devoluciones. Los importes son unidades monetarias de simulación; las recomendaciones proponen qué investigar, sin atribuir causas ni demostrar rentabilidad.

MySQL y Power BI comparten las tablas de ventas y dimensiones. Sus diagramas y correspondencia están en `docs/modelo_mysql_powerbi.md`.

## Dónde encontrar cada parte

| Carpeta | Contenido |
|---|---|
| `sql/` | Consultas comerciales, esquema, carga y controles. |
| `powerbi/` | Informe `NexaMart.pbix`, medidas y guía de uso. |
| `docs/` | Preguntas respondidas, modelo, criterios técnicos y reproducción. La conclusión comercial es una nota breve de apoyo. |
| `capturas/` y `data/` | Evidencias del proceso, datos y resultados. |
