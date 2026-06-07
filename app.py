import glob
import math
import os

import folium
import pandas as pd
import streamlit as st
from streamlit_folium import st_folium

# Ruta absoluta al proyecto independientemente de dónde se corra Streamlit
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# ---------------------------------------------------------------------------
# Configuración de página
# ---------------------------------------------------------------------------
st.set_page_config(
    page_title="Dashboard Inmobiliario",
    page_icon="🏠",
    layout="wide",
)

st.title("🏠 Dashboard Inmobiliario — Hermosillo")

# ---------------------------------------------------------------------------
# Estados de las casas
# ---------------------------------------------------------------------------
ESTADOS = {
    "Visitada": {"color": "green",  "emoji": "🟢", "desc": "Fui en persona"},
    "Vista":    {"color": "orange", "emoji": "🟡", "desc": "Tengo info / fotos"},
    "Por ver":  {"color": "red",    "emoji": "🔴", "desc": "Quiero ir"},
}

# ---------------------------------------------------------------------------
# Lugares de interés (POIs)
# Coordenadas marcadas con (*) son aproximadas — verificar en Google Maps
# ---------------------------------------------------------------------------
POIS = [
    {
        "nombre":  "Trabajo — Ausenco",
        "emoji":   "🏢",
        "lat":     29.09744,   # Blvd. Fco. Eusebio Kino 309, Country Club
        "lon":     -110.94039,
    },
    {
        "nombre":  "Costco",
        "emoji":   "🛒",
        "lat":     29.08308,   # Av. Luis Donaldo Colosio 416, Villa Satélite
        "lon":     -110.97992,
    },
    {
        "nombre":  "Universidad de Sonora",
        "emoji":   "🎓",
        "lat":     29.08342,   # Blvd. Luis Encinas J. y Av. Rosales, Centro
        "lon":     -110.96019,
    },
    {
        "nombre":  "Galerías Sonora",
        "emoji":   "🏬",
        "lat":     29.06619,   # Av. Cultura 55 Ote, Proyecto Río Sonora
        "lon":     -110.95122,
    },
    {
        "nombre":  "Mi casa actual",
        "emoji":   "🏠",
        "lat":     29.021846,  # Ingeniero Oscar Pinto Luján 99
        "lon":     -110.943501,
    },
    {
        "nombre":  "Casa de mi novia",
        "emoji":   "💛",
        "lat":     29.026194,  # Los Girasoles 20, Av. Ardillas
        "lon":     -110.964000,
    },
]

