-- NexaMart | 10 preguntas comerciales y una vista de consumo. MySQL 8.0+.
-- Convención común con Power BI: rankings y participaciones sobre ventas NETAS.
-- Ventas brutas = eventos de venta; importe devuelto positivo; netas = brutas - devuelto.
-- Pedidos y ticket excluyen eventos de devolución. Un producto por pedido en esta versión.
USE nexamart;

-- 1. ¿Qué tiendas generan más ventas y con qué ticket?
SELECT t.tienda_id, t.nombre_tienda, t.ciudad,
       SUM(CASE WHEN f.es_devolucion = 0 THEN f.precio_total ELSE 0 END) AS ventas_brutas,
       -SUM(CASE WHEN f.es_devolucion = 1 THEN f.precio_total ELSE 0 END) AS importe_devoluciones,
       SUM(f.precio_total) AS ventas_netas,
       COUNT(DISTINCT CASE WHEN f.es_devolucion = 0 THEN f.order_id END) AS pedidos_venta,
       ROUND(SUM(CASE WHEN f.es_devolucion = 0 THEN f.precio_total ELSE 0 END) /
             NULLIF(COUNT(DISTINCT CASE WHEN f.es_devolucion = 0 THEN f.order_id END), 0), 2) AS ticket_promedio
FROM factventas f
JOIN dimtienda t ON f.tienda_id = t.tienda_id
GROUP BY t.tienda_id, t.nombre_tienda, t.ciudad
ORDER BY ventas_netas DESC, t.tienda_id;

-- 2. ¿Quién lidera globalmente y dentro de cada tienda?
-- La tienda se atribuye desde el hecho, igual que el filtro de tienda en Power BI.
-- No registrado queda fuera del ranking, pero sus ventas se conservan en el total.
WITH ventas_por_vendedor AS (
    SELECT v.vendedor_id, v.nombre_vendedor, t.tienda_id, t.nombre_tienda,
           SUM(f.precio_total) AS ventas_netas
    FROM factventas f
    JOIN dimvendedor v ON f.vendedor_id = v.vendedor_id
    JOIN dimtienda t ON f.tienda_id = t.tienda_id
    WHERE v.vendedor_id <> -1
    GROUP BY v.vendedor_id, v.nombre_vendedor, t.tienda_id, t.nombre_tienda
)
SELECT vendedor_id, nombre_vendedor, nombre_tienda, ventas_netas,
       RANK() OVER (ORDER BY ventas_netas DESC) AS ranking_global,
       RANK() OVER (PARTITION BY tienda_id ORDER BY ventas_netas DESC) AS ranking_en_tienda
FROM ventas_por_vendedor
ORDER BY ranking_global, vendedor_id, tienda_id;

-- 3. ¿Qué tres productos generan más ingresos NETOS por categoría?
-- ROW_NUMBER y producto_id como desempate: exactamente tres filas por categoría.
WITH ventas_producto AS (
    SELECT p.producto_id, p.categoria, p.nombre_producto,
           SUM(f.cantidad) AS unidades_netas, SUM(f.precio_total) AS ventas_netas
    FROM factventas f
    JOIN dimproducto p ON f.producto_id = p.producto_id
    GROUP BY p.producto_id, p.categoria, p.nombre_producto
), ranked AS (
    SELECT *, ROW_NUMBER() OVER (
        PARTITION BY categoria ORDER BY ventas_netas DESC, producto_id
    ) AS posicion
    FROM ventas_producto
)
SELECT categoria, nombre_producto, unidades_netas, ventas_netas, posicion
FROM ranked WHERE posicion <= 3
ORDER BY categoria, posicion;

-- 4. ¿Qué participación tiene cada método de pago sobre las ventas netas?
SELECT mp.nombre_metodo,
       COUNT(DISTINCT CASE WHEN f.es_devolucion = 0 THEN f.order_id END) AS pedidos_venta,
       SUM(f.precio_total) AS ventas_netas,
       ROUND(100.0 * SUM(f.precio_total) /
             NULLIF((SELECT SUM(precio_total) FROM factventas), 0), 2) AS porcentaje_ventas_netas
FROM factventas f
JOIN dimmetodopago mp ON f.metodo_pago_id = mp.metodo_pago_id
GROUP BY mp.metodo_pago_id, mp.nombre_metodo
ORDER BY ventas_netas DESC, mp.metodo_pago_id;

-- 5. ¿Cómo evolucionan ventas y pedidos? Orden cronológico, no por importe.
SELECT DATE_FORMAT(fecha, '%Y-%m') AS mes,
       SUM(CASE WHEN es_devolucion = 0 THEN precio_total ELSE 0 END) AS ventas_brutas,
       -SUM(CASE WHEN es_devolucion = 1 THEN precio_total ELSE 0 END) AS importe_devoluciones,
       SUM(precio_total) AS ventas_netas,
       COUNT(DISTINCT CASE WHEN es_devolucion = 0 THEN order_id END) AS pedidos_venta
