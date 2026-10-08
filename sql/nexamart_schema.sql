-- NexaMart | Esquema reconstruido a partir del DDL compartido.
-- MySQL 8.0+. Crear en una instancia de trabajo nueva.
-- Esquema sin datos; cargar después nexamart_snapshot_data.sql.
-- Grano actual: un producto por order_id; una sola fila por pedido.
CREATE DATABASE IF NOT EXISTS nexamart
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE nexamart;

CREATE TABLE dimtienda (
    tienda_id INT PRIMARY KEY,
    nombre_tienda VARCHAR(100) NOT NULL,
    ciudad VARCHAR(80),
    pais VARCHAR(80),
    region VARCHAR(50)
);
CREATE TABLE dimvendedor (
    vendedor_id INT PRIMARY KEY,
    nombre_vendedor VARCHAR(120) NOT NULL,
    tienda_id INT,
    FOREIGN KEY (tienda_id) REFERENCES dimtienda(tienda_id)
);
CREATE TABLE dimproducto (
    producto_id INT PRIMARY KEY,
    nombre_producto VARCHAR(150) NOT NULL,
    categoria VARCHAR(60),
    precio_unitario DECIMAL(10,2)
);
CREATE TABLE dimcliente (
    cliente_id INT PRIMARY KEY,
    nombre_cliente VARCHAR(120),
    email VARCHAR(150),
    segmento VARCHAR(20)
);
CREATE TABLE dimmetodopago (
    metodo_pago_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre_metodo VARCHAR(50) UNIQUE NOT NULL
);
CREATE TABLE factventas (
    order_id INT PRIMARY KEY,
    fecha DATE NOT NULL,
    tienda_id INT,
    vendedor_id INT,
    cliente_id INT,
    producto_id INT NOT NULL,
    metodo_pago_id INT,
    cantidad INT NOT NULL,
    precio_unitario DECIMAL(10,2) NOT NULL,
    precio_total DECIMAL(10,2) NOT NULL,
    es_devolucion TINYINT(1) DEFAULT 0,
    FOREIGN KEY (tienda_id) REFERENCES dimtienda(tienda_id),
    FOREIGN KEY (vendedor_id) REFERENCES dimvendedor(vendedor_id),
    FOREIGN KEY (cliente_id) REFERENCES dimcliente(cliente_id),
    FOREIGN KEY (producto_id) REFERENCES dimproducto(producto_id),
    FOREIGN KEY (metodo_pago_id) REFERENCES dimmetodopago(metodo_pago_id)
);

-- La carga original debe insertar los miembros -1 / No registrado
-- de dimcliente y dimvendedor ANTES de insertar los hechos asociados.
-- Este archivo mantiene la relación vendedor-tienda del MySQL original.
-- En Power BI debe evitarse un segundo camino activo hacia factventas.
