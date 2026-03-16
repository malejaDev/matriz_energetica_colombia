## ⚡ Análisis de Datos Energéticos - Talento Tech

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![Streamlit](https://img.shields.io/badge/Streamlit-1.31.0-red.svg)](https://streamlit.io/)
[![Pandas](https://img.shields.io/badge/Pandas-2.1.4-green.svg)](https://pandas.pydata.org/)
[![Seaborn](https://img.shields.io/badge/Seaborn-0.13.1-orange.svg)](https://seaborn.pydata.org/)
[![Matplotlib](https://img.shields.io/badge/Matplotlib-latest-lightgrey.svg)](https://matplotlib.org/)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

## 📋 Descripción

Aplicación **interactiva** de análisis de la matriz energética de **Colombia**, desarrollada para el curso de **Análisis de Datos de Talento Tech**.  

Permite explorar y visualizar datos sintéticos de generación de energía renovable (**solar, eólica, hídrica y geotérmica**) para el periodo **2020–2026**, analizando generación, oferta, demanda, costos, inversiones y emisiones de CO₂.

Con esta herramienta se pueden responder preguntas como:
- ¿**Cuál es la fuente de energía más utilizada** en Colombia en los diferentes años?
- ¿Qué tipo de energía resulta **más limpia** en términos de emisiones de CO₂ por GWh generado?
- ¿Cómo se comportan los **costos de generación (USD/MWh)** entre las distintas tecnologías?
- ¿En qué fuentes se concentra la **mayor inversión** y cuál es su relación con la cobertura de la demanda?
- ¿Qué combinación de fuentes aporta una **mayor eficiencia** entre cobertura e impacto ambiental?

La app está construida con **Streamlit**, utiliza **Pandas** para el manejo de datos y **Seaborn / Matplotlib** para las visualizaciones.

## 👥 Equipo de Desarrollo

- **Claudia Arroyave**
- **Michely Muñoz**
- **Jesus Garcia**
- **Luis Alfonso Giraldo Castro**
- **Maria Alejandra Colorado Ríos**

## 🚀 Características principales

- ✅ **Landing page** informativa con descripción del proyecto y objetivos.
- ✅ Más de **30 visualizaciones interactivas** (estructura escalable).
- ✅ **Filtros dinámicos** por año, tipo de energía e inversión.
- ✅ Gráficos de líneas, barras, cajas y pastel con **Seaborn** y **Matplotlib**.
- ✅ **KPIs en tiempo real** (generación total, costo promedio, inversión, cobertura, emisiones).
- ✅ Análisis de **eficiencia, costos y emisiones**.
- ✅ Mensajes de ayuda contextual (`show_help`) en la interfaz.
- ✅ Diseño limpio y responsive dentro de Streamlit.

## 📊 Dataset

El dataset sintético `datos_energeticos_sinteticos.csv` incluye las siguientes variables:

| Variable                  | Descripción                 | Unidad          |
|---------------------------|-----------------------------|-----------------|
| `Año`                     | Período de generación       | Año             |
| `Tipo_Energia`           | Fuente energética           | Categoría       |
| `Generacion_GWh`         | Energía generada            | GWh             |
| `Oferta_GWh`             | Energía disponible          | GWh             |
| `Demanda_GWh`            | Energía requerida           | GWh             |
| `Costo_MWh`              | Costo de generación         | USD/MWh         |
| `Porcentaje_Cobertura`   | Eficiencia de cobertura     | Proporción (0–1)|
| `Inversion_USD_millones` | Capital invertido           | Millones USD    |
| `Emisiones_CO2_toneladas`| Impacto ambiental           | Toneladas       |

> 📌 Importante: El archivo CSV debe estar en la misma carpeta que `app.py` para que la función `load_data()` lo cargue correctamente.

## 🧩 Estructura del proyecto

```text
.
├── app.py                            # Aplicación principal de Streamlit
├── database/                         # Carpeta de "base de datos" (scripts SQL)
│   ├── 1_ScriptCreacionTablas.sql   # Script DDL: creación de tablas y estructura de la BD
│   ├── 2_ScriptInsert.sql           # Script con INSERTs para poblar las tablas
│   └── 3_scriptConsultas.sql        # Consultas SQL para análisis y explotación de los datos
├── README.md                         # Documentación del proyecto
├── requirements.txt (opcional)       # Dependencias del entorno
└── LICENSE                           # Licencia del proyecto
```

La carpeta `database/` centraliza la lógica de **base de datos relacional** del proyecto y contiene:

- `1_ScriptCreacionTablas.sql`: definición de tablas, tipos de datos y relaciones necesarias para modelar la matriz energética.
- `2_ScriptInsert.sql`: instrucciones `INSERT` para cargar datos de ejemplo en las tablas creadas.
- `3_scriptConsultas.sql`: conjunto de consultas SQL que permiten explotar la información (agregaciones, filtrados y análisis sobre generación, costos, emisiones, etc.).

## 🛠️ Requisitos previos

- **Python 3.10+** instalado  
- `pip` configurado  
- Conexión a internet (para cargar algunos recursos externos como imágenes y badges)

### 📦 Dependencias principales

Las dependencias del proyecto están definidas en `requirements.txt` con versiones mínimas recomendadas:

- `streamlit>=1.31.0`
- `pandas>=2.1.4`
- `seaborn>=0.13.1`
- `matplotlib>=3.8.0`
- `numpy>=1.26.0`
- `scipy>=1.11.0`
- `plotly>=5.20.0`
- `squarify>=0.4.3`

Se recomienda crear un entorno virtual y luego instalar todas las dependencias con:

```bash
pip install -r requirements.txt
```

## 🔧 Instalación

1. **Clonar el repositorio**

```bash
git clone <URL-DE-TU-REPOSITORIO>
cd matriz_energetica_colombia   # o el nombre real de tu carpeta
```

2. **(Opcional) Crear entorno virtual**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Linux / MacOS
source venv/bin/activate
```

3. **Instalar dependencias**

```bash
pip install -r requirements.txt  # si tienes este archivo
# o bien:
pip install streamlit pandas seaborn matplotlib numpy
```

4. Asegúrate de que el archivo `datos_energeticos_sinteticos.csv` esté en la misma carpeta que `app.py`.

## ▶️ Ejecución de la aplicación

Desde la carpeta raíz del proyecto, ejecuta:

```bash
streamlit run app.py
```

Luego abre en tu navegador la URL que te indique la terminal (normalmente `http://localhost:8501`).

## 🧭 Navegación dentro de la app

La aplicación tiene dos vistas principales:

- **Landing Page**
  - Presentación del proyecto.
  - Badges de tecnologías utilizadas.
  - Explicación del dataset y de las fuentes de energía.
  - Objetivos del análisis.
  - Botón **“INGRESAR AL PANEL DE ANÁLISIS”** para pasar al dashboard.

- **Dashboard principal**
  - **Barra lateral** con filtros:
    - Años (`Año`)
    - Tipos de energía (`Tipo_Energia`)
    - Rango de inversión (`Inversion_USD_millones`)
  - **KPIs**:
    - Generación total (GWh)
    - Costo promedio (USD/MWh)
    - Inversión total (Millones USD)
    - Cobertura promedio (%)
    - Emisiones totales de CO₂
  - **Conjunto de visualizaciones interactivas** (extensibles hasta 30+ gráficos especializados):
    - Evolución de generación por año y tipo de energía.
    - Inversión total por año.
    - Distribución de generación por tipo de energía (gráfico de pastel).
    - Distribución de costos (`Costo_MWh`) por tipo de energía (boxplot).
  - Botón en la barra lateral para **volver a la landing page**.

> ℹ️ Cuando se aplican filtros muy estrictos y no hay datos, la app muestra un mensaje de advertencia para que el usuario ajuste los filtros.

## 🧠 Lógica implementada (vista rápida)

- `load_data()`: carga y valida el dataset desde `datos_energeticos_sinteticos.csv`, asegurando tipos de datos correctos.
- `show_help(text)`: muestra mensajes de ayuda contextual como bloques informativos.
- `landing_page()`: construye la página de bienvenida con descripción, tecnologías, objetivos y botón de acceso al dashboard.
- `dashboard()`: gestiona filtros, KPIs y visualizaciones principales.
- Uso de `st.session_state['show_dashboard']` para navegar entre landing y dashboard sin recargar toda la app.

## 🔮 Mejoras futuras (ideas)

- Agregar más gráficos (heatmaps, scatterplots, pairplots, violinplots) para completar y superar las 30 visualizaciones.
- Incorporar **Plotly** para gráficos 100% interactivos.
- Cargar datos reales de fuentes oficiales (UPME, XM, IDEAM, etc.).
- Descarga de reportes en PDF/Excel con los gráficos y KPIs seleccionados.
- Internacionalización (ES/EN).

## 📄 Licencia

Este proyecto está licenciado bajo la licencia **MIT**.  
Puedes usar, modificar y distribuir el código respetando los términos de la licencia.