# ---------------------------------------------------------------------------
# Funciones de distancia y tiempo estimado
# ---------------------------------------------------------------------------
def distancia_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Distancia Haversine en kilómetros."""
    R = 6371
    phi1, phi2 = math.radians(lat1), math.radians(lat2)
    a = (
        math.sin(math.radians((lat2 - lat1) / 2)) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(math.radians((lon2 - lon1) / 2)) ** 2
    )
    return 2 * R * math.asin(math.sqrt(a))


def tiempo_min(km: float) -> int:
    """Tiempo estimado en minutos: distancia × factor tortuosidad 1.35 / 30 km/h promedio urbano."""
    return round(km * 1.35 / 30 * 60)


# ---------------------------------------------------------------------------
# Datos de propiedades
# ---------------------------------------------------------------------------
@st.cache_data
def cargar_datos() -> pd.DataFrame:
    return pd.DataFrame([
        # ── Casas reales ──────────────────────────────────────────────────
        {
            "Nombre":       "Montesinos Villena — Vicar",
            "Colonia":      "Periférico Norte",
            "Precio":       2_195_500,
            "Terreno":      123.5,
            "Construccion": 105.15,
            "Recamaras":    2,
            "Banos":        1.5,
            "Latitud":      29.138361,
            "Longitud":     -111.031417,
            "Estado":       "Por ver",
            "Notas":        "Modelo Vicar. 2 plantas, 2 recámaras, 1½ baños. "
                            "Estancia, cocina, sala-comedor, lavandería, cochera.",
            "Contacto":     "Vendedora Montesinos. Tel: (662) 430 2546",
            "Fotos":        "montesinos-villena-vicar",
        },
        {
            "Nombre":       "Montesinos Villena — Vicar Plus",
            "Colonia":      "Periférico Norte",
            "Precio":       2_398_000,
            "Terreno":      144,
            "Construccion": 106.3,
            "Recamaras":    3,
            "Banos":        2.5,
            "Latitud":      29.138461,
            "Longitud":     -111.031317,
            "Estado":       "Por ver",
            "Notas":        "Modelo Vicar Plus. 2 niveles, 3 recámaras, 2½ baños. "
                            "Walk-in closet en recámara principal. "
                            "Este mes hay bonos de promoción aún no aplicados.",
            "Contacto":     "Vendedora Montesinos. Tel: (662) 430 2546",
            "Fotos":        "montesinos-villena-vicar-plus",
        },
    ])


df = cargar_datos()

# ---------------------------------------------------------------------------
# Sidebar — filtros
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
    "Rango de Precio (MXN)",
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
st.sidebar.markdown("**Leyenda — Casas**")
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
tab_mapa, tab_stats, tab_detalle = st.tabs(["📍 Mapa", "📊 Estadísticas", "🏡 Detalle"])

# ── Mapa ─────────────────────────────────────────────────────────────────────
with tab_mapa:
    lat_c = df_f["Latitud"].mean() if not df_f.empty else 29.0892
    lon_c = df_f["Longitud"].mean() if not df_f.empty else -110.9504

    mapa = folium.Map(
        location=[lat_c, lon_c],
        zoom_start=12,
        tiles="CartoDB positron",
    )

    # Marcadores de casas
    for _, casa in df_f.iterrows():
        color = ESTADOS[casa["Estado"]]["color"]
        emoji = ESTADOS[casa["Estado"]]["emoji"]

        popup_html = f"""
        <div style="font-family:sans-serif;min-width:200px;line-height:1.7">
            <b style="font-size:15px">{casa['Nombre']}</b><br>
            <hr style="margin:4px 0">
            {emoji} <b>{casa['Estado']}</b><br>
            📍 {casa['Colonia']}<br>
            💰 <b>${casa['Precio']:,.0f}</b><br>
            🛏 {int(casa['Recamaras'])} rec.&nbsp;|&nbsp;🚿 {casa['Banos']} baños<br>
            📐 {casa['Terreno']} m² terreno · {casa['Construccion']} m² const.<br>
            <br>
            <i style="color:#555;font-size:12px">{casa['Notas']}</i>
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
            popup=folium.Popup(popup_html, max_width=260),
        ).add_to(mapa)

    # Marcadores de lugares de interés
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
        # Métricas generales
        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Precio promedio",        f"${df_f['Precio'].mean():,.0f}")
        c2.metric("Precio mínimo",          f"${df_f['Precio'].min():,.0f}")
        c3.metric("m² construcción prom.",  f"{df_f['Construccion'].mean():.1f} m²")
        c4.metric("Total propiedades",      len(df_f))

        st.divider()

        col_izq, col_der = st.columns(2)
        with col_izq:
            st.markdown("**Precio por propiedad**")
            st.bar_chart(df_f.set_index("Nombre")["Precio"])
        with col_der:
            st.markdown("**Casas por estado**")
            por_estado = (
                df_f["Estado"]
                .value_counts()
                .rename_axis("Estado")
                .reset_index(name="Cantidad")
            )
            st.bar_chart(por_estado.set_index("Estado"))


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
        emoji = ESTADOS[casa["Estado"]]["emoji"]

        st.divider()
        st.markdown(f"## {casa['Nombre']}")
        st.markdown(f"{emoji} **{casa['Estado']}** &nbsp;·&nbsp; 📍 {casa['Colonia']}")
        if casa["Contacto"]:
            st.caption(f"📞 {casa['Contacto']}")

        st.divider()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Precio",               f"${casa['Precio']:,.0f}")
        c2.metric("Terreno",              f"{casa['Terreno']} m²")
        c3.metric("Construcción",         f"{casa['Construccion']} m²")
        c4.metric("Recámaras / Baños",    f"{int(casa['Recamaras'])} / {casa['Banos']}")

        st.divider()

        st.markdown("**📝 Notas**")
        st.info(casa["Notas"])

        st.divider()

        # Distancias a lugares de referencia
        st.markdown("**🚗 Distancias a lugares de referencia**")
        st.caption("Línea recta × tortuosidad urbana 1.35 ÷ 30 km/h promedio. Tiempos estimados.")

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

        st.divider()

        # Galería de fotos
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
