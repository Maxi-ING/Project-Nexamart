# Singapore frente a Sydney: volumen, ticket y catálogo

**Conclusión:** Singapore supera a Sydney en 8.690,55 unidades monetarias netas. La descomposición atribuye la mayor contribución al ticket por compra; el análisis por categoría concentra la brecha en Sports & Fitness y Smart Home. Esto orienta una revisión del catálogo y las cantidades por compra, además del volumen de pedidos.

Fuente: consultas 9 y 10 de [consultas_analiticas.sql](../sql/consultas_analiticas.sql), sobre el mismo snapshot utilizado en Power BI. Período completo: septiembre de 2025–agosto de 2026. Importes simulados, sin conversión de divisas documentada.

## Comparación de las tiendas

| Indicador | Singapore | Sydney |
|---|---:|---:|
| Ventas brutas | 31.390,09 | 22.372,59 |
| Importe devuelto | 416,93 | 89,98 |
| **Ventas netas** | **30.973,16** | **22.282,61** |
| Compras, sin eventos de devolución | 197 | 177 |
| Ticket bruto por compra | 159,34 | 126,40 |

Singapore registra **20 compras más** y un ticket **32,94 mayor**. El ticket utiliza ventas brutas / compras; no divide ingresos netos entre ventas y devoluciones mezcladas.

## Descomposición de la brecha

Se utiliza una descomposición simétrica: reparte la interacción entre volumen y ticket en partes iguales y evita elegir arbitrariamente una tienda como referencia. Se calcula con tickets sin redondear.

| Factor | Contribución a la brecha neta | % de la brecha |
|---|---:|---:|
| Más compras | +2.857,39 | 32,88 % |
| Mayor ticket por compra | +6.160,11 | 70,88 % |
| Mayor importe devuelto en Singapore | −326,95 | −3,76 % |
| **Brecha neta** | **8.690,55** | **100,00 %** |

La identidad es: **Δ netas = Δ compras × ticket medio de las tiendas + Δ ticket × compras medias − Δ importe devuelto**. Las contribuciones positivas superan el 100 % antes de descontar las devoluciones. Es una explicación contable de la diferencia, no una prueba de causalidad.

## Dónde se concentra la diferencia

| Categoría | Neto Singapore | Neto Sydney | Contribución a la brecha |
|---|---:|---:|---:|
| Sports & Fitness | 8.993,50 | 3.304,51 | +5.688,99 |
| Smart Home | 7.574,34 | 4.954,55 | +2.619,79 |
| Fashion | 2.894,49 | 1.809,65 | +1.084,84 |
| Beauty & Personal Care | 1.491,56 | 1.264,56 | +227,00 |
| Electronics | 10.019,27 | 10.949,34 | −930,07 |
| **Total** | **30.973,16** | **22.282,61** | **8.690,55** |

Sports & Fitness aporta **65,46 %** de la brecha con **37 compras en cada tienda**. El ticket bruto de la categoría es 245,55 en Singapore y 89,31 en Sydney. Foldable Treadmill registra **20 unidades netas frente a 4**, con una diferencia de 6.399,84; los demás productos de la categoría compensan parte de esa ventaja. Sydney, en cambio, supera a Singapore en Electronics.

La consulta 10 incorpora también la participación de compras de cada categoría dentro de cada tienda y sus tickets. **Las contribuciones por categoría son otra lectura de la misma brecha: no se suman a los efectos de volumen y ticket.**

## Decisión que orienta el análisis

Priorizar una revisión comercial de Sports & Fitness en Sydney: contrastar disponibilidad, surtido y promociones de Foldable Treadmill, y revisar cuántas unidades se compran por pedido. Después, profundizar Smart Home. Mantener Electronics como referencia de una categoría donde Sydney ya genera más ingresos.

Estas son acciones para investigar y validar. No hay información de stock, margen, tráfico, horarios, promociones ejecutadas ni metas que permita afirmar por qué se produce la diferencia o garantizar una mejora. La recomendación se apoya en localizar la brecha y formular una comprobación comercial concreta.

[Resultados de la descomposición](../data/resultados/comparacion_tiendas.csv) · [Resultados por categoría](../data/resultados/mezcla_categorias.csv)
