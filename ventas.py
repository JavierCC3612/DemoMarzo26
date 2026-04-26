import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

st.set_page_config(page_title="Dashboard de Ventas", layout="wide", page_icon="📊")

st.title("📊 Dashboard de Ventas — Sucursales USA")
st.markdown("---")

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
# GRÁFICA 1 — Ventas mensuales por Región (línea de tiempo)
# ══════════════════════════════════════════════════════════════════
st.subheader("📅 Gráfica 1 — Tendencia de Ventas Mensuales por Región")
st.caption("Muestra cómo evoluciona el ingreso en el tiempo para cada región, permitiendo detectar estacionalidad y crecimiento.")

monthly = (
    dff.groupby(["Mes", "Region"])["Sales"]
    .sum()
    .reset_index()
    .sort_values("Mes")
)

fig1 = px.line(
    monthly,
    x="Mes",
    y="Sales",
    color="Region",
    markers=True,
    color_discrete_sequence=px.colors.qualitative.Bold,
    labels={"Sales": "Ventas ($)", "Mes": "Mes", "Region": "Región"},
)
fig1.update_layout(
    xaxis_tickangle=-45,
    hovermode="x unified",
    legend_title="Región",
    yaxis_tickformat="$,.0f",
    height=420,
)
st.plotly_chart(fig1, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════
# GRÁFICA 2 — Ventas vs Ganancia por Categoría y Segmento
# ══════════════════════════════════════════════════════════════════
st.subheader("🏷️ Gráfica 2 — Ventas vs. Ganancia por Categoría y Segmento")
st.caption("Compara cuánto se vende con cuánto se gana realmente: identifica qué categorías son rentables y cuáles no.")

cat_seg = (
    dff.groupby(["Category", "Segment"])[["Sales", "Profit"]]
    .sum()
    .reset_index()
)

fig2 = px.scatter(
    cat_seg,
    x="Sales",
    y="Profit",
    color="Category",
    symbol="Segment",
    size="Sales",
    text="Segment",
    color_discrete_sequence=px.colors.qualitative.Set2,
    labels={"Sales": "Ventas ($)", "Profit": "Ganancia ($)", "Category": "Categoría", "Segment": "Segmento"},
)
fig2.update_traces(textposition="top center", marker=dict(sizemode="area", sizeref=2.*cat_seg["Sales"].max()/(40.**2)))
fig2.add_hline(y=0, line_dash="dash", line_color="red", annotation_text="Punto de equilibrio", annotation_position="bottom right")
fig2.update_layout(
    xaxis_tickformat="$,.0f",
    yaxis_tickformat="$,.0f",
    height=440,
)
st.plotly_chart(fig2, use_container_width=True)

st.markdown("---")

# ══════════════════════════════════════════════════════════════════
# GRÁFICA 3 — Top 15 Estados por Ventas (barras horizontales + margen)
# ══════════════════════════════════════════════════════════════════
st.subheader("🗺️ Gráfica 3 — Top 15 Estados por Ventas y Rentabilidad")
st.caption("Rankea las sucursales/estados por volumen de ventas y superpone el margen de ganancia para ver cuáles son estratégicamente más valiosos.")

state_data = (
    dff.groupby("State")[["Sales", "Profit"]]
    .sum()
    .reset_index()
)
state_data["Margen %"] = (state_data["Profit"] / state_data["Sales"] * 100).round(1)
state_data = state_data.nlargest(15, "Sales").sort_values("Sales")

fig3 = go.Figure()
fig3.add_trace(go.Bar(
    y=state_data["State"],
    x=state_data["Sales"],
    orientation="h",
    name="Ventas",
    marker_color="#4C72B0",
    text=state_data["Sales"].apply(lambda v: f"${v:,.0f}"),
    textposition="outside",
))
fig3.add_trace(go.Scatter(
    y=state_data["State"],
    x=state_data["Margen %"],
    mode="markers+text",
    name="Margen %",
    marker=dict(color="orange", size=10, symbol="diamond"),
    text=state_data["Margen %"].apply(lambda v: f"{v:.1f}%"),
    textposition="middle right",
    xaxis="x2",
))
fig3.update_layout(
    xaxis=dict(title="Ventas ($)", tickformat="$,.0f"),
    xaxis2=dict(title="Margen de Ganancia (%)", overlaying="x", side="top", ticksuffix="%"),
    yaxis=dict(title=""),
    legend=dict(x=0.75, y=0.05),
    height=520,
    hovermode="y unified",
    margin=dict(r=120),
)
st.plotly_chart(fig3, use_container_width=True)

st.markdown("---")
st.caption("📁 Fuente: SalidaVentas.xlsx · Datos 2015–2018 · Filtros aplicables desde el panel lateral")
