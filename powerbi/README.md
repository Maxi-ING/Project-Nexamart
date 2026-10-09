# Power BI: versión corregida del proyecto

La versión editable está en [NexaMart_corregido](NexaMart_corregido/) y se descarga completa en [NexaMart_corregido.zip](NexaMart_corregido.zip). Incluye las tres páginas del informe original, su tema y un modelo corregido con **15 medidas y seis relaciones activas**.

Se corrigieron las definiciones del calendario, el orden mensual y las métricas en los archivos del proyecto. **Pendiente de validación en Power BI Desktop:** abrir, actualizar, comprobar el informe y guardarlo como PBIX. Este entorno no ejecuta Desktop ni el motor DAX. El [PBIX original](NexaMart.pbix) sigue disponible como evidencia histórica y conserva sus limitaciones; no es el archivo corregido.

## Cambios incorporados

- Calendario con años completos 2025–2026, clave de fecha y relación activa 1:* a ventas, con filtro desde calendario.
- Año-Mes de tipo texto, ordenado por AñoMesOrden; tendencia ascendente por mes.
- Ventas Brutas, Importe Devoluciones y Ventas Netas separados en los KPIs.
- Pedidos Venta excluye devoluciones. Ticket Promedio = Ventas Brutas / Pedidos Venta: **139,44**, sobre **751 compras**.
- Rankings y participación de pagos calculados sobre ventas netas, igual que SQL.
- Proporción Eventos Devolución = eventos de devolución / todos los eventos: **6 / 757 = 0,79 %**.
- Top 3 por categoría con desempate por producto_id, consistente con ROW_NUMBER.
- Comparación de tiendas enriquecida con tooltip de compras, ticket, bruto y devoluciones.

## Abrir y guardar

1. Descarga y descomprime el ZIP; conserva todas sus carpetas juntas.
2. En Power BI Desktop con soporte PBIP/PBIR, abre `NexaMart_corregido/NexaMart.pbip`. Si tu versión solicita habilitar las opciones de proyecto/informe, actívalas y reinicia Desktop.
3. Pulsa **Actualizar**. El modo predeterminado `Snapshot` incorpora los mismos datos recuperados del informe, sin rutas locales ni credenciales. La primera apertura no incluye caché de datos.
4. Comprueba los cinco KPIs: **104.718,63 bruto; 866,89 devuelto; 103.851,74 neto; 751 compras; ticket 139,44**.
5. Selecciona un mes: la tendencia debe seguir septiembre de 2025–agosto de 2026, la suma debe conciliar y las medidas temporales deben responder al filtro. Comprueba también el Top 3 y los filtros por categoría.
6. Usa **Guardar como → PBIX** para generar `NexaMart_corregido.pbix`. Ese guardado final y las capturas actualizadas todavía requieren Desktop.

## Usar MySQL como origen

Restaura el esquema y la carga del repositorio en MySQL. En **Transformar datos → Administrar parámetros**, cambia `pModo` a `MySQL`, ajusta `pServidor` y `pBase`, y configura el conector y las credenciales localmente. Las seis particiones importan las tablas base directamente con MySQL.Database; las medidas y relaciones son las mismas en ambos modos.

El modo Snapshot facilita revisar el caso; MySQL mantiene la arquitectura principal del proyecto. No se incluyen credenciales. El calendario más amplio no añade ventas: YTD de 2025 solo tiene datos desde septiembre y no hay histórico suficiente para YoY completo.

## Verificación reproducible

```bash
python -m pip install -r requirements_verificacion.txt
python scripts/construir_powerbi_corregido.py
python scripts/verificar_correcciones.py
```

Ejecuta estos comandos desde la raíz del repositorio. La verificación revisa referencias de visuales, relaciones, datos incorporados, esquemas JSON oficiales, consultas adaptadas a SQLite e identidades comerciales. No certifica ejecución DAX/Desktop o MySQL.

Documentación del formato: [proyectos PBIP](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-overview) · [modelo semántico](https://learn.microsoft.com/en-us/power-bi/developer/projects/projects-dataset).
