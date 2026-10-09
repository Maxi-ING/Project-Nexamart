# NexaMart | Explorar el dashboard

[Descarga NexaMart.pbix](NexaMart.pbix) y ábrelo en **Power BI Desktop**. El informe contiene tres páginas:

| Página | Qué permite explorar |
|---|---|
| Resumen ejecutivo | Indicadores generales, comparación de tiendas y evolución mensual. |
| Productos y vendedores | Rankings de vendedores y Top 3 de productos por categoría. |
| Regional y calidad | Ubicación de tiendas, métodos de pago y devoluciones. |

Utiliza los filtros disponibles para profundizar los resultados. Con el período completo y sin filtros, los indicadores principales son **103.851,74 netos, 751 compras y ticket 139,44**.

[Preguntas y respuestas SQL](../docs/preguntas_sql.md) · [Conclusión comercial](../docs/conclusion_comercial.md) · [Modelos MySQL–Power BI](../docs/modelo_mysql_powerbi.md)

## Datos y documentación

El informe utiliza las seis tablas de MySQL en modo Import. Para actualizar desde tu servidor, configura los pasos de origen y las credenciales localmente. [Ver carga y reproducción](../docs/reproduccion.md).

El PBIX es el informe principal y corresponde a las capturas publicadas. [Medidas DAX](medidas_actuales.dax) y [definiciones](../docs/decisiones_tecnicas.md) están disponibles para quien quiera explorar el modelo.

<details>
<summary>Versiones de apoyo y alcance de revisión</summary>

El [PBIX inicial](historico/NexaMart_original.pbix) se conserva como histórico. El [proyecto PBIP alternativo](NexaMart_corregido.zip) es una propuesta editable de apoyo, validada estructuralmente; no generó las capturas actuales y requiere comprobación en Desktop si se utiliza.

La revisión del informe principal comprobó datos, fórmulas, relaciones y capturas aportadas por el autor. [Registro de revisión](../docs/revision_pbix_actualizado.json). La ejecución de DAX no se realizó en este entorno.

</details>