FROM factventas GROUP BY mes ORDER BY mes;

-- 6. ¿Qué clientes VIP acumulan mayor gasto neto?
WITH gasto_cliente AS (
    SELECT c.cliente_id, c.nombre_cliente, c.segmento,
           SUM(f.precio_total) AS gasto_neto,
           COUNT(DISTINCT CASE WHEN f.es_devolucion = 0 THEN f.order_id END) AS num_compras
    FROM factventas f
    JOIN dimcliente c ON f.cliente_id = c.cliente_id
    WHERE c.cliente_id <> -1
    GROUP BY c.cliente_id, c.nombre_cliente, c.segmento
)
SELECT * FROM gasto_cliente WHERE segmento = 'VIP'
ORDER BY gasto_neto DESC, cliente_id LIMIT 10;

-- 7. ¿Qué categorías presentan mayor proporción de EVENTOS de devolución?
-- No es una tasa de unidades devueltas ni de pedidos originales devueltos.
SELECT p.categoria,
       SUM(CASE WHEN f.es_devolucion = 1 THEN 1 ELSE 0 END) AS num_devoluciones,
       COUNT(*) AS total_eventos,
       ROUND(100.0 * SUM(CASE WHEN f.es_devolucion = 1 THEN 1 ELSE 0 END)
             / NULLIF(COUNT(*), 0), 2) AS proporcion_eventos_devolucion_pct
FROM factventas f JOIN dimproducto p ON f.producto_id = p.producto_id
GROUP BY p.categoria
ORDER BY proporcion_eventos_devolucion_pct DESC, p.categoria;

-- 8. ¿Concilian las métricas del SQL con las definiciones del dashboard?
SELECT SUM(CASE WHEN es_devolucion = 0 THEN precio_total ELSE 0 END) AS ventas_brutas,
       -SUM(CASE WHEN es_devolucion = 1 THEN precio_total ELSE 0 END) AS importe_devoluciones,
       SUM(precio_total) AS ventas_netas,
       COUNT(DISTINCT CASE WHEN es_devolucion = 0 THEN order_id END) AS pedidos_venta,
       ROUND(SUM(CASE WHEN es_devolucion = 0 THEN precio_total ELSE 0 END) /
             NULLIF(COUNT(DISTINCT CASE WHEN es_devolucion = 0 THEN order_id END), 0), 2) AS ticket_promedio,
       COUNT(*) AS total_eventos,
       SUM(CASE WHEN es_devolucion = 1 THEN 1 ELSE 0 END) AS eventos_devolucion
FROM factventas;

-- 9. ¿Cuánto de la brecha Singapore-Sydney corresponde a volumen y ticket?
-- Descomposición simétrica: reparte la interacción entre ambos factores.
-- Delta brutas = Delta pedidos * ticket medio de tiendas + Delta ticket * pedidos medios.
-- Delta netas = efecto volumen + efecto ticket - Delta importe devuelto.
-- No prueba causas. Usar tickets SIN redondear para que la identidad concilie.
WITH tienda AS (
    SELECT t.ciudad,
           SUM(CASE WHEN f.es_devolucion = 0 THEN f.precio_total ELSE 0 END) AS brutas,
           -SUM(CASE WHEN f.es_devolucion = 1 THEN f.precio_total ELSE 0 END) AS devuelto,
           SUM(f.precio_total) AS netas,
           COUNT(DISTINCT CASE WHEN f.es_devolucion = 0 THEN f.order_id END) AS pedidos
    FROM factventas f JOIN dimtienda t ON f.tienda_id = t.tienda_id
    WHERE t.ciudad IN ('Singapore', 'Sydney')
    GROUP BY t.ciudad
), tickets AS (
    SELECT *, brutas / NULLIF(pedidos, 0) AS ticket FROM tienda
), comparacion AS (
    SELECT s.pedidos AS pedidos_singapore, y.pedidos AS pedidos_sydney,
           s.ticket AS ticket_singapore, y.ticket AS ticket_sydney,
           s.netas - y.netas AS brecha_neta,
           (s.pedidos - y.pedidos) * (s.ticket + y.ticket) / 2.0 AS efecto_volumen,
           (s.ticket - y.ticket) * (s.pedidos + y.pedidos) / 2.0 AS efecto_ticket,
           -(s.devuelto - y.devuelto) AS efecto_devoluciones
    FROM tickets s JOIN tickets y ON s.ciudad = 'Singapore' AND y.ciudad = 'Sydney'
)
SELECT pedidos_singapore, pedidos_sydney,
       ROUND(ticket_singapore, 2) AS ticket_singapore,
       ROUND(ticket_sydney, 2) AS ticket_sydney,
       ROUND(brecha_neta, 2) AS brecha_neta,
       ROUND(efecto_volumen, 2) AS efecto_volumen,
       ROUND(efecto_ticket, 2) AS efecto_ticket,
       ROUND(efecto_devoluciones, 2) AS efecto_devoluciones,
       ROUND(100.0 * efecto_volumen / NULLIF(brecha_neta, 0), 2) AS volumen_pct_brecha,
       ROUND(100.0 * efecto_ticket / NULLIF(brecha_neta, 0), 2) AS ticket_pct_brecha,
       ROUND(100.0 * efecto_devoluciones / NULLIF(brecha_neta, 0), 2) AS devoluciones_pct_brecha,
       ROUND(brecha_neta - efecto_volumen - efecto_ticket - efecto_devoluciones, 2) AS residual
