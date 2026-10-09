-- NexaMart | Controles del snapshot recuperado del PBIX. MySQL 8.0+.
USE nexamart;

-- Conteos esperados: 4, 9, 31, 171, 5 y 757.
SELECT 'dimtienda' AS tabla, COUNT(*) AS registros FROM dimtienda
UNION ALL SELECT 'dimvendedor', COUNT(*) FROM dimvendedor
UNION ALL SELECT 'dimproducto', COUNT(*) FROM dimproducto
UNION ALL SELECT 'dimcliente', COUNT(*) FROM dimcliente
UNION ALL SELECT 'dimmetodopago', COUNT(*) FROM dimmetodopago
UNION ALL SELECT 'factventas', COUNT(*) FROM factventas;

-- 757 eventos, 751 ventas y 6 devoluciones.
SELECT COUNT(*) AS eventos, COUNT(DISTINCT order_id) AS ids_distintos,
       SUM(CASE WHEN es_devolucion = 0 THEN 1 ELSE 0 END) AS ventas,
       SUM(CASE WHEN es_devolucion = 1 THEN 1 ELSE 0 END) AS devoluciones,
       MIN(fecha) AS fecha_inicio, MAX(fecha) AS fecha_fin
FROM factventas;

-- 104718.63 - 866.89 = 103851.74; ticket de compra 139.44; proporción 0.79%.
SELECT SUM(CASE WHEN es_devolucion = 0 THEN precio_total ELSE 0 END) AS ventas_brutas,
       -SUM(CASE WHEN es_devolucion = 1 THEN precio_total ELSE 0 END) AS importe_devoluciones,
       SUM(precio_total) AS neto,
       COUNT(DISTINCT CASE WHEN es_devolucion = 0 THEN order_id END) AS pedidos_venta,
       ROUND(SUM(CASE WHEN es_devolucion = 0 THEN precio_total ELSE 0 END) / NULLIF(COUNT(DISTINCT CASE WHEN es_devolucion = 0 THEN order_id END), 0), 2) AS ticket_promedio,
       ROUND(100.0 * SUM(CASE WHEN es_devolucion = 1 THEN 1 ELSE 0 END) / NULLIF(COUNT(*), 0), 2) AS devoluciones_pct
FROM factventas;

-- 10 clientes y 6 vendedores sin identificar, conservados.
SELECT SUM(CASE WHEN cliente_id = -1 THEN 1 ELSE 0 END) AS sin_cliente,
       SUM(CASE WHEN vendedor_id = -1 THEN 1 ELSE 0 END) AS sin_vendedor
FROM factventas;

-- Todas las referencias deben devolver cero hechos sin dimensión.
SELECT 'cliente' AS referencia, COUNT(*) AS hechos_sin_dimension
FROM factventas f LEFT JOIN dimcliente d ON f.cliente_id = d.cliente_id WHERE d.cliente_id IS NULL
UNION ALL SELECT 'vendedor', COUNT(*)
FROM factventas f LEFT JOIN dimvendedor d ON f.vendedor_id = d.vendedor_id WHERE d.vendedor_id IS NULL
UNION ALL SELECT 'producto', COUNT(*)
FROM factventas f LEFT JOIN dimproducto d ON f.producto_id = d.producto_id WHERE d.producto_id IS NULL
UNION ALL SELECT 'tienda', COUNT(*)
FROM factventas f LEFT JOIN dimtienda d ON f.tienda_id = d.tienda_id WHERE d.tienda_id IS NULL
UNION ALL SELECT 'metodo_pago', COUNT(*)
FROM factventas f LEFT JOIN dimmetodopago d ON f.metodo_pago_id = d.metodo_pago_id WHERE d.metodo_pago_id IS NULL;

SELECT COUNT(*) AS importes_incoherentes
FROM factventas WHERE precio_total <> ROUND(precio_unitario * cantidad, 2);
SELECT COUNT(*) AS banderas_incoherentes
FROM factventas WHERE es_devolucion IS NULL OR es_devolucion NOT IN (0, 1)
 OR (cantidad < 0 AND es_devolucion <> 1) OR (cantidad >= 0 AND es_devolucion = 1);

-- 10499.58 - 249.99 = 10249.59.
SELECT p.nombre_producto,
       SUM(CASE WHEN f.es_devolucion = 0 THEN f.precio_total ELSE 0 END) AS ventas_brutas,
       -SUM(CASE WHEN f.es_devolucion = 1 THEN f.precio_total ELSE 0 END) AS importe_devoluciones,
       SUM(f.precio_total) AS neto
FROM factventas f JOIN dimproducto p ON f.producto_id = p.producto_id
WHERE p.nombre_producto = 'Smartwatch Series X'
GROUP BY p.producto_id, p.nombre_producto;
