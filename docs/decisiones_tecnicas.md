# NexaMart | Decisiones técnicas y alcance de la evidencia

## 1. Diseño del caso

Se definió una empresa ficticia de retail internacional, con cuatro tiendas y cinco categorías: Electronics, Smart Home, Fashion, Sports & Fitness y Beauty & Personal Care. El conjunto se generó con Python y Faker, con semillas fijas según el resumen del desarrollo.

El catálogo contiene 31 productos, 170 clientes y ocho vendedores identificados. Un miembro adicional «No registrado» permite representar la ausencia de cliente o vendedor. El período cubre septiembre de 2025 a agosto de 2026.

La simulación facilita controlar los errores y practicar el flujo completo. No demuestra patrones del mercado real ni permite atribuir mejoras económicas a una empresa existente.

## 2. ETL documentado

El proceso descrito utiliza `ventas_raw_dirty.csv` y `etl_limpieza.py`:

1. Interpretar explícitamente tres formatos de fecha: `DD/MM/YYYY`, `MM-DD-YYYY` y `YYYY-MM-DD`; normalizar a `YYYY-MM-DD`.
2. Eliminar cinco filas completamente duplicadas.
3. Normalizar categoría, nombres de producto y métodos de pago, corrigiendo espacios y variaciones de mayúsculas.
4. Reemplazar identificadores faltantes de cliente y vendedor por `-1`; crear los miembros correspondientes en las dimensiones antes de cargar los hechos.
5. Conservar seis cantidades negativas y marcarlas como devoluciones mediante `es_devolucion`.
6. Apartar tres filas con cantidad 500 en `ventas_para_revision.csv`, conservando trazabilidad para revisión manual.

**Conciliación:** 765 filas iniciales − 5 duplicados − 3 outliers = 757 registros finales. Las devoluciones y los identificadores faltantes no se restan del total final.

El conteo final se observa en MySQL. Los CSV, el generador y el script ETL no se recibieron en esta entrega, por lo que no se verificaron las semillas, el detalle de los nulos ni la ejecución de estas transformaciones. Tampoco se reconstruyeron datos a partir de imágenes.

## 3. Base relacional y grano

La base contiene `FactVentas` y cinco dimensiones: tienda, vendedor, producto, cliente y método de pago. Las claves foráneas permiten mantener la integridad referencial.

El esquema MySQL incorpora también la relación `DimVendedor.tienda_id → DimTienda.tienda_id`. Por ello, describe una base dimensional con una relación adicional entre dimensiones; no es una estrella pura de dimensiones independientes.

`FactVentas.order_id` es clave primaria. **La versión actual admite una sola fila con un producto por pedido.** El enunciado «una línea de producto por orden» solo es compatible con esa restricción. Una ampliación a pedidos de varios productos requeriría una clave como `venta_linea_id` o `(order_id, linea_id)`. En esa ampliación, el total de pedidos seguiría contando `DISTINCT order_id`, no filas.

El archivo `sql/nexamart_schema.sql` reproduce el DDL compartido y añade creación de la base con UTF-8. No incluye carga de datos, limpieza ni eliminación de tablas existentes. La columna `es_devolucion` conserva la definición original `TINYINT(1)`; el ETL y la carga deben garantizar sus valores y evitar nulos imprevistos.

## 4. Consultas analíticas

Se recibieron siete consultas SELECT. Cubren agregaciones, JOINs, dos rankings con funciones de ventana, una subconsulta escalar y agregación condicional. La existencia de `vw_ventas_analitico` se observa en las capturas, pero su DDL no se compartió.

La publicación incorpora una **definición propuesta** de esa vista, con LEFT JOIN para conservar hechos y sin correos de clientes. La vista incluye devoluciones para que el consumidor aplique su criterio de negocio. Se usa `CREATE VIEW`, que no sobrescribe una vista existente.

Ajustes de la versión preparada:

- Agrupar por identificador además del nombre, evitando combinar entidades diferentes con el mismo nombre.
- Desempatar el Top 3 por `producto_id`, manteniendo el criterio principal de ingresos.
- Usar `NULLIF(..., 0)` en porcentajes para evitar división por cero.
- Explicitar en nombres y comentarios cuándo se excluyen devoluciones.

El ranking por tienda conserva la asignación de `DimVendedor`, como en la consulta original. Este criterio supone una tienda por vendedor; con traslados históricos se necesitaría modelar esa asignación en el tiempo.

Las capturas respaldan la ejecución original del ranking y del Top 3. **No se ejecutó la versión editorial sobre MySQL**, porque no se recibió la carga original ni una conexión a esa instancia.

## 5. Modelo de Power BI

Según el proceso documentado, se importaron las seis tablas base desde MySQL mediante Connector/NET, en modo Import, sin utilizar la vista como tabla principal.

Se retiró la relación adicional vendedor-tienda del modelo de Power BI para mantener un único camino activo desde cada dimensión hasta `FactVentas`. La captura confirma las relaciones directas de las dimensiones con los hechos. El resumen identifica este cambio como la solución aplicada al problema de totales repetidos por vendedor; sin el `.pbix` previo no se puede aislar retrospectivamente toda la causa del error.

