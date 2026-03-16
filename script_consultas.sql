-- ============================================================
-- SCRIPT DE CONSULTAS
-- Base de datos: bd_matriz_energetica_colombia
-- Objetivo:
-- Analizar la generación, demanda, inversión y emisiones
-- de los distintos tipos de energía en Colombia.
-- ============================================================



-- ============================================================
-- 1. CONSULTAS DE EXPLORACIÓN DE DATOS
-- Permiten visualizar el contenido básico de cada tabla
-- ============================================================

-- Tabla de tipos de energía (solar, hidráulica, eólica, etc.)
select * from tipo_energia;

-- Tabla de periodos analizados (años)
select * from periodo;

-- Tabla principal con estadísticas energéticas
select * from estadisticas_energia;



-- ============================================================
-- 2. CONSULTA DE INTEGRACIÓN DE TABLAS
-- Une estadísticas con su tipo de energía y el periodo
-- ============================================================

select  
    te.nombre as tipo_energia,
    p.anio as periodo,
    est.*
from estadisticas_energia est
inner join tipo_energia te 
    on te.id_tipo_energia = est.id_tipo_energia
inner join periodo p 
    on p.id_periodo = est.id_periodo;



-- ============================================================
-- 3. ANÁLISIS GENERAL DE LA MATRIZ ENERGÉTICA
-- Totales y promedios por tipo de energía y año
-- ============================================================

SELECT 
    p.anio,
    te.nombre AS tipo_energia,
    SUM(ee.generacion_gwh)        AS total_generacion_gwh,
    SUM(ee.oferta_gwh)            AS total_oferta_gwh,
    SUM(ee.demanda_gwh)           AS total_demanda_gwh,
    AVG(ee.costo_mwh)             AS promedio_costo_mwh,
    AVG(ee.porcentaje_cobertura)  AS promedio_cobertura,
    SUM(ee.inversion_usd_millones)AS total_inversion_usd_millones,
    SUM(ee.emisiones_co2_toneladas) AS total_emisiones_co2
FROM estadisticas_energia ee
INNER JOIN tipo_energia te ON ee.id_tipo_energia = te.id_tipo_energia
INNER JOIN periodo p       ON ee.id_periodo = p.id_periodo
GROUP BY p.anio, te.nombre
ORDER BY p.anio, te.nombre;



-- ============================================================
-- 4. ANÁLISIS FILTRADO POR ENERGÍA SOLAR
-- Permite observar el comportamiento de esta fuente
-- a lo largo del tiempo
-- ============================================================

SELECT 
    p.anio,
    te.nombre AS tipo_energia,
    SUM(ee.generacion_gwh)        AS total_generacion_gwh,
    SUM(ee.oferta_gwh)            AS total_oferta_gwh,
    SUM(ee.demanda_gwh)           AS total_demanda_gwh,
    AVG(ee.costo_mwh)             AS promedio_costo_mwh,
    AVG(ee.porcentaje_cobertura)  AS promedio_cobertura,
    SUM(ee.inversion_usd_millones)AS total_inversion_usd_millones,
    SUM(ee.emisiones_co2_toneladas) AS total_emisiones_co2
FROM estadisticas_energia ee
INNER JOIN tipo_energia te ON ee.id_tipo_energia = te.id_tipo_energia
INNER JOIN periodo p       ON ee.id_periodo = p.id_periodo
where te.nombre = 'Solar'
GROUP BY p.anio, te.nombre
ORDER BY p.anio, te.nombre;



-- ============================================================
-- 5. EFICIENCIA ENERGÉTICA
-- Relación entre generación y demanda
-- ============================================================

SELECT 
    te.nombre AS tipo_energia,
    SUM(ee.generacion_gwh) AS total_generacion_gwh,
    SUM(ee.demanda_gwh) AS total_demanda_gwh,
    ROUND(SUM(ee.generacion_gwh) / SUM(ee.demanda_gwh), 4) 
        AS eficiencia_energetica
FROM estadisticas_energia ee
INNER JOIN tipo_energia te ON ee.id_tipo_energia = te.id_tipo_energia
GROUP BY te.nombre
ORDER BY eficiencia_energetica DESC;



-- ============================================================
-- 6. ANÁLISIS DE COSTOS DE GENERACIÓN
-- Permite ver promedio, mínimo y máximo del costo por MWh
-- ============================================================

SELECT 
    te.nombre AS tipo_energia,
    SUM(ee.generacion_gwh) AS total_generacion_gwh,
    SUM(ee.demanda_gwh) AS total_demanda_gwh,
    ROUND(SUM(ee.generacion_gwh) / SUM(ee.demanda_gwh), 4) 
        AS eficiencia_energetica,
    ROUND(AVG(ee.costo_mwh), 2) AS promedio_costo_mwh,
    ROUND(MIN(ee.costo_mwh), 2) AS min_costo_mwh,
    ROUND(MAX(ee.costo_mwh), 2) AS max_costo_mwh
FROM estadisticas_energia ee
INNER JOIN tipo_energia te ON ee.id_tipo_energia = te.id_tipo_energia
GROUP BY te.nombre
ORDER BY eficiencia_energetica DESC;



