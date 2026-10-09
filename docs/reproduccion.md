# NexaMart | Explorar y reproducir el análisis

## Consultar el dashboard

Descarga [NexaMart.pbix](../powerbi/NexaMart.pbix), ábrelo en Power BI Desktop y recorre sus tres páginas. Puedes explorar el informe con los datos importados, sin conectar tu propia base de datos.

Con todos los datos, los indicadores principales son **103.851,74 netos, 751 compras y ticket promedio 139,44**. [Ver la guía del dashboard](../powerbi/README.md).

## Ejecutar el análisis SQL en MySQL 8.0+

En una base de trabajo nueva, ejecuta estos archivos en orden:

1. [nexamart_schema.sql](../sql/nexamart_schema.sql): crea las tablas y relaciones.
2. [nexamart_snapshot_data.sql](../sql/nexamart_snapshot_data.sql): carga los datos del informe. Requiere tablas vacías; ejecútalo una sola vez.
3. [controles_snapshot.sql](../sql/controles_snapshot.sql): comprueba conteos e indicadores.
4. [consultas_analiticas.sql](../sql/consultas_analiticas.sql): responde diez preguntas y crea o actualiza la vista analítica.

Después compara tus resultados con la [guía de preguntas y respuestas](preguntas_sql.md). La carga no borra ni reemplaza datos; la vista se actualiza con CREATE OR REPLACE VIEW.

## Actualizar Power BI desde tu MySQL

En el PBIX principal, abre Transformar datos y ajusta el servidor y la base de datos en el paso de origen de las seis consultas. Configura tus credenciales localmente y actualiza el informe.

## Verificación de apoyo

Las respuestas publicadas se comprobaron sobre los datos del informe mediante adaptación del SQL a SQLite. [Resultados completos](../data/resultados/respuestas_sql.json). Los datos del snapshot se recuperaron del PBIX; no incluyen el CSV sucio ni el ETL original.

Para revisar también el proyecto PBIP alternativo:

```bash
python -m pip install -r requirements_verificacion.txt
python scripts/verificar_correcciones.py
```

Este control concilia SQL y datos y comprueba la estructura del PBIP. No ejecuta MySQL ni DAX/Desktop. [Alcance técnico](decisiones_tecnicas.md) y [registro](validacion_correcciones.json).
