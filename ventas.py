import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard de Ventas", layout="wide", page_icon="📊")

st.title("📊 Dashboard de Ventas — Sucursales USA")
st.markdown("---")

# Diccionario: nombre completo del estado → abreviatura de 2 letras (requerido por Plotly para el mapa)
ESTADO_A_CODIGO = {
    "Alabama": "AL", "Alaska": "AK", "Arizona": "AZ", "Arkansas": "AR",
    "California": "CA", "Colorado": "CO", "Connecticut": "CT", "Delaware": "DE",
    "District of Columbia": "DC", "Florida": "FL", "Georgia": "GA", "Hawaii": "HI",
    "Idaho": "ID", "Illinois": "IL", "Indiana": "IN", "Iowa": "IA",
    "Kansas": "KS", "Kentucky": "KY", "Louisiana": "LA", "Maine": "ME",
    "Maryland": "MD", "Massachusetts": "MA", "Michigan": "MI", "Minnesota": "MN",
    "Mississippi": "MS", "Missouri": "MO", "Montana": "MT", "Nebraska": "NE",
    "Nevada": "NV", "New Hampshire": "NH", "New Jersey": "NJ", "New Mexico": "NM",
    "New York": "NY", "North Carolina": "NC", "North Dakota": "ND", "Ohio": "OH",
    "Oklahoma": "OK", "Oregon": "OR", "Pennsylvania": "PA", "Rhode Island": "RI",
    "South Carolina": "SC", "South Dakota": "SD", "Tennessee": "TN", "Texas": "TX",
    "Utah": "UT", "Vermont": "VT", "Virginia": "VA", "Washington": "WA",
    "West Virginia": "WV", "Wisconsin": "WI", "Wyoming": "WY"
}

@st.cache_data
def load_data():
    df = pd.read_excel("datos/SalidaVentas.xlsx")
    df["Order Date"] = pd.to_datetime(df["Order Date"])
    df["Año"] = df["Order Date"].dt.year
    df["Mes"] = df["Order Date"].dt.to_period("M").astype(str)
    return df

df = load_data()

# ── Filtros en sidebar ──────────────────────────────────────────────
st.sidebar.header("🔎 Filtros")
regiones = st.sidebar.multiselect(
    "Región", options=sorted(df["Region"].unique()), default=sorted(df["Region"].unique())
)
años = st.sidebar.multiselect(
    "Año", options=sorted(df["Año"].unique()), default=sorted(df["Año"].unique())
)
categorias = st.sidebar.multiselect(
    "Categoría", options=sorted(df["Category"].unique()), default=sorted(df["Category"].unique())
)

mask = (
    df["Region"].isin(regiones) &
    df["Año"].isin(años) &
    df["Category"].isin(categorias)
)
dff = df[mask]

# ── KPIs ────────────────────────────────────────────────────────────
total_ventas = dff["Sales"].sum()
total_profit = dff["Profit"].sum()
total_ordenes = dff["Order ID-1"].nunique()
margen = (total_profit / total_ventas * 100) if total_ventas > 0 else 0

k1, k2, k3, k4 = st.columns(4)
k1.metric("💰 Ventas Totales", f"${total_ventas:,.0f}")
k2.metric("📈 Ganancia Total", f"${total_profit:,.0f}")
k3.metric("🛒 Órdenes Únicas", f"{total_ordenes:,}")
k4.metric("🎯 Margen Neto", f"{margen:.1f}%")

st.markdown("---")

# ══════════════════════════════════════════════════════════════════
# MAPA — Ventas por estado
# ══════════════════════════════════════════════════════════════════
st.subheader("🗺️ ¿En qué estados se vende más?")
st.caption("Más oscuro el color = más ventas tuvo ese estado. Pasa el cursor sobre un estado para ver el detalle.")

