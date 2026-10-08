# NexaMart | Análisis comercial con SQL y Power BI

**SQL · MySQL · Power BI · DAX**

Análisis de ventas de una cadena ficticia con tiendas en **New York, London, Singapore y Sydney**. Utilicé SQL para comparar el desempeño comercial y Power BI para explorar los resultados y orientar decisiones sobre productos, vendedores y devoluciones.

**757 registros · 4 tiendas · 31 productos · 12 meses**  
Septiembre de 2025 a agosto de 2026. Datos simulados con fines de portafolio.

[Consultas SQL](sql/consultas_analiticas.sql) · [Dashboard Power BI](powerbi/NexaMart.pbix) · [Caso en Notion](https://app.notion.com/p/3f3711ab612481f9a5b6fe8d50bfbdbd)

## SQL: preguntas de negocio y análisis

El núcleo del proyecto son **siete consultas comerciales** sobre un modelo de ventas en MySQL, acompañadas de una vista consolidada para facilitar su consumo.

| Pregunta | Técnica SQL |
|---|---|
| ¿Qué tiendas generan más ventas? | JOIN y agregación |
| ¿Quién lidera globalmente y dentro de su tienda? | CTE + `RANK() OVER` |
| ¿Qué tres productos generan más ingresos por categoría? | CTE + `ROW_NUMBER()` particionado |
| ¿Qué peso tiene cada método de pago? | Subconsulta escalar y porcentajes |
| ¿Cómo evolucionan las ventas y los pedidos por mes? | Agrupación temporal |
| ¿Qué clientes VIP acumulan mayor gasto? | CTE, segmentación y Top 10 |
| ¿Qué categorías presentan más devoluciones? | `CASE` y agregación condicional |

**Ejemplo: ranking global y por tienda.** Una CTE calcula el importe por vendedor; las funciones de ventana permiten compararlo en ambos niveles sin perder el detalle:

```sql
SELECT *,
    RANK() OVER (
        ORDER BY ventas_totales DESC
    ) AS ranking_global,
    RANK() OVER (
        PARTITION BY nombre_tienda ORDER BY ventas_totales DESC
    ) AS ranking_en_tienda
FROM ventas_por_vendedor;
```

[Ver la consulta completa y las demás preguntas](sql/consultas_analiticas.sql).

![Ranking de vendedores ejecutado en MySQL](capturas/04_ranking_vendedores_sql.png)

Las consultas comerciales excluyen devoluciones: suman **104.718,63** en 751 ventas. Power BI incorpora los seis eventos negativos y muestra **103.851,74 netos**. Los importes son unidades monetarias de simulación.

## Dashboard: respuestas y decisiones

### 1. Resumen ejecutivo — ¿Dónde se concentra el resultado?

**Respuesta:** Singapore lidera con **30.973,16 netos**, frente a **22.282,61** de Sydney. Los indicadores y la comparación por tienda permiten localizar diferencias y explorar su evolución mensual.

**Acción sugerida:** comparar el catálogo y la mezcla de ventas de ambas tiendas antes de definir acciones comerciales para Sydney.

![Resumen ejecutivo](capturas/06_resumen_ejecutivo.png)

### 2. Productos y vendedores — ¿Quién y qué impulsa las ventas?

**Respuesta:** Cristian Santos lidera entre vendedores identificados con **16.345,58 netos**. Foldable Treadmill es el producto con mayor importe: **16.399,59**. El Top 3 se calcula dentro de cada categoría y se ordena por ingresos.

**Acción sugerida:** revisar disponibilidad y promociones de los productos destacados y contrastar las prácticas de los vendedores líderes. El filtro por categoría permite ajustar esa comparación.

![Productos y vendedores](capturas/07_productos_vendedores.png)

### 3. Regional y calidad — ¿Qué conviene vigilar?

**Respuesta:** Credit Card representa **31,26 % del importe neto**. Fashion presenta **1,50 % de registros de devolución** y Electronics **1,44 %**; en total son seis devoluciones de 757 registros (**0,79 %**). El mapa ubica las tiendas.

**Acción sugerida:** revisar los casos de devolución de ambas categorías y mantener seguimiento por período; comprobar también la continuidad de los medios de pago más utilizados.

![Regional y calidad](capturas/08_regional_calidad.png)

Estas acciones son recomendaciones del caso, no mejoras económicas demostradas. Los ingresos no permiten concluir rentabilidad o productividad, y seis devoluciones no bastan para atribuir causas.

## Modelo y revisión técnica

Una tabla de hechos y cinco dimensiones sostienen los JOINs y el análisis. En esta versión hay **un producto por pedido**. La preparación en Python normalizó los datos y conservó los registros sin identificación mediante la clave `-1`.

- [Esquema y carga MySQL](sql/) y [datos del informe](data/snapshot/README.md).
- [Once medidas DAX](powerbi/medidas_originales.dax), [modelo y definiciones](docs/decisiones_tecnicas.md).
- [Capturas de consultas, dashboard y filtros](capturas/README.md).
- [Cómo reproducir el análisis](docs/reproduccion.md): MySQL 8.0+, carga, controles y revisión del PBIX.

**Antes de revisar la tendencia, MoM o YTD:** restablecer la relación calendario–ventas y ordenar los meses cronológicamente, según la guía. El repositorio permite reproducir el análisis desde los datos importados del PBIX.
