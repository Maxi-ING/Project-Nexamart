# NexaMart | Revisar y reproducir el análisis

## Power BI revisado

Descarga [NexaMart_corregido.zip](../powerbi/NexaMart_corregido.zip), descomprímelo y abre NexaMart.pbip en Desktop. Pulsa Actualizar para cargar el snapshot incorporado; comprueba los cinco KPIs y los filtros antes de guardar como PBIX. El calendario y el orden mensual ya están definidos en el proyecto.

Resultados esperados: bruto 104.718,63; importe devuelto 866,89; neto 103.851,74; 751 compras; ticket 139,44. Los pasos completos y la conexión MySQL están en [powerbi/README.md](../powerbi/README.md).

**Pendiente:** apertura y ejecución DAX/Desktop, captura del informe actualizado y guardado final como PBIX. El PBIX original sigue disponible como evidencia, sin estas correcciones.

## Restaurar los datos en MySQL 8.0+

En una base de trabajo nueva, ejecuta en orden:

1. sql/nexamart_schema.sql: crea las seis tablas.
2. sql/nexamart_snapshot_data.sql: carga dimensiones y hechos. Requiere tablas vacías; no ejecutar dos veces.
3. sql/controles_snapshot.sql: concilia conteos, referencias e indicadores.
4. sql/consultas_analiticas.sql: ejecuta diez consultas y crea o actualiza la vista analítica del proyecto.

Los INSERT no borran ni reemplazan datos. Usa otra instancia de trabajo si ya tienes la base original. La vista sí se actualiza con CREATE OR REPLACE VIEW, para incorporar los campos de bruto y devuelto.

En Desktop, cambia pModo a MySQL y configura pServidor, pBase y tus credenciales localmente. No se publican credenciales.

## Verificación local de esta entrega

```bash
python -m pip install -r requirements_verificacion.txt
python scripts/construir_powerbi_corregido.py
python scripts/verificar_correcciones.py
```

La verificación interpreta SQL MySQL con sqlglot, lo adapta a SQLite y compara los resultados con los CSV. Comprueba relaciones, referencias de visuales, datos portátiles, orden mensual, esquemas JSON oficiales e integridad ZIP. No ejecuta el motor DAX ni MySQL.

Los resultados están en data/resultados y el registro en docs/validacion_correcciones.json. Para reproducir el origen recuperado utiliza scripts/exportar_snapshot_pbix.py con requirements_snapshot.txt; conserva sin cambios el PBIX original y su manifiesto.