ventas_estado = (
    dff.groupby("State")["Sales"]
    .sum()
    .reset_index()
)
ventas_estado["Codigo"] = ventas_estado["State"].map(ESTADO_A_CODIGO)
ventas_estado["Ventas (miles $)"] = (ventas_estado["Sales"] / 1000).round(1)

fig_mapa = px.choropleth(
    ventas_estado,
    locations="Codigo",
    locationmode="USA-states",
    color="Ventas (miles $)",
    scope="usa",
    color_continuous_scale="Blues",
    hover_name="State",
    hover_data={"Ventas (miles $)": True, "Codigo": False},
    labels={"Ventas (miles $)": "Ventas (miles $)"},
)
fig_mapa.update_layout(
    geo=dict(bgcolor="rgba(0,0,0,0)"),
    coloraxis_colorbar=dict(title="Ventas<br>(miles $)", tickprefix="$", ticksuffix="k"),
    height=500,
    margin=dict(l=0, r=0, t=0, b=0),
)
st.plotly_chart(fig_mapa, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════
# GRÁFICA 1 — ¿Cuánto vendió cada región por año?
# ══════════════════════════════════════════════════════════════════
st.subheader("🌎 ¿Cuánto vendió cada región cada año?")
st.caption("Barras agrupadas por año — más alta la barra, más ventas tuvo esa región ese año.")

ventas_region_año = (
    dff.groupby(["Año", "Region"])["Sales"]
    .sum()
    .reset_index()
)
ventas_region_año["Ventas (miles $)"] = (ventas_region_año["Sales"] / 1000).round(1)
ventas_region_año["Etiqueta"] = ventas_region_año["Ventas (miles $)"].apply(lambda v: f"${v:.0f}k")

fig1 = px.bar(
    ventas_region_año,
    x="Año",
    y="Ventas (miles $)",
    color="Region",
    barmode="group",
    text="Etiqueta",
    color_discrete_sequence=px.colors.qualitative.Bold,
    labels={"Region": "Región", "Año": "Año"},
)
fig1.update_traces(textposition="outside")
fig1.update_layout(
    yaxis_title="Ventas (miles de dólares)",
    xaxis_title="",
    xaxis=dict(tickmode="array", tickvals=ventas_region_año["Año"].unique()),
    legend_title="Región",
    height=420,
    yaxis=dict(showgrid=True, gridcolor="#eeeeee"),
    plot_bgcolor="white",
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════
# GRÁFICA 2 — ¿Qué categoría deja más ganancia?
# ══════════════════════════════════════════════════════════════════
st.subheader("🏷️ ¿Qué categoría de producto deja más ganancia?")
st.caption("Cada barra muestra la ganancia total. En verde = ganancia positiva.")

ganancia_cat = (
    dff.groupby("Category")["Profit"]
    .sum()
    .reset_index()
    .sort_values("Profit", ascending=False)
)
ganancia_cat["Ganancia (miles $)"] = (ganancia_cat["Profit"] / 1000).round(1)
ganancia_cat["Etiqueta"] = ganancia_cat["Ganancia (miles $)"].apply(lambda v: f"${v:.1f}k")
ganancia_cat["Color"] = ganancia_cat["Profit"].apply(lambda v: "Ganancia" if v >= 0 else "Pérdida")

fig2 = px.bar(
    ganancia_cat,
    x="Category",
    y="Ganancia (miles $)",
    text="Etiqueta",
    color="Color",
    color_discrete_map={"Ganancia": "#2ecc71", "Pérdida": "#e74c3c"},
    labels={"Category": "Categoría", "Ganancia (miles $)": "Ganancia (miles $)"},
)
fig2.update_traces(textposition="outside", width=0.4)
fig2.update_layout(
    xaxis_title="",
    yaxis_title="Ganancia (miles de dólares)",
    showlegend=False,
    height=400,
    plot_bgcolor="white",
    yaxis=dict(showgrid=True, gridcolor="#eeeeee"),
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════
# GRÁFICA 3 — ¿Cuáles son los 10 estados que más venden?
# ══════════════════════════════════════════════════════════════════
st.subheader("📊 ¿Cuáles son los 10 estados que más venden?")
st.caption("Ranking horizontal — el estado más largo es el que más vendió.")

top_estados = (
    dff.groupby("State")["Sales"]
    .sum()
    .reset_index()
    .nlargest(10, "Sales")
    .sort_values("Sales")
)
top_estados["Ventas (miles $)"] = (top_estados["Sales"] / 1000).round(1)
top_estados["Etiqueta"] = top_estados["Ventas (miles $)"].apply(lambda v: f"${v:.0f}k")

fig3 = px.bar(
    top_estados,
    x="Ventas (miles $)",
    y="State",
    orientation="h",
    text="Etiqueta",
    color="Ventas (miles $)",
    color_continuous_scale="Blues",
    labels={"State": "Estado", "Ventas (miles $)": "Ventas (miles $)"},
)
fig3.update_traces(textposition="outside")
fig3.update_layout(
    xaxis_title="Ventas (miles de dólares)",
    yaxis_title="",
    coloraxis_showscale=False,
    height=430,
    plot_bgcolor="white",
    xaxis=dict(showgrid=True, gridcolor="#eeeeee"),
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════
# DATAFRAME INTERACTIVO
# ══════════════════════════════════════════════════════════════════
st.subheader("🔍 Explorar datos en detalle")
st.caption("Usa los filtros de abajo para buscar registros específicos. Los filtros del panel lateral también aplican aquí.")

# Filtros extra solo para la tabla
col1, col2, col3 = st.columns(3)

with col1:
    estados_tabla = st.multiselect(
        "Filtrar por Estado",
        options=sorted(dff["State"].unique()),
        default=[],
        placeholder="Todos los estados..."
    )
with col2:
    segmentos_tabla = st.multiselect(
        "Filtrar por Segmento",
        options=sorted(dff["Segment"].unique()),
        default=[],
        placeholder="Todos los segmentos..."
    )
with col3:
    busqueda = st.text_input("🔎 Buscar por nombre de cliente o producto", placeholder="Escribe aquí...")

# Aplicar filtros de la tabla
df_tabla = dff.copy()

if estados_tabla:
    df_tabla = df_tabla[df_tabla["State"].isin(estados_tabla)]
if segmentos_tabla:
    df_tabla = df_tabla[df_tabla["Segment"].isin(segmentos_tabla)]
if busqueda:
    df_tabla = df_tabla[
        df_tabla["Customer Name"].str.contains(busqueda, case=False, na=False) |
        df_tabla["Product Name"].str.contains(busqueda, case=False, na=False)
    ]

# Columnas relevantes para mostrar
columnas_mostrar = ["Order Date", "Customer Name", "State", "Region", "Segment",
                    "Category", "Sub-Category", "Product Name", "Sales", "Quantity", "Profit", "Ship Mode"]

st.markdown(f"**{len(df_tabla):,} registros encontrados**")
st.dataframe(
    df_tabla[columnas_mostrar].reset_index(drop=True),
    use_container_width=True,
    height=400,
    column_config={
        "Order Date": st.column_config.DateColumn("Fecha de Orden", format="DD/MM/YYYY"),
        "Sales": st.column_config.NumberColumn("Ventas ($)", format="$%.2f"),
        "Profit": st.column_config.NumberColumn("Ganancia ($)", format="$%.2f"),
        "Quantity": st.column_config.NumberColumn("Cantidad"),
        "Customer Name": "Cliente",
        "Product Name": "Producto",
        "Ship Mode": "Envío",
        "Sub-Category": "Sub-Categoría",
    }
)

st.markdown("---")
st.caption("📁 Fuente: SalidaVentas.xlsx · Datos 2015–2018 · Usa los filtros del panel izquierdo para explorar")