-- ============================================================
-- 7. RETORNO DE INVERSIÓN ENERGÉTICA
-- Cuánta energía se genera por cada dólar invertido
-- ============================================================

SELECT 
    te.nombre AS tipo_energia,
    SUM(ee.generacion_gwh) AS total_generacion_gwh,
    SUM(ee.demanda_gwh) AS total_demanda_gwh,
    ROUND(SUM(ee.generacion_gwh) / SUM(ee.demanda_gwh), 4) 
        AS eficiencia_energetica,
    ROUND(SUM(ee.inversion_usd_millones), 2) 
        AS total_inversion_usd_millones,
    ROUND(SUM(ee.generacion_gwh) / SUM(ee.inversion_usd_millones), 4)
        AS generacion_por_dolar_invertido
FROM estadisticas_energia ee
INNER JOIN tipo_energia te ON ee.id_tipo_energia = te.id_tipo_energia
GROUP BY te.nombre
ORDER BY generacion_por_dolar_invertido DESC;



-- ============================================================
-- 8. NIVEL DE COBERTURA ENERGÉTICA
-- Clasificación del porcentaje de cobertura
-- ============================================================

SELECT 
    p.anio,
    te.nombre AS tipo_energia,
    ROUND(AVG(ee.porcentaje_cobertura) * 100, 2) 
        AS cobertura_promedio_pct,

    CASE
        WHEN AVG(ee.porcentaje_cobertura) >= 0.8 THEN 'ALTA'
        WHEN AVG(ee.porcentaje_cobertura) >= 0.5 THEN 'MEDIA'
        ELSE 'BAJA'
    END AS nivel_cobertura

FROM estadisticas_energia ee
INNER JOIN tipo_energia te ON ee.id_tipo_energia = te.id_tipo_energia
INNER JOIN periodo p ON ee.id_periodo = p.id_periodo

GROUP BY p.anio, te.nombre
ORDER BY p.anio, cobertura_promedio_pct DESC;



-- ============================================================
-- 9. RANKING DE ENERGÍAS MÁS LIMPIAS
-- Basado en emisiones de CO2 por generación
-- ============================================================

SELECT 
    te.nombre AS tipo_energia,

    ROUND(SUM(ee.emisiones_co2_toneladas), 2) 
        AS total_emisiones_co2,

    ROUND(SUM(ee.generacion_gwh), 2) 
        AS total_generacion_gwh,

    ROUND(
        SUM(ee.emisiones_co2_toneladas) /
        SUM(ee.generacion_gwh), 4
    ) AS toneladas_co2_por_gwh,

    RANK() OVER (
        ORDER BY SUM(ee.emisiones_co2_toneladas) /
                 SUM(ee.generacion_gwh) ASC
    ) AS ranking_mas_limpia

FROM estadisticas_energia ee
INNER JOIN tipo_energia te 
    ON ee.id_tipo_energia = te.id_tipo_energia

GROUP BY te.nombre
ORDER BY ranking_mas_limpia;



-- ============================================================
-- 10. CONSULTA CON HAVING
-- Energías que tienen más de un registro en la base
-- ============================================================

SELECT 
    te.nombre,
    COUNT(*) AS cantidad_registros
FROM estadisticas_energia ee
INNER JOIN tipo_energia te
    ON ee.id_tipo_energia = te.id_tipo_energia
GROUP BY te.nombre
HAVING COUNT(*) > 1;



-- ============================================================
-- 11. SUBCONSULTA EN SELECT
-- Comparación entre generación de cada energía
-- y el promedio global
-- ============================================================

SELECT 
    te.nombre,
    SUM(ee.generacion_gwh) AS total_generacion,

    (SELECT AVG(generacion_gwh)
     FROM estadisticas_energia) 
     AS promedio_global

FROM estadisticas_energia ee
INNER JOIN tipo_energia te
    ON ee.id_tipo_energia = te.id_tipo_energia
GROUP BY te.nombre;



-- ============================================================
-- 12. SUBCONSULTA EN FROM
-- Crea una tabla temporal con generación total
-- ============================================================

SELECT *
FROM
(
    SELECT 
        te.nombre AS tipo_energia,
        SUM(ee.generacion_gwh) AS total_generacion
    FROM estadisticas_energia ee
    INNER JOIN tipo_energia te
        ON ee.id_tipo_energia = te.id_tipo_energia
    GROUP BY te.nombre
) datos
ORDER BY total_generacion DESC;



-- ============================================================
-- 13. PARTICIPACIÓN EN LA MATRIZ ENERGÉTICA
-- Porcentaje de generación respecto al total
-- ============================================================

SELECT 
    te.nombre,

    SUM(ee.generacion_gwh) AS total_generacion,

    ROUND(
        SUM(ee.generacion_gwh) /
        (SELECT SUM(generacion_gwh)
         FROM estadisticas_energia) * 100
    ,2) AS participacion_pct

FROM estadisticas_energia ee
INNER JOIN tipo_energia te
    ON ee.id_tipo_energia = te.id_tipo_energia
GROUP BY te.nombre
ORDER BY participacion_pct DESC;