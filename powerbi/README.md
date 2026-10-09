# NexaMart | Explorar el dashboard

El archivo está en `powerbi/NexaMart.pbix`. Ábrelo en **Power BI Desktop**. El informe contiene tres páginas:

| Página | Qué permite explorar |
|---|---|
| Resumen ejecutivo | Indicadores generales, comparación de tiendas y evolución mensual. |
| Productos y vendedores | Rankings de vendedores y Top 3 de productos por categoría. |
| Regional y calidad | Ubicación de tiendas, métodos de pago y devoluciones. |

Utiliza los filtros disponibles para profundizar los resultados. Con el período completo y sin filtros, los indicadores principales son **103.851,74 netos, 751 compras y ticket 139,44**.

Las respuestas, la conclusión breve y los diagramas están en la carpeta `docs/`.

## Datos y documentación

El informe utiliza las seis tablas de MySQL en modo Import. Para actualizar desde tu servidor, configura los pasos de origen y las credenciales localmente. Los pasos están en `docs/reproduccion.md`.

El PBIX es el informe principal y corresponde a las capturas publicadas. `powerbi/medidas_actuales.dax` y `docs/decisiones_tecnicas.md` están disponibles para quien quiera explorar el modelo.

<details>
<summary>Versiones de apoyo y alcance de revisión</summary>

El archivo `powerbi/historico/NexaMart_original.pbix` se conserva como histórico. El archivo `powerbi/NexaMart_corregido.zip` es una propuesta editable de apoyo, validada estructuralmente; no generó las capturas actuales y requiere comprobación en Desktop si se utiliza.

La revisión del informe principal comprobó datos, fórmulas, relaciones y capturas aportadas por el autor. El registro está en `docs/revision_pbix_actualizado.json`. La ejecución de DAX no se realizó en este entorno.

</details>
