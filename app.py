"""
Aplicación de Análisis de Datos Energéticos - Curso Talento Tech
Desarrollado por: Claudia Arroyave, Michely Muñoz, Jesus Garcia, Luis Alfonso, Maria Alejandra Colorado
Compatible con Python 3.10+ y librerías actualizadas
"""

import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import plotly.express as px
import warnings

# Ignorar warnings específicos de versiones nuevas
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', category=UserWarning, module='seaborn')

# Paleta de colores consistente por tipo de energía
ENERGY_COLOR_MAP = {
    "Solar": "#FDB813",        # amarillo solar
    "Eólica": "#2E86C1",       # azul viento
    "Hídrica": "#1ABC9C",      # verde agua
    "Geotérmica": "#AF7AC5",   # morado/geotermia
}

# Configuración de página
st.set_page_config(
    page_title="Análisis de Datos Energéticos | Talento Tech",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
<style>
    .main-header {font-size: 2.5rem; font-weight: bold; color: #1f77b4; text-align: center;}
    .sub-header {font-size: 1.2rem; color: #ff7f0e; text-align: center; margin-bottom: 20px;}
    .metric-card {background-color: #f0f2f6; padding: 15px; border-radius: 10px; text-align: center;}
    .stButton>button {width: 100%; background-color: #1f77b4; color: white; font-weight: bold;}
</style>
""", unsafe_allow_html=True)

# Función para cargar datos
@st.cache_data
def load_data():
    try:
        df = pd.read_csv('datos_energeticos_sinteticos.csv')
        # Asegurar tipos de datos correctos
        df['Año'] = df['Año'].astype(int)
        df['Tipo_Energia'] = df['Tipo_Energia'].astype(str)
        return df
    except Exception as e:
        st.error(f"Error cargando datos: {e}")
        return pd.DataFrame()

# Funciones de ayuda
def show_help(text: str):
    st.info(f"💡 **Ayuda:** {text}", icon="ℹ️")


def plotly_with_help(fig, help_text: str):
    st.plotly_chart(fig, use_container_width=True)
    show_help(help_text)


def compute_summary_metrics(df_f: pd.DataFrame) -> dict:
    """Calcula métricas resumen para conclusiones automáticas."""
    summary: dict[str, object] = {}

    if df_f.empty:
        return summary

    # Fuente con mayor generación total
    gen_by_type = df_f.groupby("Tipo_Energia")["Generacion_GWh"].sum().sort_values(ascending=False)
    total_gen = gen_by_type.sum()
    top_gen_energy = gen_by_type.index[0]
    top_gen_value = gen_by_type.iloc[0]
    top_gen_pct = (top_gen_value / total_gen * 100) if total_gen > 0 else 0

    # Fuente más limpia (menor CO2 por GWh)
    emis = (
        df_f.groupby("Tipo_Energia")[["Emisiones_CO2_toneladas", "Generacion_GWh"]]
        .sum()
        .reset_index()
    )
    emis = emis[emis["Generacion_GWh"] > 0].copy()
    if not emis.empty:
        emis["co2_por_gwh"] = emis["Emisiones_CO2_toneladas"] / emis["Generacion_GWh"]
        emis_sorted = emis.sort_values("co2_por_gwh")
        cleanest = emis_sorted.iloc[0]
        dirtiest = emis_sorted.iloc[-1]
        cleanest_energy = cleanest["Tipo_Energia"]
        cleanest_ratio = cleanest["co2_por_gwh"]
        dirtiest_ratio = dirtiest["co2_por_gwh"]
        improvement_pct = (
            (dirtiest_ratio - cleanest_ratio) / dirtiest_ratio * 100
            if dirtiest_ratio > 0
            else 0
        )
    else:
        cleanest_energy = None
        cleanest_ratio = None
        improvement_pct = None

    # Tecnología más económica (costo promedio)
    costs = df_f.groupby("Tipo_Energia")["Costo_MWh"].mean().sort_values()
    cheapest_energy = costs.index[0]
    cheapest_cost = costs.iloc[0]

    summary.update(
        {
            "top_gen_energy": top_gen_energy,
            "top_gen_value": top_gen_value,
            "top_gen_pct": top_gen_pct,
            "cleanest_energy": cleanest_energy,
            "cleanest_ratio": cleanest_ratio,
            "cleanest_improvement_pct": improvement_pct,
            "cheapest_energy": cheapest_energy,
            "cheapest_cost": cheapest_cost,
        }
    )
    return summary


def render_text_summary(summary: dict):
    """Renderiza conclusiones automáticas basadas en las métricas calculadas."""
    if not summary:
        return

    st.markdown("### 🧾 Resumen analítico del periodo filtrado")

    bullets = []

    # Generación
    bullets.append(
        f"- La fuente con **mayor generación** en el periodo filtrado es "
        f"**{summary['top_gen_energy']}**, con aproximadamente "
        f"**{summary['top_gen_value']:,.1f} GWh**, lo que representa cerca del "
        f"**{summary['top_gen_pct']:.1f}%** de la generación total."
    )

    # Limpieza
    if summary.get("cleanest_energy") is not None and summary.get("cleanest_ratio") is not None:
        if summary.get("cleanest_improvement_pct") is not None:
            bullets.append(
                f"- La tecnología **más limpia** es **{summary['cleanest_energy']}**, "
                f"con alrededor de **{summary['cleanest_ratio']:.2f} ton CO₂/GWh**, "
                f"lo que supone una mejora aproximada del "
                f"**{summary['cleanest_improvement_pct']:.1f}%** frente a la fuente más emisora."
            )
        else:
            bullets.append(
                f"- La tecnología **más limpia** es **{summary['cleanest_energy']}**, "
                f"con alrededor de **{summary['cleanest_ratio']:.2f} ton CO₂/GWh**."
            )

    # Costos
    bullets.append(
        f"- La fuente con **menor costo promedio** es **{summary['cheapest_energy']}**, "
        f"con un valor medio cercano a **${summary['cheapest_cost']:.2f} USD/MWh**."
    )

    st.markdown("\n".join(bullets))
    st.caption(
        "Estas conclusiones se calculan dinámicamente con base en los filtros seleccionados "
        "y representan un escenario sintético de la matriz energética de Colombia."
    )

def get_filtered_data(df: pd.DataFrame):
    """Aplica filtros comunes y devuelve el dataframe filtrado y los parámetros usados."""
    years = sorted(df['Año'].unique())
    energy_types = sorted(df['Tipo_Energia'].unique())
    min_inv, max_inv = float(df['Inversion_USD_millones'].min()), float(df['Inversion_USD_millones'].max())

    with st.sidebar.expander("⚙️ Filtros detallados", expanded=True):
        selected_years = st.multiselect("📅 Años:", options=years, default=years, key="years_filter")

        selected_energy = st.multiselect("⚡ Tipo de Energía:", options=energy_types, default=energy_types, key="energy_filter")

        selected_inv = st.slider(
            "💰 Inversión (Millones USD):",
            min_value=min_inv,
            max_value=max_inv,
            value=(min_inv, max_inv),
            key="inv_filter",
        )

    df_f = df[
        (df['Año'].isin(selected_years)) &
        (df['Tipo_Energia'].isin(selected_energy)) &
        (df['Inversion_USD_millones'] >= selected_inv[0]) &
        (df['Inversion_USD_millones'] <= selected_inv[1])
    ]

    return df_f, selected_years, selected_energy, selected_inv

# --- LANDING PAGE ---
def landing_page():
    st.markdown('<p class="main-header">⚡ ANÁLISIS DE DATOS ENERGÉTICOS</p>', unsafe_allow_html=True)
    st.markdown('<p class="sub-header">Curso Análisis de Datos - Talento Tech | 2026</p>', unsafe_allow_html=True)
    
    # Badges de tecnologías
    c1, c2, c3, c4, c5 = st.columns(5)
    with c1: st.markdown("![Python](https://img.shields.io/badge/Python-3776AB?logo=python&logoColor=white)")
    with c2: st.markdown("![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?logo=streamlit&logoColor=white)")
    with c3: st.markdown("![Pandas](https://img.shields.io/badge/Pandas-150458?logo=pandas&logoColor=white)")
    with c4: st.markdown("![Seaborn](https://img.shields.io/badge/Seaborn-3776AB?logo=python&logoColor=white)")
    with c5: st.markdown("![Plotly](https://img.shields.io/badge/Plotly-3F4F75?logo=plotly&logoColor=white)")

    st.image("https://images.unsplash.com/photo-1466611653911-95081537e5b7?w=1200&h=400&fit=crop", 
             caption="Energías Renovables: Solar, Eólica, Hídrica y Geotérmica", use_container_width=True)
    
    st.markdown("---")
    
    col1, col2 = st.columns([2, 1])
    with col1:
        st.markdown("""
        ### 📋 Sobre este Dataset
        Este panel interactivo se basa en un dataset sintético que modela la **matriz energética de Colombia** para el periodo **2020-2026**. 
        Los datos provienen de un archivo CSV (`datos_energeticos_sinteticos.csv`) que consolida información anual por tipo de energía:
        - Volúmenes de **generación, oferta y demanda** (GWh)
        - **Costos de generación** (USD/MWh)
        - **Porcentaje de cobertura** de la demanda
        - **Inversión** asociada (Millones de USD)
        - **Emisiones de CO₂** (toneladas)

        A partir de estas variables es posible responder preguntas como:
        - ¿Qué fuentes aportan mayor participación en la matriz energética colombiana?
        - ¿Cuáles son las tecnologías con **mejor relación costo–beneficio**?
        - ¿Qué energías presentan **menores emisiones por GWh generado**?
        - ¿Cómo evoluciona la **cobertura** y la demanda a lo largo del tiempo?

        **Fuentes de Energía Incluidas:**
        - ☀️ **Solar**: Fotovoltaica
        - 💨 **Eólica**: Turbinas de viento
        - 💧 **Hídrica**: Represas y flujo
        - 🌋 **Geotérmica**: Calor terrestre
        
        Utiliza los filtros laterales para explorar tendencias, comparar eficiencias, analizar el desempeño económico 
        y evaluar el impacto ambiental (CO₂) de cada fuente.
        """)
    with col2:
        st.markdown("### 🎯 Objetivos")
        st.markdown("""
        1. Visualizar tendencias temporales.
        2. Comparar costos por tipo de energía.
        3. Analizar eficiencia de inversión.
        4. Evaluar impacto de emisiones.
        """)
        st.metric("Registros Totales", len(df) if 'df' in globals() else 0)

    st.markdown("---")
    
    if st.button("🚀 INGRESAR AL PANEL DE ANÁLISIS", type="primary", use_container_width=True):
        st.session_state['show_dashboard'] = True
        st.rerun()
    st.markdown("""
    <div style='text-align: center; color: #666; font-size: 0.9em;'>
        <strong>Equipo de Desarrollo:</strong><br>
        Claudia Arroyave | Michely Muñoz | Jesus Garcia | Luis Alfonso | Maria Alejandra Colorado
    </div>
    """, unsafe_allow_html=True)

# --- DASHBOARD PRINCIPAL ---
def dashboard():
    # Selección de idioma básica
    lang = st.sidebar.selectbox("Idioma / Language", ["ES", "EN"], index=0, key="lang")

    # Modo de visualización
    view_mode = st.sidebar.radio(
        "Modo de visualización",
        options=["Básico", "Avanzado"],
        index=0,
        key="view_mode",
        help="El modo básico muestra los elementos esenciales. El modo avanzado añade análisis detallado.",
    )

    texts = {
        "ES": {
            "filters_title": "🔍 Filtros de Análisis",
            "dashboard_title": "📊 Panel de Control Energético",
            "no_data": "⚠️ No hay datos con los filtros seleccionados. Por favor ajusta los filtros.",
            "downloads_title": "📥 Descarga de datos filtrados",
            "download_label": "Descargar CSV filtrado",
            "interactive_section": "📊 Visualizaciones Interactivas (Plotly)",
            "quick_scenarios": "🎛️ Escenarios rápidos",
        },
        "EN": {
            "filters_title": "🔍 Analysis Filters",
            "dashboard_title": "📊 Energy Control Panel",
            "no_data": "⚠️ No data for the selected filters. Please adjust them.",
            "downloads_title": "📥 Download filtered data",
            "download_label": "Download filtered CSV",
            "interactive_section": "📊 Interactive Visualizations (Plotly)",
            "quick_scenarios": "🎛️ Quick scenarios",
        },
    }
    t = texts[lang]

    st.sidebar.header(t["filters_title"])
    st.sidebar.markdown("---")

    # Escenarios rápidos de filtros
    st.sidebar.subheader(t["quick_scenarios"])
    years_all = sorted(df["Año"].unique())
    energy_all = sorted(df["Tipo_Energia"].unique())
    min_inv, max_inv = float(df["Inversion_USD_millones"].min()), float(df["Inversion_USD_millones"].max())

    col_s1, col_s2 = st.sidebar.columns(2)
    with col_s1:
        if st.button("2020 vs 2026"):
            st.session_state["years_filter"] = [min(years_all), max(years_all)]
            st.session_state["energy_filter"] = energy_all
            st.session_state["inv_filter"] = (min_inv, max_inv)
            st.rerun()
    with col_s2:
        if st.button("Alta inversión"):
            st.session_state["years_filter"] = years_all
            st.session_state["energy_filter"] = energy_all
            # Top 25% de inversión
            inv_threshold = df["Inversion_USD_millones"].quantile(0.75)
            st.session_state["inv_filter"] = (float(inv_threshold), max_inv)
            st.rerun()

    if st.sidebar.button("Solo renovables más limpias"):
        # Priorizar tecnologías con menor CO2/GWh dentro del propio dataset
        tmp = (
            df.groupby("Tipo_Energia")[["Emisiones_CO2_toneladas", "Generacion_GWh"]]
            .sum()
            .reset_index()
        )
        tmp = tmp[tmp["Generacion_GWh"] > 0].copy()
        if not tmp.empty:
            tmp["co2_por_gwh"] = tmp["Emisiones_CO2_toneladas"] / tmp["Generacion_GWh"]
            clean_types = tmp.sort_values("co2_por_gwh")["Tipo_Energia"].head(2).tolist()
            st.session_state["energy_filter"] = clean_types
        st.session_state["years_filter"] = years_all
        st.session_state["inv_filter"] = (min_inv, max_inv)
        st.rerun()

    # Filtros reutilizables
    df_f, selected_years, selected_energy, selected_inv = get_filtered_data(df)

    if df_f.empty:
        st.warning(t["no_data"])
        return

    st.title(t["dashboard_title"])
    
    # KPIs
    kpi1, kpi2, kpi3, kpi4, kpi5 = st.columns(5)
    kpi1.metric("Generación Total", f"{df_f['Generacion_GWh'].sum():,.1f} GWh")
    kpi2.metric("Costo Promedio", f"${df_f['Costo_MWh'].mean():.2f}", delta="USD/MWh")
    kpi3.metric("Inversión Total", f"${df_f['Inversion_USD_millones'].sum():,.0f}M")
    kpi4.metric("Cobertura Promedio", f"{df_f['Porcentaje_Cobertura'].mean()*100:.1f}%")
    kpi5.metric("Emisiones CO2", f"{df_f['Emisiones_CO2_toneladas'].sum():,.0f} ton")
    
    # Resumen analítico automático
    summary = compute_summary_metrics(df_f)
    render_text_summary(summary)

    st.markdown("---")
    
    # Sección de Gráficos
    st.subheader("📈 Evolución Temporal")
    
    col_g1, col_g2 = st.columns(2)
    with col_g1:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.lineplot(data=df_f, x='Año', y='Generacion_GWh', hue='Tipo_Energia', marker='o', ax=ax, palette='viridis')
        ax.set_title("Tendencia de Generación por Año")
        ax.set_xlabel("Año")
        ax.set_ylabel("GWh")
        st.pyplot(fig)
        show_help("Muestra cómo ha crecido la generación de energía a lo largo de los años por tipo de fuente.")
    
    with col_g2:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(data=df_f, x='Año', y='Inversion_USD_millones', hue='Tipo_Energia', ax=ax, palette='magma', estimator='sum')
        ax.set_title("Inversión Total por Año")
        st.pyplot(fig)
        show_help("Compara el volumen de inversión anual acumulada por tipo de energía.")

    st.markdown("---")
    st.subheader("🍰 Distribución y Comparativa")
    
    c1, c2 = st.columns(2)
    with c1:
        fig, ax = plt.subplots(figsize=(8, 8))
        gen_by_type = df_f.groupby('Tipo_Energia')['Generacion_GWh'].sum()
        ax.pie(gen_by_type, labels=gen_by_type.index, autopct='%1.1f%%', colors=sns.color_palette('pastel'))
        ax.set_title("Distribución de Generación por Tipo")
        st.pyplot(fig)
        show_help("Porcentaje de contribución de cada fuente a la generación total del periodo filtrado.")
        
    with c2:
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.boxplot(data=df_f, x='Tipo_Energia', y='Costo_MWh', palette='coolwarm')
        ax.set_title("Distribución de Costos por Tipo de Energía")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45)
        st.pyplot(fig)
        show_help("Diagrama de caja que muestra la mediana, cuartiles y valores atípicos del costo por MWh.")

    st.markdown("---")
    st.subheader(t["interactive_section"])

    tab1, tab2, tab3 = st.tabs(["Tendencia (Line)", "Costos vs Emisiones (Scatter)", "Mapa de calor (Heatmap)"])

    with tab1:
        fig_line = px.line(
            df_f,
            x="Año",
            y="Generacion_GWh",
            color="Tipo_Energia",
            markers=True,
            title="Tendencia interactiva de generación por año y tipo de energía",
            color_discrete_map=ENERGY_COLOR_MAP,
        )
        plotly_with_help(
            fig_line,
            "Muestra: generación anual (GWh) por tipo de energía.\n"
            "Cómo leerlo: compara la pendiente de cada línea para ver crecimientos o caídas.\n"
            "Útil para: identificar qué tecnologías ganan o pierden relevancia en el tiempo.",
        )

    with tab2:
        fig_scatter = px.scatter(
            df_f,
            x="Costo_MWh",
            y="Emisiones_CO2_toneladas",
            color="Tipo_Energia",
            size="Generacion_GWh",
            hover_data=["Año"],
            title="Relación costo vs emisiones (tamaño = generación)",
            color_discrete_map=ENERGY_COLOR_MAP,
        )
        plotly_with_help(
            fig_scatter,
            "Muestra: relación entre costo (USD/MWh) y emisiones (ton CO₂).\n"
            "Cómo leerlo: cada punto es un registro; el tamaño indica la generación asociada.\n"
            "Útil para: entender el trade-off entre sostenibilidad y costo por tecnología.",
        )

    with tab3:
        pivot = df_f.pivot_table(
            index="Tipo_Energia",
            columns="Año",
            values="Generacion_GWh",
            aggfunc="sum",
            fill_value=0,
        )
        fig_heat = px.imshow(
            pivot,
            labels=dict(x="Año", y="Tipo de energía", color="Generación (GWh)"),
            aspect="auto",
            title="Mapa de calor de generación por año y tipo de energía",
        )
        plotly_with_help(
            fig_heat,
            "Identifica patrones de crecimiento o caída por tipo de energía. "
            "Los colores más intensos indican mayor generación (GWh) en el año seleccionado.",
        )

    # Sección de análisis avanzado alineado con consultas SQL (solo en modo avanzado)
    if view_mode == "Avanzado":
        st.markdown("---")
        st.subheader("📊 Análisis avanzado de la matriz energética")

        adv_tab1, adv_tab2, adv_tab3, adv_tab4, adv_tab5 = st.tabs(
            [
                "Totales y promedios por tipo",
                "Eficiencia energética",
                "Costos de generación",
                "Retorno de inversión",
                "Cobertura, limpieza y participación",
            ]
        )

    # 1) Totales y promedios por tipo de energía y año (4 gráficos)
    with adv_tab1:
        st.markdown("### Totales y promedios por tipo de energía y año")
        grouped = (
            df_f.groupby(["Año", "Tipo_Energia"])
            .agg(
                total_generacion_gwh=("Generacion_GWh", "sum"),
                total_oferta_gwh=("Oferta_GWh", "sum"),
                total_demanda_gwh=("Demanda_GWh", "sum"),
                promedio_costo_mwh=("Costo_MWh", "mean"),
                promedio_cobertura=("Porcentaje_Cobertura", "mean"),
                total_inversion_usd_millones=("Inversion_USD_millones", "sum"),
                total_emisiones_co2=("Emisiones_CO2_toneladas", "sum"),
            )
            .reset_index()
        )

        c1, c2 = st.columns(2)
        with c1:
            fig = px.bar(
                grouped,
                x="Año",
                y="total_generacion_gwh",
                color="Tipo_Energia",
                title="Generación total por año y tipo de energía",
            )
            plotly_with_help(
                fig,
                "Compara la generación total (GWh) anual por fuente. Útil para ver qué energía domina en cada periodo.",
            )

        with c2:
            fig = px.bar(
                grouped,
                x="Año",
                y="total_demanda_gwh",
                color="Tipo_Energia",
                title="Demanda total por año y tipo de energía",
            )
            plotly_with_help(
                fig,
                "Visualiza la demanda total (GWh) por año y fuente. Permite contrastar comportamientos de demanda por tecnología.",
            )

        c3, c4 = st.columns(2)
        with c3:
            fig = px.line(
                grouped,
                x="Año",
                y="promedio_costo_mwh",
                color="Tipo_Energia",
                markers=True,
                title="Costo promedio por MWh a lo largo del tiempo",
            )
            plotly_with_help(
                fig,
                "Observa cómo cambia el costo medio (USD/MWh) por tecnología a lo largo del tiempo. "
                "Ayuda a detectar tendencias de competitividad.",
            )

        with c4:
            fig = px.line(
                grouped,
                x="Año",
                y="promedio_cobertura",
                color="Tipo_Energia",
                markers=True,
                title="Cobertura promedio por tipo de energía",
            )
            plotly_with_help(
                fig,
                "Mide el aporte relativo de cobertura por tecnología en el tiempo. Valores mayores sugieren mejor capacidad de cubrir demanda.",
            )

        # Conclusión breve de la pestaña
        top_year = grouped.groupby("Año")["total_generacion_gwh"].sum().idxmax()
        st.markdown(
            f"**Conclusión rápida:** en el periodo filtrado, el año con mayor generación total simulada es "
            f"**{top_year}**, lo que sugiere un pico de actividad energética en dicho año bajo este escenario."
        )

    # 2) Eficiencia energética (3 gráficos)
    with adv_tab2:
        st.markdown("### Eficiencia energética (generación vs demanda)")
        eff = (
            df_f.groupby("Tipo_Energia")[["Generacion_GWh", "Demanda_GWh"]]
            .sum()
            .reset_index()
        )
        eff["eficiencia_energetica"] = eff["Generacion_GWh"] / eff["Demanda_GWh"]

        fig = px.bar(
            eff,
            x="Tipo_Energia",
            y="eficiencia_energetica",
            title="Eficiencia energética por tipo de energía",
            text="eficiencia_energetica",
        )
        plotly_with_help(
            fig,
            "Eficiencia aproximada como Generación/Demanda. Valores más altos indican mayor capacidad de respuesta frente a la demanda agregada.",
        )

        fig2 = px.scatter(
            eff,
            x="Demanda_GWh",
            y="Generacion_GWh",
            color="Tipo_Energia",
            size="Generacion_GWh",
            title="Relación generación vs demanda por tipo de energía",
        )
        plotly_with_help(
            fig2,
            "Compara generación y demanda agregadas por tecnología. "
            "Puntos alejados de la diagonal sugieren desbalances relativos entre lo demandado y lo generado.",
        )

        fig3 = px.bar(
            eff.sort_values("Generacion_GWh", ascending=False),
            x="Tipo_Energia",
            y="Generacion_GWh",
            title="Ranking de generación total por tipo de energía",
        )
        plotly_with_help(
            fig3,
            "Ranking de aporte total de generación (GWh) por fuente en el periodo filtrado.",
        )

        # Conclusión breve de la pestaña
        best_eff = eff.sort_values("eficiencia_energetica", ascending=False).iloc[0]
        st.markdown(
            f"**Conclusión rápida:** la fuente con mejor relación generación/demanda en el escenario actual es "
            f"**{best_eff['Tipo_Energia']}**, con una eficiencia aproximada de "
            f"**{best_eff['eficiencia_energetica']:.2f}**."
        )

    # 3) Análisis de costos de generación (4 gráficos)
    with adv_tab3:
        st.markdown("### Análisis de costos de generación")
        cost = (
            df_f.groupby("Tipo_Energia")["Costo_MWh"]
            .agg(["mean", "min", "max"])
            .reset_index()
            .rename(columns={"mean": "promedio", "min": "minimo", "max": "maximo"})
        )

        fig = px.bar(
            cost,
            x="Tipo_Energia",
            y="promedio",
            error_y=cost["maximo"] - cost["promedio"],
            error_y_minus=cost["promedio"] - cost["minimo"],
            title="Costo promedio por MWh con rango mínimo-máximo",
        )
        plotly_with_help(
            fig,
            "Compara el costo promedio por tecnología y su variabilidad (mín–máx). Útil para evaluar estabilidad de costos.",
        )

        fig2 = px.box(
            df_f,
            x="Tipo_Energia",
            y="Costo_MWh",
            points="all",
            title="Distribución detallada de costos por tipo de energía",
        )
        plotly_with_help(
            fig2,
            "Distribución de costos por tecnología (mediana, cuartiles y dispersión). Los puntos muestran observaciones individuales.",
        )

        fig3 = px.violin(
            df_f,
            x="Tipo_Energia",
            y="Costo_MWh",
            box=True,
            points="all",
            title="Violin plot de costos por MWh",
        )
        plotly_with_help(
            fig3,
            "Muestra la densidad de costos por tecnología. Útil para comparar formas de distribución (concentración y colas).",
        )

        fig4 = px.scatter(
            df_f,
            x="Generacion_GWh",
            y="Costo_MWh",
            color="Tipo_Energia",
            hover_data=["Año"],
            title="Costo vs generación por registro",
        )
        plotly_with_help(
            fig4,
            "Relación entre generación (GWh) y costo (USD/MWh) por registro. Ayuda a identificar economías de escala o outliers.",
        )

        # Conclusión breve de la pestaña
        cheapest = cost.sort_values("promedio").iloc[0]
        st.markdown(
            f"**Conclusión rápida:** la tecnología con **menor costo promedio** en el periodo filtrado es "
            f"**{cheapest['Tipo_Energia']}**, con un costo medio cercano a **${cheapest['promedio']:.2f} USD/MWh**."
        )

    # 4) Retorno de inversión energética (4 gráficos)
    with adv_tab4:
        st.markdown("### Retorno de inversión energética")
        inv = (
            df_f.groupby("Tipo_Energia")[["Generacion_GWh", "Demanda_GWh", "Inversion_USD_millones"]]
            .sum()
            .reset_index()
        )
        inv["generacion_por_dolar"] = inv["Generacion_GWh"] / inv["Inversion_USD_millones"]
        inv["demanda_por_dolar"] = inv["Demanda_GWh"] / inv["Inversion_USD_millones"]

        fig = px.bar(
            inv.sort_values("generacion_por_dolar", ascending=False),
            x="Tipo_Energia",
            y="generacion_por_dolar",
            title="Generación (GWh) por millón de USD invertido",
        )
        plotly_with_help(
            fig,
            "Indicador de retorno: cuánta generación se obtiene por cada millón de USD invertido. Útil para comparar eficiencia de capital.",
        )

        fig2 = px.bar(
            inv.sort_values("Inversion_USD_millones", ascending=False),
            x="Tipo_Energia",
            y="Inversion_USD_millones",
            title="Inversión total por tipo de energía",
        )
        plotly_with_help(
            fig2,
            "Muestra dónde se concentra el capital (Millones USD). Permite comparar apuesta de inversión vs resultados energéticos.",
        )

        fig3 = px.scatter(
            inv,
            x="Inversion_USD_millones",
            y="Generacion_GWh",
            color="Tipo_Energia",
            size="Generacion_GWh",
            title="Relación inversión vs generación total",
        )
        plotly_with_help(
            fig3,
            "Evalúa si mayor inversión se traduce en mayor generación total por tecnología.",
        )

        fig4 = px.scatter(
            inv,
            x="Inversion_USD_millones",
            y="Demanda_GWh",
            color="Tipo_Energia",
            size="Demanda_GWh",
            title="Relación inversión vs demanda total",
        )
        plotly_with_help(
            fig4,
            "Relaciona inversión con demanda agregada atendida. Ayuda a entender si el capital se dirige a fuentes con mayor demanda.",
        )

        # Conclusión breve de la pestaña
        best_roi = inv.sort_values("generacion_por_dolar", ascending=False).iloc[0]
        st.markdown(
            f"**Conclusión rápida:** según el indicador de **generación por millón de USD**, la fuente con mejor retorno "
            f"de inversión simulada es **{best_roi['Tipo_Energia']}**, con aproximadamente "
            f"**{best_roi['generacion_por_dolar']:.2f} GWh/MUSD**."
        )

    # 5) Cobertura, limpieza y participación (5 gráficos)
    with adv_tab5:
        st.markdown("### Cobertura, limpieza y participación en la matriz")

        cov = (
            df_f.groupby(["Año", "Tipo_Energia"])["Porcentaje_Cobertura"]
            .mean()
            .reset_index()
        )
        cov["Cobertura_pct"] = cov["Porcentaje_Cobertura"] * 100

        fig = px.bar(
            cov,
            x="Año",
            y="Cobertura_pct",
            color="Tipo_Energia",
            title="Cobertura promedio (%) por año y tipo de energía",
        )
        plotly_with_help(
            fig,
            "Comparación de cobertura promedio (%). Útil para identificar tecnologías con mejor desempeño en cobertura por año.",
        )

        emis = (
            df_f.groupby("Tipo_Energia")[["Emisiones_CO2_toneladas", "Generacion_GWh"]]
            .sum()
            .reset_index()
        )
        emis["co2_por_gwh"] = emis["Emisiones_CO2_toneladas"] / emis["Generacion_GWh"]

        fig2 = px.bar(
            emis.sort_values("co2_por_gwh"),
            x="Tipo_Energia",
            y="co2_por_gwh",
            title="Ranking de energías más limpias (ton CO₂ / GWh)",
        )
        plotly_with_help(
            fig2,
            "Ranking de limpieza: emisiones relativas por energía generada (ton CO₂/GWh). Menor es mejor.",
        )

        total_gen = emis["Generacion_GWh"].sum()
        emis["participacion_pct"] = emis["Generacion_GWh"] / total_gen * 100

        fig3 = px.pie(
            emis,
            names="Tipo_Energia",
            values="participacion_pct",
            title="Participación en la matriz energética (%)",
        )
        plotly_with_help(
            fig3,
            "Distribución del aporte de cada fuente a la generación total del periodo filtrado (participación %).",
        )

        fig4 = px.scatter(
            emis,
            x="co2_por_gwh",
            y="participacion_pct",
            color="Tipo_Energia",
            size="Generacion_GWh",
            title="Limpieza vs participación en la matriz",
        )
        plotly_with_help(
            fig4,
            "Cruza sostenibilidad (CO₂/GWh) vs relevancia (participación %). "
            "Permite identificar fuentes limpias con alto impacto en la matriz.",
        )

        cov_level = cov.copy()
        cov_level["nivel_cobertura"] = pd.cut(
            cov_level["Porcentaje_Cobertura"],
            bins=[0, 0.5, 0.8, 1.0],
            labels=["BAJA", "MEDIA", "ALTA"],
            include_lowest=True,
        )

        fig5 = px.histogram(
            cov_level,
            x="Año",
            color="nivel_cobertura",
            barmode="group",
            title="Distribución de niveles de cobertura por año",
        )
        plotly_with_help(
            fig5,
            "Clasifica la cobertura en BAJA/MEDIA/ALTA y muestra su distribución anual. Útil para evaluar consistencia de cobertura.",
        )

        # Conclusión breve de la pestaña
        avg_cov = cov.groupby("Tipo_Energia")["Cobertura_pct"].mean().sort_values(ascending=False)
        top_cov_energy = avg_cov.index[0]
        top_cov_value = avg_cov.iloc[0]
        cleanest_row = emis.sort_values("co2_por_gwh").iloc[0]
        st.markdown(
            f"**Conclusión rápida:** en términos de cobertura promedio, **{top_cov_energy}** lidera con alrededor de "
            f"**{top_cov_value:.1f}%**, mientras que la fuente más limpia del escenario es "
            f"**{cleanest_row['Tipo_Energia']}** con aproximadamente **{cleanest_row['co2_por_gwh']:.2f} ton CO₂/GWh**."
        )

    st.markdown("---")
    st.subheader(t["downloads_title"])

    csv = df_f.to_csv(index=False).encode("utf-8")
    st.download_button(
        label=t["download_label"],
        data=csv,
        file_name="datos_filtrados_matriz_energetica_colombia.csv",
        mime="text/csv",
        use_container_width=True,
    )

    st.markdown("---")
    st.caption("Desarrollado por: Claudia Arroyave, Michely Muñoz, Jesus Garcia, Luis Alfonso, Maria Alejandra Colorado")

# Main Execution
if __name__ == "__main__":
    df = load_data()
    
    if 'show_dashboard' not in st.session_state:
        st.session_state['show_dashboard'] = False
    
    if not st.session_state['show_dashboard']:
        landing_page()
    else:
        if st.sidebar.button("🏠 Volver al Inicio"):
            st.session_state['show_dashboard'] = False
            st.rerun()
        else:
            dashboard()
