-- NexaMart | 7 consultas compartidas + vista añadida en esta publicación.
-- MySQL 8.0+. Requiere esquema y DATOS ORIGINALES cargados.
-- Adaptaciones editoriales: identificadores en GROUP BY, desempates,
-- NULLIF en divisiones. Ranking por tienda asignada al vendedor, como el original.
-- Las capturas documentan la versión original, no estas adaptaciones.
USE nexamart;

-- Comprobación: 757 registros en la base original (incluye devoluciones).
SELECT COUNT(*) AS total_registros FROM FactVentas;

-- 1. Ventas por tienda: importes y pedidos SIN devoluciones.
SELECT t.nombre_tienda, t.region,
       SUM(f.precio_total) AS ventas_sin_devoluciones,
       COUNT(DISTINCT f.order_id) AS pedidos_sin_devoluciones
FROM FactVentas f
JOIN DimTienda t ON f.tienda_id = t.tienda_id
WHERE f.es_devolucion = 0
GROUP BY t.tienda_id, t.nombre_tienda, t.region
ORDER BY ventas_sin_devoluciones DESC, t.tienda_id;

-- 2. Ranking: ingresos por vendedor y su tienda asignada en DimVendedor.
-- La versión actual asigna cada vendedor a una sola tienda.
-- Se excluye No registrado. Si hubiera movilidad de vendedores,
-- se debería modelar esa historia antes de atribuir los ingresos por tienda.
WITH ventas_por_vendedor AS (
    SELECT v.vendedor_id, v.nombre_vendedor,
           t.tienda_id, t.nombre_tienda,
           SUM(f.precio_total) AS ventas_totales
    FROM FactVentas f
    JOIN DimVendedor v ON f.vendedor_id = v.vendedor_id
    JOIN DimTienda t ON v.tienda_id = t.tienda_id
    WHERE f.es_devolucion = 0 AND v.vendedor_id <> -1
    GROUP BY v.vendedor_id, v.nombre_vendedor, t.tienda_id, t.nombre_tienda
)
SELECT vendedor_id, nombre_vendedor, nombre_tienda, ventas_totales,
       RANK() OVER (ORDER BY ventas_totales DESC) AS ranking_global,
       RANK() OVER (PARTITION BY tienda_id ORDER BY ventas_totales DESC) AS ranking_en_tienda
FROM ventas_por_vendedor
ORDER BY ranking_global, vendedor_id, tienda_id;

-- 3. Top 3 productos POR INGRESOS dentro de cada categoría.
-- ROW_NUMBER limita a tres filas; producto_id desempata importes iguales.
WITH ventas_producto AS (
    SELECT p.producto_id, p.categoria, p.nombre_producto,
           SUM(f.cantidad) AS unidades_vendidas,
           SUM(f.precio_total) AS ventas_totales
    FROM FactVentas f
    JOIN DimProducto p ON f.producto_id = p.producto_id
    WHERE f.es_devolucion = 0
    GROUP BY p.producto_id, p.categoria, p.nombre_producto
), ranked AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY categoria ORDER BY ventas_totales DESC, producto_id
    ) AS posicion
    FROM ventas_producto
)
SELECT categoria, nombre_producto, unidades_vendidas, ventas_totales, posicion
FROM ranked
WHERE posicion <= 3
ORDER BY categoria, posicion;

-- 4. Participación de métodos de pago sobre importes sin devoluciones.
-- NULLIF devuelve NULL si el total es cero: evita división por cero.
SELECT mp.nombre_metodo,
       COUNT(*) AS num_transacciones,
       SUM(f.precio_total) AS ventas_totales,
       ROUND(100.0 * SUM(f.precio_total) / NULLIF(
           (SELECT SUM(precio_total) FROM FactVentas WHERE es_devolucion = 0),
           0), 2) AS porcentaje_ventas
FROM FactVentas f
JOIN DimMetodoPago mp ON f.metodo_pago_id = mp.metodo_pago_id
WHERE f.es_devolucion = 0
GROUP BY mp.metodo_pago_id, mp.nombre_metodo
ORDER BY ventas_totales DESC, mp.metodo_pago_id;

-- 5. Evolución mensual: excluye devoluciones.
SELECT DATE_FORMAT(fecha, '%Y-%m') AS mes,
       SUM(precio_total) AS ventas_totales,
       COUNT(DISTINCT order_id) AS total_pedidos
FROM FactVentas
WHERE es_devolucion = 0
GROUP BY mes
ORDER BY mes;

-- 6. Top 10 clientes VIP por gasto sin devoluciones.
WITH gasto_cliente AS (
    SELECT c.cliente_id, c.nombre_cliente, c.segmento,
           SUM(f.precio_total) AS gasto_total,
           COUNT(DISTINCT f.order_id) AS num_compras
    FROM FactVentas f
    JOIN DimCliente c ON f.cliente_id = c.cliente_id
    WHERE f.es_devolucion = 0 AND c.cliente_id <> -1
    GROUP BY c.cliente_id, c.nombre_cliente, c.segmento
)
SELECT * FROM gasto_cliente
WHERE segmento = 'VIP'
ORDER BY gasto_total DESC, cliente_id
LIMIT 10;

-- 7. Porcentaje de REGISTROS marcados como devolución por categoría.
-- Denominador: todas las filas de la categoría, incluidas devoluciones.
-- No equivale a unidades devueltas / unidades vendidas.
SELECT p.categoria,
       SUM(CASE WHEN f.es_devolucion = 1 THEN 1 ELSE 0 END) AS num_devoluciones,
       COUNT(*) AS total_registros,
       ROUND(100.0 * SUM(CASE WHEN f.es_devolucion = 1 THEN 1 ELSE 0 END)
           / NULLIF(COUNT(*), 0), 2) AS tasa_devolucion_registros_pct
FROM FactVentas f
JOIN DimProducto p ON f.producto_id = p.producto_id
GROUP BY p.categoria
ORDER BY tasa_devolucion_registros_pct DESC, p.categoria;

-- 8. Vista de consumo propuesta: conserva TODOS los hechos mediante
-- LEFT JOIN. Esta definición se añadió aquí; el DDL original no fue recibido.
-- Incluye devoluciones; el consumidor decide el filtro de negocio.
-- CREATE VIEW no reemplaza una vista existente de manera automática.
CREATE VIEW vw_ventas_analitico AS
SELECT f.order_id, f.fecha,
       f.tienda_id, t.nombre_tienda, t.ciudad, t.pais, t.region,
       f.vendedor_id, v.nombre_vendedor,
       f.cliente_id, c.nombre_cliente, c.segmento,
       f.producto_id, p.nombre_producto, p.categoria,
       f.metodo_pago_id, mp.nombre_metodo,
       f.cantidad, f.precio_unitario, f.precio_total, f.es_devolucion
FROM FactVentas f
LEFT JOIN DimTienda t ON f.tienda_id = t.tienda_id
LEFT JOIN DimVendedor v ON f.vendedor_id = v.vendedor_id
LEFT JOIN DimCliente c ON f.cliente_id = c.cliente_id
LEFT JOIN DimProducto p ON f.producto_id = p.producto_id
LEFT JOIN DimMetodoPago mp ON f.metodo_pago_id = mp.metodo_pago_id;
