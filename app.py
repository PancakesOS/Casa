import glob
import math
import os

import altair as alt
import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

st.set_page_config(
    page_title="Dashboard Inmobiliario",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 Dashboard Inmobiliario — Hermosillo")

# ---------------------------------------------------------------------------
# Estados
# ---------------------------------------------------------------------------
ESTADOS = {
    "Visitada": {"color": "green",  "emoji": "🟢", "desc": "Fui en persona"},
    "Vista":    {"color": "orange", "emoji": "🟡", "desc": "Tengo info / fotos"},
    "Por ver":  {"color": "red",    "emoji": "🔴", "desc": "Quiero ir"},
}

# ---------------------------------------------------------------------------
# POIs
# ---------------------------------------------------------------------------
POIS = [
    {"nombre": "Trabajo — Ausenco",     "emoji": "🏢", "lat": 29.09744,  "lon": -110.94039},
    {"nombre": "Costco",                "emoji": "🛒", "lat": 29.08308,  "lon": -110.97992},
    {"nombre": "Universidad de Sonora", "emoji": "🎓", "lat": 29.08342,  "lon": -110.96019},
    {"nombre": "Galerías Sonora",       "emoji": "🏬", "lat": 29.06619,  "lon": -110.95122},
    {"nombre": "Mi casa actual",        "emoji": "🏠", "lat": 29.021846, "lon": -110.943501},
    {"nombre": "Casa de mi novia",      "emoji": "💛", "lat": 29.026194, "lon": -110.964000},
]


# ---------------------------------------------------------------------------
# Financiamiento — valores fijos
# ---------------------------------------------------------------------------
CREDITO    = 2_354_888   # crédito hipotecario disponible
GASTOS_NOT = 0.06        # 6 % gastos notariales / ISAI Sonora
COSTO_AGUA = 4_000       # contrato de agua potable

# ---------------------------------------------------------------------------
# Utilidades
# ---------------------------------------------------------------------------
def distancia_km(lat1, lon1, lat2, lon2):
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    a = (
        math.sin(math.radians((lat2 - lat1) / 2)) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(math.radians((lon2 - lon1) / 2)) ** 2
    )
    return 2 * R * math.asin(math.sqrt(a))


def tiempo_min(km):
    return round(km * 1.35 / 30 * 60)


def fmt_m2(val):
    if pd.isna(val) or val == 0:
        return "N/D"
    return f"{val:.0f} m²"


def bullet_list(texto, color):
    """Renderiza texto con saltos de línea como lista de bullets de color."""
    items = [l.strip() for l in str(texto).split("\n") if l.strip()]
    if not items:
        return ""
    icon = "✅" if color == "green" else "❌"
    return "\n".join(f"{icon} {item}" for item in items)


# ---------------------------------------------------------------------------
# Datos
# ---------------------------------------------------------------------------
@st.cache_data
def cargar_datos():
    return pd.DataFrame([
        {
            "Nombre":            "Montesinos — Vicar",
            "Colonia":           "Montesinos Villena",
            "Precio":            2_122_877,
            "Precio_Nota":       "",
            "Terreno":           123.0,
            "Construccion":      105.0,
            "Recamaras":         2,
            "Banos":             1.5,
            "Fachada":           "Sur–Norte",
            "Estado":            "Visitada",
            "Estado_General":    "Detalles menores",
            "Latitud":           29.137639,
            "Longitud":          -111.032139,
            "Link":              "https://www.google.com/maps/place/29%C2%B008'15.5%22N+111%C2%B001'55.7%22W/@29.1374866,-111.0317024,217m",
            "Pros":              "Barata\nCerca del Quiroga\nPosible expansión\nBonito lugar\nCalificación 3.9",
            "Contras":           "Muy lejos\nLugar ruidoso\nCerca de un cerro\nSin baño propio en rec. principal\nNo cabe cama King\nSin espacio para tocador",
            "Recamara_Ppal":     "—",
            "Home_Office":       "Espacio en estancia/recámara",
            "Climatizacion":     "Solo preparaciones/ductos",
            "Cocina":            "Sin isla",
            "Lavado":            "Interior cerrado",
            "Patio":             "Mediano, con pasto",
            "Cochera":           "Sin techar, para 2",
            "Acceso":            "Guardia 24/7",
            "Amenidades":        "Parque, Alberca comunitaria, Cancha deportiva, Juegos infantiles",
            "Contacto":          "Vendedora Montesinos. Tel: (662) 430 2546",
            "Fotos":             "montesinos-villena-vicar",
            "Precio_Final":      0,
        },
        {
            "Nombre":            "Salamanca — Mallorca",
            "Colonia":           "Montesinos Salamanca",
            "Precio":            1_600_000,
            "Precio_Nota":       "",
            "Terreno":           85.0,
            "Construccion":      75.0,
            "Recamaras":         2,
            "Banos":             1.5,
            "Fachada":           "Sur–Norte",
            "Estado":            "Visitada",
            "Estado_General":    "Detalles menores",
            "Latitud":           29.117167,
            "Longitud":          -111.052222,
            "Link":              "https://www.google.com/maps/place/29%C2%B007'01.8%22N+111%C2%B003'08.0%22W/@29.117179,-111.0528767,259m",
            "Pros":              "Barata",
            "Contras":           "Solo 2 recámaras\nPoco patio\nLejos\nSolo 1 baño\nMuy pequeña",
            "Recamara_Ppal":     "—",
            "Home_Office":       "Improvisado en área común",
            "Climatizacion":     "Solo preparaciones/ductos",
            "Cocina":            "Sin isla",
            "Lavado":            "Exterior techado",
            "Patio":             "Apenas un pasillo",
            "Cochera":           "Sin techar, para 2",
            "Acceso":            "Guardia 24/7",
            "Amenidades":        "Parque, Alberca comunitaria, Cancha deportiva, Terraza/Salón de eventos, Juegos infantiles",
            "Contacto":          "",
            "Fotos":             "Salamanca-Mallorca",
            "Precio_Final":      0,
        },
        {
            "Nombre":            "Salamanca — Valencia",
            "Colonia":           "Montesinos Salamanca",
            "Precio":            1_995_000,
            "Precio_Nota":       "Precio base de la vivienda. Con ofertas y escrituras incluidas: $2,188,000",
            "Terreno":           126.0,
            "Construccion":      122.0,
            "Recamaras":         3,
            "Banos":             2.5,
            "Fachada":           "Norte–Sur",
            "Estado":            "Visitada",
            "Estado_General":    "Detalles menores",
            "Latitud":           29.117083,
            "Longitud":          -111.053444,
            "Link":              "https://www.google.com/maps/place/29%C2%B007'01.5%22N+111%C2%B003'12.4%22W/@29.1170431,-111.0533716,129m",
            "Pros":              "Excelente recámara principal\nEspacio social en planta baja\nBuena área de lavado\nBonita privada\nCerrada de pocas casas",
            "Contras":           "Lejos\nTráfico en Gaspar Luken",
            "Recamara_Ppal":     "Walk-in closet · Baño propio · Cabe King Size",
            "Home_Office":       "Cuarto independiente",
            "Climatizacion":     "Solo preparaciones/ductos",
            "Cocina":            "Isla/barra",
            "Lavado":            "Exterior techado",
            "Patio":             "Apenas un pasillo",
            "Cochera":           "Sin techar, para 2",
            "Acceso":            "Guardia 24/7",
            "Amenidades":        "Parque, Alberca comunitaria, Cancha deportiva, Terraza/Salón de eventos, Juegos infantiles",
            "Contacto":          "",
            "Fotos":             "salamanca-valencia",
            "Precio_Final":      2_188_000,
        },
        {
            "Nombre":            "San Francisco — 3 Recámaras",
            "Colonia":           "San Francisco Valle",
            "Precio":            2_400_000,
            "Precio_Nota":       "",
            "Terreno":           117.0,
            "Construccion":      95.0,
            "Recamaras":         3,
            "Banos":             1.5,
            "Fachada":           "Sur–Norte",
            "Estado":            "Visitada",
            "Estado_General":    "Detalles menores",
            "Latitud":           29.052472,
            "Longitud":          -111.013361,
            "Link":              "https://www.google.com/maps/place/29%C2%B003'08.9%22N+111%C2%B000'48.1%22W/@29.052481,-111.0146505,518m",
            "Pros":              "Buena ubicación\nBuen patio",
            "Contras":           "Muy cara\nOxxo más cercano a 5 min en carro",
            "Recamara_Ppal":     "Cabe King Size",
            "Home_Office":       "Cuarto independiente",
            "Climatizacion":     "Solo preparaciones/ductos",
            "Cocina":            "Sin isla",
            "Lavado":            "Interior cerrado",
            "Patio":             "Grande, con pasto",
            "Cochera":           "Sin techar, para 2",
            "Acceso":            "Guardia 24/7",
            "Amenidades":        "Parque, Alberca comunitaria, Juegos infantiles",
            "Contacto":          "",
            "Fotos":             "san-francisco-3-rec",
            "Precio_Final":      0,
        },
        {
            "Nombre":            "San Francisco — 2 Recámaras",
            "Colonia":           "San Francisco Valle",
            "Precio":            2_100_000,
            "Precio_Nota":       "Precio incluye escrituras",
            "Terreno":           117.0,
            "Construccion":      71.0,
            "Recamaras":         2,
            "Banos":             1.5,
            "Fachada":           "Este–Oeste",
            "Estado":            "Visitada",
            "Estado_General":    "Detalles menores",
            "Latitud":           29.052083,
            "Longitud":          -111.014083,
            "Link":              "https://www.google.com/maps/place/29%C2%B003'07.5%22N+111%C2%B000'50.7%22W/@29.052082,-111.0152464,518m",
            "Pros":              "Precio accesible\nPatio grande",
            "Contras":           "Muy pequeña",
            "Recamara_Ppal":     "—",
            "Home_Office":       "Improvisado en área común",
            "Climatizacion":     "Solo preparaciones/ductos",
            "Cocina":            "Sin isla",
            "Lavado":            "Exterior techado",
            "Patio":             "Grande",
            "Cochera":           "Sin techar, para 2",
            "Acceso":            "Guardia 24/7",
            "Amenidades":        "Parque, Alberca comunitaria, Juegos infantiles",
            "Contacto":          "",
            "Fotos":             "san-francisco-2-rec",
            "Precio_Final":      0,
        },
        {
            "Nombre":            "Málaga — Arezzo",
            "Colonia":           "Málaga Residencial",
            "Precio":            1_370_000,
            "Precio_Nota":       "Precio incluye escrituras",
            "Terreno":           113.9,
            "Construccion":      67.42,
            "Recamaras":         2,
            "Banos":             1.5,
            "Fachada":           "Sur–Norte",
            "Estado":            "Visitada",
            "Estado_General":    "Detalles menores",
            "Latitud":           29.165861,
            "Longitud":          -111.008417,
            "Link":              "https://www.google.com/maps/place/29%C2%B009'57.1%22N+111%C2%B000'30.3%22W/@29.165864,-111.0097135,397m",
            "Pros":              "Barata",
            "Contras":           "Está muy lejos",
            "Recamara_Ppal":     "—",
            "Home_Office":       "Improvisado en área común",
            "Climatizacion":     "Solo preparaciones/ductos",
            "Cocina":            "—",
            "Lavado":            "Intemperie",
            "Patio":             "Grande",
            "Cochera":           "Sin techar, para 1",
            "Acceso":            "Guardia 24/7",
            "Amenidades":        "Parque / áreas verdes",
            "Contacto":          "",
            "Fotos":             "Malaga - Arezzo",
            "Precio_Final":      1_370_000,
        },
        {
            "Nombre":            "Málaga — Savoy",
            "Colonia":           "Málaga Residencial",
            "Precio":            1_688_000,
            "Precio_Nota":       "Precio incluye escrituras",
            "Terreno":           113.9,
            "Construccion":      83.46,
            "Recamaras":         3,
            "Banos":             1.5,
            "Fachada":           "Sur–Norte",
            "Estado":            "Visitada",
            "Estado_General":    "Detalles menores",
            "Latitud":           29.166500,
            "Longitud":          -111.009000,
            "Link":              "https://www.google.com/maps/place/29%C2%B009'59.4%22N+111%C2%B000'32.4%22W/@29.165864,-111.0097135,397m",
            "Pros":              "Cuartos grandes\nPatio grande",
            "Contras":           "Muy lejos",
            "Recamara_Ppal":     "—",
            "Home_Office":       "Improvisado en área común",
            "Climatizacion":     "Solo preparaciones/ductos",
            "Cocina":            "—",
            "Lavado":            "Intemperie",
            "Patio":             "Grande",
            "Cochera":           "Sin techar, para 1",
            "Acceso":            "Guardia 24/7",
            "Amenidades":        "Parque / áreas verdes",
            "Contacto":          "",
            "Fotos":             "Malaga - Savoy",
            "Precio_Final":      1_688_000,
        },
        {
            "Nombre":            "Málaga — Rivoli",
            "Colonia":           "Málaga Residencial",
            "Precio":            1_885_000,
            "Precio_Nota":       "Precio incluye escrituras",
            "Terreno":           115.6,
            "Construccion":      105.6,
            "Recamaras":         3,
            "Banos":             2.5,
            "Fachada":           "Norte–Sur",
            "Estado":            "Visitada",
            "Estado_General":    "Detalles menores",
            "Latitud":           29.166750,
            "Longitud":          -111.007944,
            "Link":              "https://www.google.com/maps/place/29%C2%B010'00.3%22N+111%C2%B000'28.6%22W/@29.166501,-111.0102825,397m",
            "Pros":              "Cuartos grandes\nBaño en recámara principal",
            "Contras":           "Muy lejos",
            "Recamara_Ppal":     "—",
            "Home_Office":       "Cuarto independiente",
            "Climatizacion":     "Solo preparaciones/ductos",
            "Cocina":            "—",
            "Lavado":            "Interior cerrado",
            "Patio":             "Grande",
            "Cochera":           "Sin techar, para 1",
            "Acceso":            "Guardia 24/7",
            "Amenidades":        "Parque / áreas verdes",
            "Contacto":          "",
            "Fotos":             "Malaga - Rivoli",
            "Precio_Final":      1_885_000,
        },
    ])


df = cargar_datos()

# ---------------------------------------------------------------------------
# Sidebar
# ---------------------------------------------------------------------------
st.sidebar.header("🔎 Filtros")

estados_sel = st.sidebar.multiselect(
    "Estado",
    options=list(ESTADOS.keys()),
    default=list(ESTADOS.keys()),
    format_func=lambda e: f"{ESTADOS[e]['emoji']} {e}",
)

colonias_sel = st.sidebar.multiselect(
    "Colonia",
    options=sorted(df["Colonia"].unique()),
    default=sorted(df["Colonia"].unique()),
)

precio_min, precio_max = int(df["Precio"].min()), int(df["Precio"].max())
rango_precio = st.sidebar.slider(
    "Rango de precio (MXN)",
    min_value=precio_min,
    max_value=precio_max,
    value=(precio_min, precio_max),
    step=50_000,
    format="$%d",
)

mostrar_pois = st.sidebar.checkbox("Mostrar lugares de interés", value=True)

df_f = df[
    df["Estado"].isin(estados_sel)
    & df["Colonia"].isin(colonias_sel)
    & df["Precio"].between(rango_precio[0], rango_precio[1])
].copy()

st.sidebar.markdown(f"**{len(df_f)} propiedad(es)**")

st.sidebar.divider()
st.sidebar.markdown("**Leyenda**")
for nombre, cfg in ESTADOS.items():
    st.sidebar.markdown(f"{cfg['emoji']} **{nombre}** — {cfg['desc']}")

if mostrar_pois:
    st.sidebar.divider()
    st.sidebar.markdown("**Lugares de referencia**")
    for poi in POIS:
        st.sidebar.markdown(f"{poi['emoji']} {poi['nombre']}")

# ---------------------------------------------------------------------------
# Pestañas
# ---------------------------------------------------------------------------
tab_mapa, tab_stats, tab_detalle, tab_comp = st.tabs(
    ["📍 Mapa", "📊 Estadísticas", "🏡 Detalle", "⚖️ Comparación"]
)

# ── Mapa ─────────────────────────────────────────────────────────────────────
with tab_mapa:
    lat_c = df_f["Latitud"].mean() if not df_f.empty else 29.0892
    lon_c = df_f["Longitud"].mean() if not df_f.empty else -110.9504

    mapa = folium.Map(
        location=[lat_c, lon_c],
        zoom_start=12,
        tiles="CartoDB positron",
    )

    for _, casa in df_f.iterrows():
        color = ESTADOS[casa["Estado"]]["color"]
        emoji = ESTADOS[casa["Estado"]]["emoji"]

        pros_preview = casa["Pros"].split("\n")[0] if casa["Pros"] else ""
        contras_preview = casa["Contras"].split("\n")[0] if casa["Contras"] else ""

        popup_html = f"""
        <div style="font-family:sans-serif;min-width:210px;line-height:1.7">
            <b style="font-size:15px">{casa['Nombre']}</b><br>
            <hr style="margin:4px 0">
            {emoji} <b>{casa['Estado']}</b> &nbsp;·&nbsp; 📍 {casa['Colonia']}<br>
            💰 <b>${casa['Precio']:,.0f}</b>
            {"&nbsp;<small style='color:#888'>(incl. escrituras)</small>" if casa['Precio_Nota'] else ""}<br>
            🛏 {int(casa['Recamaras'])} rec. &nbsp;|&nbsp; 🚿 {casa['Banos']} baños<br>
            📐 {fmt_m2(casa['Terreno'])} terreno &nbsp;·&nbsp; {fmt_m2(casa['Construccion'])} const.<br>
            🧭 Fachada: {casa['Fachada']}<br>
            <hr style="margin:4px 0">
            {"✅ " + pros_preview if pros_preview else ""}
            {"<br>❌ " + contras_preview if contras_preview else ""}
        </div>
        """

        folium.CircleMarker(
            location=[casa["Latitud"], casa["Longitud"]],
            radius=13,
            color="white",
            weight=2.5,
            fill=True,
            fill_color=color,
            fill_opacity=0.88,
            tooltip=f"{emoji} {casa['Nombre']} — ${casa['Precio']:,.0f}",
            popup=folium.Popup(popup_html, max_width=280),
        ).add_to(mapa)

    if mostrar_pois:
        for poi in POIS:
            folium.Marker(
                location=[poi["lat"], poi["lon"]],
                tooltip=poi["nombre"],
                popup=folium.Popup(
                    f'<b style="font-family:sans-serif">{poi["emoji"]} {poi["nombre"]}</b>',
                    max_width=200,
                ),
                icon=folium.DivIcon(
                    html=(
                        f'<div style="font-size:26px;'
                        f'filter:drop-shadow(1px 2px 2px rgba(0,0,0,0.35));'
                        f'line-height:1">{poi["emoji"]}</div>'
                    ),
                    icon_size=(32, 32),
                    icon_anchor=(16, 16),
                ),
            ).add_to(mapa)

    st_folium(mapa, use_container_width=True, height=560)

# ── Estadísticas ─────────────────────────────────────────────────────────────
with tab_stats:
    if df_f.empty:
        st.warning("Ninguna casa coincide con los filtros.")
    else:
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Precio promedio",       f"${df_f['Precio'].mean():,.0f}")
        c2.metric("Precio mínimo",         f"${df_f['Precio'].min():,.0f}")
        mean_const = df_f["Construccion"].mean()
        c3.metric(
            "m² construcción prom.",
            f"{mean_const:.0f} m²" if not pd.isna(mean_const) else "N/D",
        )
        c4.metric("Total propiedades", len(df_f))

        st.divider()

        # Preparar datos auxiliares
        df_stats = df_f.copy()
        df_stats["Precio/m²"] = (df_stats["Precio"] / df_stats["Construccion"]).round(0)
        df_stats["km trabajo"] = df_stats.apply(
            lambda r: round(distancia_km(r["Latitud"], r["Longitud"], POIS[0]["lat"], POIS[0]["lon"]), 1),
            axis=1,
        )
        idx = df_stats.set_index("Nombre")

        # Fila 1: Precio | m² Construcción
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Precio por propiedad**")
            st.bar_chart(idx["Precio"])
        with c2:
            st.markdown("**m² de construcción**")
            st.bar_chart(idx["Construccion"])

        st.divider()

        # Fila 2: m² Terreno | Precio por m² construido
        c3, c4 = st.columns(2)
        with c3:
            st.markdown("**m² de terreno**")
            st.bar_chart(idx["Terreno"])
        with c4:
            st.markdown("**Precio por m² construido**")
            st.caption("Menor = mejor valor por espacio")
            st.bar_chart(idx["Precio/m²"])

        st.divider()

        # Distancia al trabajo
        st.markdown("**Distancia al trabajo (km)**")
        st.caption("Estimado con tortuosidad urbana × 1.35")
        st.bar_chart(idx["km trabajo"])

        st.divider()

        # Scatter: Precio vs m² Construcción
        st.markdown("**Precio vs m² de construcción**")
        st.caption("Cada punto es una propiedad — ideal: abajo a la derecha (barata y grande)")
        scatter_df = df_stats[["Nombre", "Construccion", "Precio", "Colonia"]].copy()
        scatter = (
            alt.Chart(scatter_df)
            .mark_circle(size=180, opacity=0.85)
            .encode(
                x=alt.X("Construccion:Q", title="m² de construcción"),
                y=alt.Y("Precio:Q", title="Precio (MXN)", axis=alt.Axis(format="$,.0f")),
                color=alt.Color("Colonia:N", title="Colonia"),
                tooltip=[
                    alt.Tooltip("Nombre:N",      title="Propiedad"),
                    alt.Tooltip("Colonia:N",      title="Colonia"),
                    alt.Tooltip("Construccion:Q", title="m² construcción"),
                    alt.Tooltip("Precio:Q",       title="Precio", format="$,.0f"),
                ],
            )
            .properties(width="container")
        )
        st.altair_chart(scatter, use_container_width=True)

# ── Detalle ───────────────────────────────────────────────────────────────────
with tab_detalle:
    if df_f.empty:
        st.warning("Ninguna casa coincide con los filtros.")
    else:
        nombre_sel = st.selectbox(
            "Selecciona una propiedad",
            options=df_f["Nombre"].tolist(),
        )
        casa = df_f[df_f["Nombre"] == nombre_sel].iloc[0]
        emoji_est = ESTADOS[casa["Estado"]]["emoji"]

        st.divider()

        # Encabezado
        hdr_left, hdr_right = st.columns([5, 1])
        with hdr_left:
            st.markdown(f"## {casa['Nombre']}")
            st.markdown(
                f"{emoji_est} **{casa['Estado']}** &nbsp;·&nbsp; "
                f"📍 {casa['Colonia']} &nbsp;·&nbsp; "
                f"🧭 {casa['Fachada']} &nbsp;·&nbsp; "
                f"🔧 {casa['Estado_General']}"
            )
            if casa["Precio_Nota"]:
                st.caption(f"ℹ️ {casa['Precio_Nota']}")
            if casa["Contacto"]:
                st.caption(f"📞 {casa['Contacto']}")
        with hdr_right:
            if casa["Link"]:
                st.link_button("🗺️ Ver en Maps", casa["Link"])

        st.divider()

        # Métricas principales
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Precio",            f"${casa['Precio']:,.0f}")
        c2.metric("Terreno",           fmt_m2(casa["Terreno"]))
        c3.metric("Construcción",      fmt_m2(casa["Construccion"]))
        c4.metric("Recámaras / Baños", f"{int(casa['Recamaras'])} / {casa['Banos']}")

        # Desglose de adquisición — valores fijos
        st.divider()
        st.markdown("**💰 Costo de adquisición y financiamiento**")

        if casa["Precio_Final"] > 0:
            total_adq = casa["Precio_Final"]
            st.markdown(
                f"| Concepto | Monto |\n"
                f"|:---|---:|\n"
                f"| Precio acordado (incl. escrituras y ofertas) | **${total_adq:,.0f}** |"
            )
        else:
            gastos_not = casa["Precio"] * GASTOS_NOT
            total_adq  = casa["Precio"] + gastos_not + COSTO_AGUA
            st.markdown(
                f"| Concepto | Monto |\n"
                f"|:---|---:|\n"
                f"| Precio comercial | ${casa['Precio']:,.0f} |\n"
                f"| Gastos notariales / ISAI (6%) | ${gastos_not:,.0f} |\n"
                f"| Contrato de agua | ${COSTO_AGUA:,.0f} |\n"
                f"| **Total de adquisición** | **${total_adq:,.0f}** |"
            )

        diferencia = CREDITO - total_adq
        st.write("")
        if diferencia >= 0:
            st.success(
                f"✅ Crédito disponible: **${CREDITO:,.0f}** — "
                f"Saldo a favor: **${diferencia:,.0f}**"
            )
        else:
            st.error(
                f"⚠️ Crédito disponible: **${CREDITO:,.0f}** — "
                f"Necesitas aportar: **${abs(diferencia):,.0f}** adicionales"
            )

        # Pros y Contras
        st.divider()
        col_pros, col_contras = st.columns(2)

        with col_pros:
            st.markdown("**✅ Pros**")
            for pro in [l.strip() for l in casa["Pros"].split("\n") if l.strip()]:
                st.markdown(f"- {pro}")

        with col_contras:
            st.markdown("**❌ Contras**")
            for contra in [l.strip() for l in casa["Contras"].split("\n") if l.strip()]:
                st.markdown(f"- {contra}")

        # Detalles de la visita
        st.divider()
        with st.expander("🔍 Detalles de la visita"):
            d1, d2 = st.columns(2)
            with d1:
                st.markdown("**Recámara principal**")
                st.write(casa["Recamara_Ppal"])
                st.markdown("**Home Office**")
                st.write(casa["Home_Office"])
                st.markdown("**Cocina**")
                st.write(casa["Cocina"])
                st.markdown("**Área de lavado**")
                st.write(casa["Lavado"])
            with d2:
                st.markdown("**Climatización**")
                st.write(casa["Climatizacion"])
                st.markdown("**Patio / Jardín**")
                st.write(casa["Patio"])
                st.markdown("**Cochera**")
                st.write(casa["Cochera"])
                st.markdown("**Acceso**")
                st.write(casa["Acceso"])
            st.markdown("**Amenidades**")
            st.write(casa["Amenidades"])

        # Distancias
        st.divider()
        st.markdown("**🚗 Distancias a lugares de referencia**")
        st.caption("Línea recta × tortuosidad 1.35 ÷ 30 km/h. Tiempos estimados, sin tráfico.")

        cols_poi = st.columns(len(POIS))
        for i, poi in enumerate(POIS):
            km = distancia_km(
                casa["Latitud"], casa["Longitud"],
                poi["lat"], poi["lon"],
            )
            cols_poi[i].metric(
                label=f"{poi['emoji']} {poi['nombre']}",
                value=f"{km:.1f} km",
                delta=f"~{tiempo_min(km)} min",
                delta_color="off",
            )

        # Fotos
        st.divider()
        st.markdown("**📷 Fotos**")
        carpeta = os.path.join(BASE_DIR, "fotos", casa["Fotos"])
        extensiones = ("*.jpg", "*.jpeg", "*.png", "*.webp", "*.heic", "*.HEIC", "*.JPG", "*.PNG")
        fotos = []
        for ext in extensiones:
            fotos += glob.glob(os.path.join(carpeta, ext))
        fotos = sorted(fotos)

        if fotos:
            cols = st.columns(3)
            for i, ruta in enumerate(fotos):
                cols[i % 3].image(ruta, use_container_width=True)
        else:
            st.info(
                f"📂 Carpeta lista en `fotos/{casa['Fotos']}/`\n\n"
                f"Agrega imágenes (JPG, PNG, HEIC) y recarga la página."
            )

# ── Comparación ───────────────────────────────────────────────────────────────
with tab_comp:
    if df_f.empty:
        st.warning("Ninguna casa coincide con los filtros.")
    elif len(df_f) < 2:
        st.info("Necesitas al menos 2 propiedades visibles. Ajusta los filtros.")
    else:
        st.markdown("### Comparación de propiedades")
        st.caption(f"Crédito disponible: **${CREDITO:,.0f}** · Gastos notariales: 6% · Agua: $4,000")

        filas = []
        for _, row in df_f.iterrows():
            km_trab = distancia_km(
                row["Latitud"], row["Longitud"],
                POIS[0]["lat"], POIS[0]["lon"],
            )
            if row["Precio_Final"] > 0:
                total_c = row["Precio_Final"]
            else:
                total_c = row["Precio"] + row["Precio"] * GASTOS_NOT + COSTO_AGUA
            filas.append({
                **row.to_dict(),
                "_km_trabajo": round(km_trab, 1),
                "_total": total_c,
                "_diferencia": CREDITO - total_c,
            })

        precios = [f["Precio"] for f in filas]
        kms     = [f["_km_trabajo"] for f in filas]

        for i in range(0, len(filas), 3):
            grupo = filas[i : i + 3]
            cols  = st.columns(len(grupo))

            for col, f in zip(cols, grupo):
                total_c = f["_total"]
                emoji_e = ESTADOS[f["Estado"]]["emoji"]

                badge_p  = " 🟢" if f["Precio"] == min(precios) and len(precios) > 1 else (
                           " 🔴" if f["Precio"] == max(precios) and len(precios) > 1 else "")
                badge_km = " 🟢" if f["_km_trabajo"] == min(kms) and len(kms) > 1 else (
                           " 🔴" if f["_km_trabajo"] == max(kms) and len(kms) > 1 else "")

                with col:
                    with st.container(border=True):
                        st.markdown(f"#### {f['Nombre']}")
                        st.caption(f"📍 {f['Colonia']}  ·  {emoji_e} {f['Estado']}")

                        st.divider()

                        st.markdown(f"**Precio**{badge_p}  \n${f['Precio']:,.0f}")
                        st.markdown(f"**Costo total adquisición**  \n${total_c:,.0f}")

                        st.divider()

                        l, r = st.columns(2)
                        l.markdown(f"🛏 **{int(f['Recamaras'])}** rec.")
                        r.markdown(f"🚿 **{f['Banos']}** baños")
                        l2, r2 = st.columns(2)
                        l2.markdown(f"📐 **{fmt_m2(f['Terreno'])}** terreno")
                        r2.markdown(f"🏗️ **{fmt_m2(f['Construccion'])}** const.")
                        st.markdown(f"🧭 {f['Fachada']}")

                        st.divider()

                        st.markdown(
                            f"**Al trabajo**{badge_km}  \n"
                            f"{f['_km_trabajo']:.1f} km · ~{tiempo_min(f['_km_trabajo'])} min"
                        )

                        st.divider()
                        dif = f["_diferencia"]
                        if dif >= 0:
                            st.caption(f"✅ Saldo a favor: **${dif:,.0f}**")
                        else:
                            st.caption(f"⚠️ Falta aportar: **${abs(dif):,.0f}**")

                        if f["Pros"]:
                            st.divider()
                            primer_pro = f["Pros"].split("\n")[0].strip()
                            primer_contra = f["Contras"].split("\n")[0].strip() if f["Contras"] else ""
                            if primer_pro:
                                st.caption(f"✅ {primer_pro}")
                            if primer_contra:
                                st.caption(f"❌ {primer_contra}")

            st.write("")

        st.caption("🟢 Mejor valor · 🔴 Mayor valor — en Precio y km al trabajo")
