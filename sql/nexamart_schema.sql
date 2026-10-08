-- NexaMart | Esquema reconstruido a partir del DDL compartido.
-- MySQL 8.0+. Crear en una instancia de trabajo nueva.
-- NO contiene INSERT ni reproduce la carga de 757 registros.
-- Grano actual: un producto por order_id; una sola fila por pedido.
CREATE DATABASE IF NOT EXISTS nexamart
  CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE nexamart;

CREATE TABLE DimTienda (
    tienda_id INT PRIMARY KEY,
    nombre_tienda VARCHAR(100) NOT NULL,
    ciudad VARCHAR(80),
    pais VARCHAR(80),
    region VARCHAR(50)
);
CREATE TABLE DimVendedor (
    vendedor_id INT PRIMARY KEY,
    nombre_vendedor VARCHAR(120) NOT NULL,
    tienda_id INT,
    FOREIGN KEY (tienda_id) REFERENCES DimTienda(tienda_id)
);
CREATE TABLE DimProducto (
    producto_id INT PRIMARY KEY,
    nombre_producto VARCHAR(150) NOT NULL,
    categoria VARCHAR(60),
    precio_unitario DECIMAL(10,2)
);
CREATE TABLE DimCliente (
    cliente_id INT PRIMARY KEY,
    nombre_cliente VARCHAR(120),
    email VARCHAR(150),
    segmento VARCHAR(20)
);
CREATE TABLE DimMetodoPago (
    metodo_pago_id INT PRIMARY KEY AUTO_INCREMENT,
    nombre_metodo VARCHAR(50) UNIQUE NOT NULL
);
CREATE TABLE FactVentas (
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
    FOREIGN KEY (tienda_id) REFERENCES DimTienda(tienda_id),
    FOREIGN KEY (vendedor_id) REFERENCES DimVendedor(vendedor_id),
    FOREIGN KEY (cliente_id) REFERENCES DimCliente(cliente_id),
    FOREIGN KEY (producto_id) REFERENCES DimProducto(producto_id),
    FOREIGN KEY (metodo_pago_id) REFERENCES DimMetodoPago(metodo_pago_id)
);

-- La carga original debe insertar los miembros -1 / No registrado
-- de DimCliente y DimVendedor ANTES de insertar los hechos asociados.
-- Este archivo mantiene la relación vendedor-tienda del MySQL original.
-- En Power BI debe evitarse un segundo camino activo hacia FactVentas.
