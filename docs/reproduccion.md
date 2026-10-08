# NexaMart | Revisar y reproducir el análisis

## Revisar Power BI

Descarga [NexaMart.pbix](../powerbi/NexaMart.pbix) y ábrelo en Power BI Desktop. El archivo conserva los datos importados del autor. Se verificaron sus datos, metadatos e integridad ZIP; no se abrió Desktop en este entorno.

Antes de validar gráficos temporales:

1. Crea la relación activa **DimCalendario[Date] (1) → nexamart factventas[fecha] (*)**, con filtro único desde calendario. Ambos campos deben ser de tipo fecha.
2. Marca DimCalendario como tabla de fechas, usando Date.
3. Ordena el gráfico de tendencia por el campo de fecha de mes, de forma ascendente.
4. Comprueba que seleccionar un mes cambie el importe y que la suma de los doce meses concilie con **103.851,74**.

La relación aparece en la captura, pero falta en los metadatos del PBIX adjunto. La definición guardada del gráfico registra orden por ventas descendente. El archivo se conserva original para mantener su trazabilidad.

Para actualizar desde MySQL, ajusta el origen de las seis consultas a tu servidor y base `nexamart` y configura el conector y tus credenciales localmente. Los nombres físicos de tablas están en minúsculas, como los que utiliza el PBIX.

El tema `powerbi/tema_nexamart.json` recupera la paleta personalizada; se importa desde **Vista → Temas → Explorar temas**. Los estilos completos están en el PBIX.

## Restaurar el snapshot en MySQL

Usa MySQL 8.0 o superior, en una base de trabajo nueva. Ejecuta en este orden desde Workbench:

1. `sql/nexamart_schema.sql`: crea seis tablas vacías.
2. `sql/nexamart_snapshot_data.sql`: carga dimensiones y hechos recuperados del PBIX.
3. `sql/controles_snapshot.sql`: comprueba conteos, referencias y métricas.
4. `sql/consultas_analiticas.sql`: ejecuta las siete preguntas y crea la vista propuesta.

La carga requiere tablas vacías y no debe ejecutarse dos veces. No contiene DROP ni reemplaza claves existentes. Si ya tienes la base original, usa otra instancia de trabajo para esta restauración.

Desde una terminal con el cliente MySQL:

```bash
mysql -u TU_USUARIO -p < sql/nexamart_schema.sql
mysql -u TU_USUARIO -p < sql/nexamart_snapshot_data.sql
mysql -u TU_USUARIO -p < sql/controles_snapshot.sql
mysql -u TU_USUARIO -p < sql/consultas_analiticas.sql
```

Introduce la contraseña cuando el cliente la solicite. El repositorio no incluye credenciales.

| Control | Resultado esperado |
|---|---:|
| Tiendas / vendedores / productos | 4 / 9 / 31 |
| Clientes / métodos / hechos | 171 / 5 / 757 |
| Ventas positivas / devoluciones | 751 / 6 |
| Ventas sin devoluciones | 104.718,63 |
| Devoluciones | −866,89 |
| Neto | 103.851,74 |
| Hechos sin dimensión | 0 |
| Diferencias precio × cantidad | 0 |

SQL comercial excluye devoluciones; el DAX original las incluye. Total Pedidos y Ticket Promedio también incluyen eventos de devolución en su denominador. La ejecución sobre tu servidor completa la validación de la instalación MySQL.

## Volver a extraer datos y fórmulas

Desde la raíz del repositorio, en un entorno Python:

```bash
python -m pip install -r requirements_snapshot.txt
python scripts/exportar_snapshot_pbix.py --pbix powerbi/NexaMart.pbix --destino snapshot_exportado
```

El script exporta seis tablas, calendario, medidas, relaciones, paleta, carga MySQL y manifiesto. Utiliza otro directorio de destino para comparar con los archivos publicados.

Es una utilidad de inspección añadida a la entrega. **No sustituye al generador ni al ETL original**, y no recupera duplicados u outliers retirados antes de importar los datos.
