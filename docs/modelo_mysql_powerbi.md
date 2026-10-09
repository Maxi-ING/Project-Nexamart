# Del esquema físico de MySQL al modelo de Power BI

**Las mismas tablas sostienen las consultas SQL y el dashboard.** MySQL define las claves y conserva la integridad de los registros; Power BI utiliza las relaciones para propagar los filtros y calcular las medidas sobre las ventas.

## MySQL: estructura física

![Diagrama físico de MySQL](../capturas/02_diagrama_mysql.png)

`factventas` contiene un evento por `order_id`, con un producto por pedido en esta versión. Sus claves foráneas apuntan a tienda, vendedor, producto, cliente y método de pago. Esas mismas claves se utilizan en los JOINs del análisis.

## Power BI: relaciones para el análisis

![Modelo de Power BI actualizado](../capturas/10_modelo_powerbi.png)

Las cinco dimensiones se conectan a ventas con relaciones **1 a varios y filtro único desde la dimensión hacia los hechos**. Así, seleccionar una categoría, una tienda o un vendedor cambia el conjunto de ventas sobre el que se calculan los indicadores.

`DimCalendario`, creada con DAX, añade una sexta relación: **Date (1) → fecha (*)**. El PBIX actualizado contiene 730 días para los años 2025–2026. La tabla `Medidas` organiza las fórmulas y permanece sin relaciones; sus expresiones consultan los hechos y reciben el contexto de filtro del informe.

| Elemento | MySQL | Power BI |
|---|---|---|
| Tienda, vendedor, producto, cliente y pago | Claves primarias y foráneas | Relaciones 1:* hacia ventas |
| Vendedor–tienda | FK que conserva la asignación del vendedor | No se replica como relación adicional; ambas dimensiones filtran ventas directamente |
| Calendario | El esquema compartido contiene la fecha en ventas | Tabla DAX y relación activa por fecha |
| Indicadores | SUM, CASE, DISTINCT y funciones de ventana | Medidas DAX sobre el mismo grano y las mismas definiciones |

La diferencia vendedor–tienda evita caminos de filtro ambiguos en Power BI. El calendario permite analizar períodos sin cambiar las claves ni los registros de MySQL. SQL y Power BI comparten ventas brutas, importe devuelto, neto y ticket por compra; las relaciones semánticas permiten explorar esos resultados mediante filtros.

## Comprobación de la relación de calendario

La relación calendario–ventas está presente y activa tanto en el archivo inicial como en el actualizado. La revisión inicial la había omitido porque PBIXRay filtra tablas con `SystemFlags` distintos de cero, incluyendo tablas calculadas. Se corrigió el extractor para consultar las relaciones completas y excluir únicamente las tablas automáticas de fecha. No era una relación faltante del proyecto.

Las relaciones extraídas están en `powerbi/relaciones_actuales.json`, el esquema en `sql/nexamart_schema.sql` y la revisión del archivo en `docs/revision_pbix_actualizado.json`.
