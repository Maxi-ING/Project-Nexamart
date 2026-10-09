# Power BI: informe actual y modelo editable

El archivo principal es [NexaMart.pbix](NexaMart.pbix), actualizado por el autor y acompañado de nuevas capturas del 9 de octubre de 2026. Contiene **14 medidas**, calendario de **730 días** y **seis relaciones analíticas activas**, todas con filtro único hacia ventas.

Se comprobó que las seis tablas de origen conservan exactamente los mismos datos que la versión anterior. La captura del resumen muestra neto **103,85 mil**, **751 compras** y ticket **139,44**. Las fórmulas de bruto e importe devuelto también están incorporadas, aunque no tienen tarjetas propias.

[Medidas actuales](medidas_actuales.dax) · [Relaciones actuales](relaciones_actuales.json) · [Calendario actual](calendario_actual.dax) · [Revisión del archivo](../docs/revision_pbix_actualizado.json)

## Correspondencia MySQL–Power BI

Las claves del esquema físico se convierten en relaciones de filtro entre dimensiones y hechos. Power BI añade calendario y medidas. La FK vendedor–tienda se conserva en MySQL, pero no se replica como un camino adicional de filtro en el informe.

[Ver ambos diagramas y la explicación](../docs/modelo_mysql_powerbi.md).

**Corrección de la revisión anterior:** calendario–ventas ya existía en el PBIX inicial. El lector empleado ocultaba relaciones con tablas calculadas. Se consultaron los metadatos completos y se corrigieron el extractor y la documentación.

## Ajustes de configuración restantes en el PBIX

La captura muestra la tendencia cronológica. Sin embargo, el archivo guarda Año-Mes como fecha, sin SortByColumn, y un criterio PBIR de orden por ventas descendente. Para dejar la configuración explícita:

1. Cambia DimCalendario[Año-Mes] a Texto.
2. Usa Ordenar por columna → AñoMesOrden.
3. En el gráfico, selecciona ordenar por Año-Mes, ascendente, y guarda.
4. Comprueba la marca de tabla de fechas usando Date. Los metadatos extraídos no permiten dar por completada esa marca.

El Top 3 DAX actual conserva RANKX sin desempate por identificador; los datos mostrados no presentan empates en sus primeros puestos. Para igualar ROW_NUMBER ante futuros empates, usa la versión de ranking del proyecto editable. Unidades Vendidas mantiene la suma firmada: representa unidades netas (1.026).

Como mejora de presentación, cambia Total Pedidos a Pedidos de venta en el título de la tarjeta y Tasa de devolución a Proporción de eventos de devolución. Bruto e importe devuelto pueden mostrarse en tooltip para conservar tres KPIs principales.

## Proyecto editable alternativo

[NexaMart_corregido.zip](NexaMart_corregido.zip) contiene una versión PBIP con **15 medidas**, calendario marcado, orden mensual explícito y desempate de productos. Es una propuesta editable verificada estructuralmente; no es el archivo que generó las capturas nuevas. Su ejecución en Desktop sigue pendiente.

Descomprime, abre NexaMart.pbip y pulsa Actualizar. El modo Snapshot incorpora los datos; para MySQL cambia pModo, pServidor y pBase, y configura el conector y tus credenciales localmente. Después de comprobar el informe, guarda como PBIX.

El [PBIX inicial](historico/NexaMart_original.pbix) y sus fórmulas originales se conservan para trazabilidad. El calendario ampliado no añade ventas anteriores a septiembre de 2025.

## Revisión reproducible

```bash
python -m pip install -r requirements_verificacion.txt
python scripts/verificar_correcciones.py
```

El verificador comprueba el PBIP alternativo, las consultas adaptadas a SQLite y las identidades comerciales. La revisión del PBIX actual se documenta por separado; este entorno no ejecuta DAX ni Desktop. La ejecución SQL nativa requiere MySQL 8.0.