FROM comparacion;

-- 10. ¿Qué categorías concentran la brecha y cómo cambia la mezcla de compras?
-- La mezcla es otra lectura de la misma brecha: NO se suma a volumen y ticket.
WITH categoria_tienda AS (
    SELECT p.categoria, t.ciudad,
           SUM(f.precio_total) AS netas,
           SUM(CASE WHEN f.es_devolucion = 0 THEN f.precio_total ELSE 0 END) AS brutas,
           COUNT(DISTINCT CASE WHEN f.es_devolucion = 0 THEN f.order_id END) AS pedidos
    FROM factventas f
    JOIN dimtienda t ON f.tienda_id = t.tienda_id
    JOIN dimproducto p ON f.producto_id = p.producto_id
    WHERE t.ciudad IN ('Singapore', 'Sydney')
    GROUP BY p.categoria, t.ciudad
), mezcla AS (
    SELECT *, 100.0 * pedidos / NULLIF(SUM(pedidos) OVER (PARTITION BY ciudad), 0) AS participacion_pedidos,
           brutas / NULLIF(pedidos, 0) AS ticket_categoria
    FROM categoria_tienda
), brechas AS (
    SELECT categoria,
           SUM(CASE WHEN ciudad = 'Singapore' THEN netas ELSE 0 END) AS netas_singapore,
           SUM(CASE WHEN ciudad = 'Sydney' THEN netas ELSE 0 END) AS netas_sydney,
           SUM(CASE WHEN ciudad = 'Singapore' THEN pedidos ELSE 0 END) AS pedidos_singapore,
           SUM(CASE WHEN ciudad = 'Sydney' THEN pedidos ELSE 0 END) AS pedidos_sydney,
           MAX(CASE WHEN ciudad = 'Singapore' THEN participacion_pedidos END) AS mezcla_singapore_pct,
           MAX(CASE WHEN ciudad = 'Sydney' THEN participacion_pedidos END) AS mezcla_sydney_pct,
           MAX(CASE WHEN ciudad = 'Singapore' THEN ticket_categoria END) AS ticket_singapore,
           MAX(CASE WHEN ciudad = 'Sydney' THEN ticket_categoria END) AS ticket_sydney
    FROM mezcla GROUP BY categoria
)
SELECT categoria, netas_singapore, netas_sydney,
       netas_singapore - netas_sydney AS contribucion_brecha,
       ROUND(100.0 * (netas_singapore - netas_sydney) /
             NULLIF(SUM(netas_singapore - netas_sydney) OVER (), 0), 2) AS porcentaje_brecha,
       pedidos_singapore, pedidos_sydney,
       ROUND(mezcla_singapore_pct, 2) AS mezcla_singapore_pct,
       ROUND(mezcla_sydney_pct, 2) AS mezcla_sydney_pct,
       ROUND(ticket_singapore, 2) AS ticket_singapore,
       ROUND(ticket_sydney, 2) AS ticket_sydney
FROM brechas ORDER BY contribucion_brecha DESC, categoria;

-- Vista: conserva todos los eventos y aporta campos explícitos para conciliación.
CREATE OR REPLACE VIEW vw_ventas_analitico AS
SELECT f.order_id, f.fecha,
       f.tienda_id, t.nombre_tienda, t.ciudad, t.pais, t.region,
       f.vendedor_id, v.nombre_vendedor,
       f.cliente_id, c.nombre_cliente, c.segmento,
       f.producto_id, p.nombre_producto, p.categoria,
       f.metodo_pago_id, mp.nombre_metodo,
       f.cantidad, f.precio_unitario, f.precio_total, f.es_devolucion,
       CASE WHEN f.es_devolucion = 0 THEN f.precio_total ELSE 0 END AS importe_venta_bruta,
       CASE WHEN f.es_devolucion = 1 THEN -f.precio_total ELSE 0 END AS importe_devuelto
FROM factventas f
LEFT JOIN dimtienda t ON f.tienda_id = t.tienda_id
LEFT JOIN dimvendedor v ON f.vendedor_id = v.vendedor_id
LEFT JOIN dimcliente c ON f.cliente_id = c.cliente_id
LEFT JOIN dimproducto p ON f.producto_id = p.producto_id
LEFT JOIN dimmetodopago mp ON f.metodo_pago_id = mp.metodo_pago_id;
