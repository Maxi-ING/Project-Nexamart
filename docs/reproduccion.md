# NexaMart | Revisar y reproducir el análisis

## Power BI actualizado

Descarga [NexaMart.pbix](../powerbi/NexaMart.pbix) y ábrelo en Desktop. El autor aportó este archivo guardado y las capturas actualizadas. Los resultados esperados son bruto 104.718,63; devuelto 866,89; neto 103.851,74; 751 compras; ticket 139,44.

La relación calendario–ventas está activa y el calendario tiene 730 días. Sigue los ajustes restantes de Año-Mes, orden y marca de fechas descritos en [powerbi/README.md](../powerbi/README.md). Para actualizar desde MySQL, ajusta las seis consultas originales a tu servidor y tus credenciales.

El PBIP alternativo es una propuesta editable con configuración explícita y no corresponde a las nuevas capturas; su apertura y ejecución en Desktop siguen pendientes. El PBIX inicial se conserva en powerbi/historico.

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

Los resultados están en data/resultados y el registro en docs/validacion_correcciones.json. Para reproducir el origen recuperado utiliza scripts/exportar_snapshot_pbix.py con requirements_snapshot.txt; conserva el PBIX inicial en powerbi/historico y su manifiesto.
