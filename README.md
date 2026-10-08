# NexaMart | Análisis de ventas retail multi-tienda

**Python · MySQL · Power BI · DAX**

[Ver el caso de estudio en Notion](https://app.notion.com/p/3f3711ab612481f9a5b6fe8d50bfbdbd?pvs=204)

Proyecto de análisis de datos de principio a fin: preparación de transacciones, modelado relacional, consultas SQL y un dashboard para comparar el desempeño de cuatro tiendas internacionales.

> **Resultado:** 757 registros, **11 medidas DAX** y tres páginas de Power BI. Se verificaron **103.851,74 unidades monetarias netas**, conciliando las ventas con las devoluciones del modelo importado. Empresa y datos simulados con fines de portafolio.

![Resumen ejecutivo de NexaMart](capturas/06_resumen_ejecutivo.png)

## El problema y el objetivo

NexaMart es una cadena ficticia con tiendas en **New York, London, Singapore y Sydney**. El caso plantea una gerencia que necesita comparar tiendas, identificar productos y vendedores destacados y revisar devoluciones desde una misma fuente de información.

Construí una solución que integra preparación de datos en Python, una base analítica en MySQL y visualización en Power BI. El objetivo es facilitar preguntas comerciales concretas y mostrar las decisiones técnicas que hacen confiable el análisis.

## Alcance y herramientas

| Elemento | Alcance |
|---|---|
| Período | Septiembre de 2025 a agosto de 2026 |
| Tiendas | 4, distribuidas en 4 países |
| Catálogo | 31 productos en 5 categorías |
| Clientes | 170 generados, más el registro «No registrado» |
| Vendedores | 8 identificados, más el registro «No registrado» |
| Pagos | Credit Card, Debit Card, Digital Wallet, PayPal y Cash |
| Preparación | Python y Faker, según el proceso documentado |
| Base y análisis | MySQL, claves foráneas, JOINs, CTEs y funciones de ventana |
| Visualización | Power BI, DAX, calendario y filtros por categoría |

**Flujo:** CSV de origen → limpieza en Python → modelo analítico en MySQL → conexión en modo Import → dashboard en Power BI.

## Decisiones de calidad de datos

El origen se generó con inconsistencias intencionales para practicar un proceso ETL: fechas en tres formatos, duplicados, identificadores faltantes, devoluciones y cantidades atípicas.

| Tratamiento documentado | Resultado |
|---|---:|
| Filas de origen | 765 |
| Duplicados exactos eliminados | 5 |
| Cantidades atípicas apartadas para revisión | 3 |
| **Registros finales** | **757** |
| Sin cliente identificado, conservados con clave `-1` | 10 |
| Sin vendedor identificado, conservados con clave `-1` | 6 |
| Devoluciones conservadas como eventos de negocio | 6 |

La conciliación es **765 − 5 − 3 = 757**. Los nulos en cliente y vendedor no implican perder la transacción. Las devoluciones se identifican mediante `es_devolucion`; los outliers quedan para revisión. El PBIX confirma los 757 hechos, los miembros «No registrado» y las seis devoluciones. Se verificaron claves únicas, referencias a dimensiones e igualdad entre precio, cantidad e importe. El CSV crudo y el ETL original siguen pendientes; el [snapshot publicado](data/snapshot/README.md) recupera el estado importado del informe.

## Modelo de datos

![Diagrama relacional en MySQL](capturas/02_diagrama_mysql.png)

`FactVentas` concentra fecha, cantidad, precio e identificadores. Se relaciona con `DimTienda`, `DimVendedor`, `DimProducto`, `DimCliente` y `DimMetodoPago`. Power BI incorpora `DimCalendario` y once medidas DAX. La relación de calendario que aparece en la captura no se conserva en el PBIX adjunto: antes de validar los gráficos temporales debe restablecerse según las [instrucciones de reproducción](docs/reproduccion.md).

Dos decisiones relevantes:

- **Integridad referencial:** cliente y vendedor pueden usar `-1` / «No registrado», conservando ventas sin identificación.
- **Filtros sin ambigüedad:** en Power BI cada dimensión filtra directamente la tabla de hechos; la relación adicional entre vendedor y tienda se retiró del modelo semántico. La relación continúa presente en MySQL.

**Grano de la versión actual:** una fila contiene un producto y un `order_id` único. La clave primaria permite una sola fila por pedido. Para admitir pedidos con varios productos se necesitaría una clave de línea independiente; esa extensión queda fuera de esta versión.

## SQL: de preguntas a consultas

El archivo [consultas_analiticas.sql](sql/consultas_analiticas.sql) contiene **las siete consultas compartidas y una vista analítica añadida al preparar esta publicación**.

| Pregunta de negocio | Técnica |
|---|---|
| ¿Qué tienda concentra más ventas? | JOIN y agregación |
| ¿Quién lidera globalmente y dentro de cada tienda? | CTE y `RANK() OVER` |
| ¿Cuáles son los tres productos con más ingresos por categoría? | CTE y `ROW_NUMBER()` particionado |
| ¿Qué participación tiene cada método de pago? | Subconsulta escalar y porcentaje |
| ¿Cómo evolucionan ventas y pedidos por mes? | Agrupación temporal |
| ¿Qué clientes VIP acumulan mayor gasto? | CTE, segmentación y Top 10 |
| ¿Qué categorías presentan mayor proporción de devoluciones? | `CASE` y agregación condicional |

![Ranking global y por tienda en MySQL](capturas/04_ranking_vendedores_sql.png)

El Top 3 se ordena por **importe**, no por unidades. El código preparado añade desempate por identificador y protección frente a división por cero. Las capturas muestran la ejecución de la versión original. La nueva carga del snapshot permite ejecutar las consultas sobre los datos importados del PBIX; la ejecución en un servidor MySQL requiere validación local.

## Dashboard: tres vistas para decidir

### 1. Resumen ejecutivo

Compara tiendas y la tendencia mensual; presenta ventas totales, conteo de pedidos y ticket promedio. El snapshot confirma que Singapore encabeza el importe neto por tienda: **30.973,16**.

### 2. Productos y vendedores

Relaciona el ranking comercial con el catálogo. Cristian Santos lidera el importe neto entre vendedores identificados: **16.345,58**; la tabla permite identificar los tres productos con mayor importe dentro de cada categoría.

![Productos y vendedores](capturas/07_productos_vendedores.png)

### 3. Regional y calidad

Integra las ubicaciones de las tiendas, métodos de pago y devoluciones. El mapa original representa presencia geográfica: no incorpora una medida de ventas para el tamaño de los puntos. Se observan **6 devoluciones sobre 757 registros: 0,79 %**. Es una proporción de registros marcados como devolución, no una tasa de unidades devueltas ni de pedidos originales devueltos.

![Regional y calidad](capturas/08_regional_calidad.png)

### Interactividad

El filtro **Electronics** modifica el ranking y las ventas por tienda. Abigail Shaffer encabeza el ranking en esa selección, mostrando cómo cambia la lectura al segmentar el negocio.

![Dashboard filtrado por Electronics](capturas/09_filtro_electronics.png)

## Métricas conciliadas

| Indicador | Valor | Definición |
|---|---:|---|
| Ventas sin devoluciones | 104.718,63 | Suma de los 751 eventos de venta |
| Importe de devoluciones | −866,89 | Seis eventos negativos |
| **Ventas netas** | **103.851,74** | Ventas + devoluciones; medida actual del informe |
| Pedidos/eventos del informe | 757 | DISTINCTCOUNT(order_id), incluidas devoluciones |
| Ticket del informe | 137,19 | Importe neto / 757 eventos |
| Proporción de devoluciones | 0,79 % | 6 / 757 eventos |

La diferencia entre SQL y Power BI responde al tratamiento de devoluciones. Para Smartwatch Series X se comprobó **10.499,58 − 249,99 = 10.249,59**. Las [fórmulas DAX originales](powerbi/medidas_originales.dax) permiten revisar esas definiciones.

El conteo y el ticket del informe incluyen devoluciones: no representan 757 compras positivas ni el ticket medio de las 751 ventas. Los importes son unidades monetarias de simulación, sin conversión de divisas documentada. Hay 12 meses de datos, sin costos, margen, inventario ni metas; no se demuestra rentabilidad ni un YoY mensual completo.

## Contenido disponible

| Ruta | Contenido |
|---|---|
| [sql/nexamart_schema.sql](sql/nexamart_schema.sql) | Esquema basado en el DDL compartido, con nombres físicos en minúsculas |
| [sql/consultas_analiticas.sql](sql/consultas_analiticas.sql) | Siete consultas y vista analítica |
| [sql/nexamart_snapshot_data.sql](sql/nexamart_snapshot_data.sql) | Carga completa del estado importado del PBIX |
| [sql/controles_snapshot.sql](sql/controles_snapshot.sql) | Conteos, referencias, signos e importes |
| [powerbi/NexaMart.pbix](powerbi/NexaMart.pbix) | Archivo original entregado por el autor |
| [powerbi/medidas_originales.dax](powerbi/medidas_originales.dax) | Once expresiones DAX originales |
| [powerbi/tema_nexamart.json](powerbi/tema_nexamart.json) | Paleta personalizada recuperada del informe |
| [data/snapshot/README.md](data/snapshot/README.md) | Seis tablas, calendario y manifiesto de verificación |
| [scripts/exportar_snapshot_pbix.py](scripts/exportar_snapshot_pbix.py) | Utilidad de extracción; no sustituye al ETL original |
| [docs/decisiones_tecnicas.md](docs/decisiones_tecnicas.md) | Modelo, métricas y alcance |
| [docs/reproduccion.md](docs/reproduccion.md) | Instrucciones de revisión y ejecución |
| [capturas/README.md](capturas/README.md) | Índice de las diez evidencias originales |
| `capturas/` | Dashboard, filtro, base, modelos y consultas |

**Pendientes del ETL original:** CSV crudo y de revisión, generador con semillas, `etl_limpieza.py` y salidas originales. La reproducción disponible empieza en el snapshot importado del PBIX; no reconstruye los errores que ya se retiraron.

## Cómo revisar esta entrega

1. Descarga [NexaMart.pbix](powerbi/NexaMart.pbix) o consulta las capturas. El archivo conserva los mismos bytes que el adjunto original.
2. En una instancia nueva de **MySQL 8.0+**, ejecuta el esquema y después `sql/nexamart_snapshot_data.sql`. La carga requiere tablas vacías; no borra ni reemplaza datos existentes.
3. Ejecuta `sql/controles_snapshot.sql` y las consultas analíticas.
4. En Power BI restablece la relación activa **DimCalendario[Date] (1) → nexamart factventas[fecha] (*)**, con filtro desde calendario, y marca la tabla de fechas. Ordena la tendencia por fecha ascendente.
5. Para actualizar desde MySQL, ajusta el origen y las credenciales a tu entorno. Para extraer de nuevo el snapshot utiliza el script y `requirements_snapshot.txt`.

La revisión verificó estructura, datos y expresiones mediante extracción; la apertura del informe en Power BI Desktop, la ejecución de DAX y la ejecución en MySQL requieren validación local. Los pasos están en [reproduccion.md](docs/reproduccion.md).

## Habilidades demostradas

**Calidad de datos y trazabilidad · Modelado relacional y dimensional · SQL analítico · Contexto de filtro en Power BI · DAX e inteligencia temporal · Comunicación de resultados y límites del análisis.**

El valor del proyecto está en conectar esas etapas en un caso coherente y explicar las decisiones que sostienen el resultado.
