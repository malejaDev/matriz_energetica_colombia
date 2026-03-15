--  CREACIÓN DE BASE DE DATOS
create database bd_matriz_energetica_colombia;
use bd_matriz_energetica_colombia;

-- CREACION DE TABLA TIPO_ENERGIA
CREATE TABLE tipo_energia (
    id_tipo_energia INT AUTO_INCREMENT PRIMARY KEY,
    nombre VARCHAR(50) NOT NULL,
    descripcion VARCHAR(200)
);


-- CREACION DE TABLA PERIODO
CREATE TABLE periodo (
    id_periodo INT AUTO_INCREMENT PRIMARY KEY,
    anio INT NOT NULL
);

-- CREACION DE TABLA ESTADISTICAS_ENERGIA
CREATE TABLE estadisticas_energia (
    id_estadistica INT AUTO_INCREMENT PRIMARY KEY,
    id_tipo_energia INT NOT NULL,
    id_periodo INT NOT NULL,

    generacion_gwh DECIMAL(12,2),
    oferta_gwh DECIMAL(12,2),
    demanda_gwh DECIMAL(12,2),
    costo_mwh DECIMAL(10,2),
    porcentaje_cobertura DECIMAL(5,2),
    inversion_usd_millones DECIMAL(12,2),
    emisiones_co2_toneladas DECIMAL(15,2),

    FOREIGN KEY (id_tipo_energia) REFERENCES tipo_energia(id_tipo_energia),
    FOREIGN KEY (id_periodo) REFERENCES periodo(id_periodo)
);