`DimCalendario` se creó con `CALENDAR`, se marcó como tabla de fechas y se relacionó con `FactVentas[fecha]`. La tabla `Medidas` organiza las medidas y no necesita relacionarse físicamente.

Para una reconstrucción se debe utilizar una tabla calendario continua que cubra años completos y comprobar tipos de fecha y dirección de filtro. La evidencia actual no permite inspeccionar la expresión exacta del calendario ni su cobertura completa.

## 6. Medidas DAX documentadas

| Grupo | Medidas o funciones descritas |
|---|---|
| Base | Ventas Totales, Unidades Vendidas, Total Pedidos, Ticket Promedio |
| Temporal | Ventas Mes Anterior con `DATEADD`, % Crecimiento MoM, Ventas YTD con `TOTALYTD` |
| Rankings | Ranking Vendedor con `RANKX`; Ranking Producto en Categoría con `RANKX` y `ALLEXCEPT` |
| Calidad | Total Devoluciones y % Tasa Devolución |

La columna `es_devolucion` se importó como booleano en Power BI, según el desarrollo: allí se comparó con `TRUE()`; en SQL se usa `1`.

Esta tabla documenta las medidas descritas. **No contiene expresiones DAX recuperadas del `.pbix`.** Deben incorporarse las fórmulas originales para comprobar selección de filtros, denominadores, tratamiento de devoluciones y desempates. Un `RANKX` con empates puede mostrar más de tres productos; `ROW_NUMBER()` limita a tres filas. La selección de ranking en DAX debe documentar esa diferencia.

## 7. Contrato de métricas y conciliación pendiente

| Concepto | Definición comprobable en el material recibido |
|---|---|
| Registros cargados | `COUNT(*)`: 757, incluidas devoluciones |
| Pedidos SQL de las consultas comerciales | `COUNT(DISTINCT order_id)` con `es_devolucion = 0` |
| Importes SQL comerciales | `SUM(precio_total)` con `es_devolucion = 0` |
| Proporción de devoluciones | Filas marcadas / todas las filas del contexto; global: 6 / 757 = 0,79 % |
| Pedidos del dashboard | La captura muestra 757; coincide con el conteo total, incluyendo devoluciones |
| Ventas y ticket del dashboard | 103,85 mil y 137,19; fórmula exacta pendiente del `.pbix` |

Si los seis eventos de devolución son filas distintas dentro de los 757 registros, los registros restantes serían 751. Debe comprobarse este conteo en la base y decidir si «Total Pedidos» debe contar ventas, eventos totales o pedidos originales.

La tabla SQL muestra **10.499,58** para Smartwatch Series X; Power BI muestra **10.249,59**. La diferencia es **249,99**. Es compatible con distintas reglas para devoluciones, pero esa explicación es una hipótesis que requiere los datos y las medidas; no se presenta como una causa comprobada.

La publicación usa «unidades monetarias de simulación» porque no se recibió una divisa común ni tasas de conversión. No se debe interpretar el total como una suma validada de USD, GBP, SGD y AUD. Para un caso real se necesitarían moneda local, moneda base, fecha y tipo de cambio.

## 8. Lectura de negocio

- Singapore encabeza el importe por tienda en la captura general.
- Cristian Santos lidera el ranking global observado.
- Al filtrar Electronics, Abigail Shaffer pasa a encabezar el ranking visible.
- Credit Card representa 31,26 % del importe del gráfico de pagos.
- Se observan seis eventos de devolución; Fashion tiene el porcentaje más alto mostrado por categoría, seguido de Electronics.

Estos hallazgos orientan preguntas sobre mezcla de productos, concentración comercial y devoluciones. No prueban productividad, desempeño ajustado por horas trabajadas, rentabilidad ni causas de devolución. Una muestra de seis devoluciones justifica explorar los casos, sin atribuir problemas sistemáticos a una categoría.

## 9. Diseño y archivos pendientes

El dashboard utiliza carbón cálido y verde esmeralda, con fondos comunes de tarjeta y acentos en barras, líneas y métodos de pago. Las tres páginas separan resumen, desempeño y calidad. Las etiquetas oscuras de algunos ejes podrían ganar contraste en una iteración posterior; no se modificaron las imágenes originales.

Para reproducir el flujo completo faltan:

- Generador de datos, semillas y dependencias de Python.
- `ventas_raw_dirty.csv`, `ventas_clean.csv` y `ventas_para_revision.csv`.
- `etl_limpieza.py` y su registro de controles.
- Carga original de MySQL (`nexamart_schema_and_data.sql` o exportación equivalente).
- `.pbix`, definiciones DAX originales y tema JSON.

La entrega actual publica documentación, esquema, consultas y diez capturas. Permite evaluar el diseño y revisar la evidencia del trabajo realizado; la reproducción de resultados queda pendiente de los originales.
