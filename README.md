# NexaMart | Análisis comercial con SQL y Power BI

**SQL · MySQL · Power BI · DAX**

¿Qué tiendas venden más, qué productos impulsan el resultado y dónde conviene actuar? Este proyecto utiliza **SQL para responder preguntas comerciales** y un **dashboard de Power BI para explorar los resultados y apoyar decisiones**.

NexaMart es una cadena ficticia con tiendas en **New York, London, Singapore y Sydney**. El análisis reúne **757 registros, 31 productos y 12 meses**, de septiembre de 2025 a agosto de 2026. Datos simulados con fines de portafolio.

[Explorar consultas SQL](sql/consultas_analiticas.sql) · [Descargar dashboard](powerbi/NexaMart.pbix) · [Ver caso en Notion](https://app.notion.com/p/3f3711ab612481f9a5b6fe8d50bfbdbd)

## 1. El objetivo del análisis

Dar a la gerencia una visión común de las cuatro tiendas para comparar ventas, identificar productos y vendedores destacados y localizar señales de devolución. Los resultados orientan revisiones de surtido, seguimiento comercial y atención a casos concretos.

## 2. SQL: de las preguntas a las respuestas

Desarrollé **diez consultas** con JOINs, CTEs, funciones de ventana, subconsultas y agregación condicional. Estos son algunos resultados:

| Pregunta de negocio | Respuesta obtenida | Técnica SQL |
|---|---|---|
| ¿Qué tienda genera más ventas? | Singapore: **30.973,16 netos**. | JOIN + agregación |
| ¿Quién lidera entre los vendedores? | Cristian Santos: **16.345,58 netos**. | CTE + RANK global y por tienda |
| ¿Qué productos destacan en cada categoría? | Top 3 por categoría; Foldable Treadmill lidera en Sports & Fitness. | CTE + ROW_NUMBER particionado |
| ¿Qué mes tuvo mayores ventas? | Agosto de 2026: **10.384,06 netos**. | Agrupación temporal |
| ¿Qué medio de pago tiene mayor peso? | Credit Card: **31,26 %** del importe neto. | Subconsulta + porcentaje |
| ¿Dónde revisar devoluciones? | Fashion y Electronics reúnen **cinco de los seis casos**. | CASE + agregación condicional |

[Ver las diez preguntas, sus respuestas y su utilidad comercial](docs/preguntas_sql.md).

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

[Ver consulta completa](sql/consultas_analiticas.sql) · [Evidencia original de ejecución en MySQL](capturas/04_ranking_vendedores_sql.png)

</details>

## 3. Dashboard: explorar y decidir

### Resumen ejecutivo — Comparar tiendas y evolución mensual

**Hallazgo:** Singapore supera a Sydney en **8.690,55 netos**. SQL muestra que la mayor contribución a esa diferencia corresponde al ticket por compra.

**Decisión que orienta:** revisar Sports & Fitness en Sydney. Esta categoría concentra **65,46 % de la brecha**, pese a tener 37 compras en cada tienda. Conviene contrastar surtido, disponibilidad y unidades por compra.

![Resumen ejecutivo](capturas/06_resumen_ejecutivo.png)

[Profundizar la comparación Singapore–Sydney](docs/conclusion_comercial.md).

### Productos y vendedores — Identificar qué impulsa las ventas

**Hallazgo:** Foldable Treadmill genera **16.399,59 netos** y Cristian Santos lidera el ranking de vendedores identificados.

**Decisión que orienta:** revisar disponibilidad de los productos destacados y comparar prácticas comerciales de los vendedores, usando los filtros del informe.

![Productos y vendedores](capturas/07_productos_vendedores.png)

### Regional y calidad — Vigilar pagos y devoluciones

**Hallazgo:** Credit Card concentra el mayor importe neto. Se registran **seis devoluciones entre 757 eventos: 0,79 %**.

**Decisión que orienta:** revisar los casos de Fashion y Electronics y dar seguimiento a los medios de pago más utilizados. El mapa permite ubicar las tiendas.

![Regional y calidad](capturas/08_regional_calidad.png)

## 4. Indicadores y modelo compartido

**Ventas netas: 103.851,74 · Compras: 751 · Ticket promedio: 139,44.**

Las ventas netas descuentan devoluciones; el ticket utiliza ventas brutas divididas entre compras, excluyendo eventos de devolución. Los importes se expresan en unidades monetarias de simulación. Las recomendaciones plantean acciones para investigar; los datos no permiten demostrar rentabilidad ni causas.

MySQL organiza ventas y dimensiones; Power BI utiliza esas mismas tablas para conectar filtros e indicadores y añade el calendario. [Ver ambos diagramas y su correspondencia](docs/modelo_mysql_powerbi.md).

## 5. Cómo explorar el proyecto

- **Consultas y respuestas:** [SQL](sql/consultas_analiticas.sql) y [guía de preguntas](docs/preguntas_sql.md).
- **Dashboard:** [archivo Power BI](powerbi/NexaMart.pbix) y [guía de uso](powerbi/README.md).
- **Base de datos:** [esquema y carga](sql/) y [pasos para reproducir](docs/reproduccion.md).
- **Evidencias y detalle:** [capturas](capturas/README.md), [análisis comercial](docs/conclusion_comercial.md) y [definiciones técnicas](docs/decisiones_tecnicas.md).
