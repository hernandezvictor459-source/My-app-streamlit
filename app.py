import os
import pandas as pd
import streamlit as st
from google import genai

try:
    from google import genai
except ImportError:
    genai = None

# Configuración de página
st.set_page_config(
    page_title="Asistente Comercial - Masas Delicias del Caribe",
    page_icon="🥟",
    layout="wide",
)


# Título principal del encabezado
st.title("🥟 Masas Delicias del Caribe, S.R.L.")
st.subheader("Asistente Comercial Inteligente y Cotizador Mayorista")


# --- LÓGICA DE NEGOCIO (PRECIOS Y COTIZADOR) ---
def obtener_precio_base(cantidad):
    if cantidad >= 1000:
        return 85.0
    elif cantidad >= 500:
        return 92.0
    elif cantidad >= 250:
        return 98.0
    elif cantidad >= 100:
        return 105.0
    elif cantidad >= 50:
        return 112.0
    elif cantidad >= 1:
        return 120.0
    return 0.0


def calcular_cotizacion(cantidad, forma_pago):
    precio_unitario = obtener_precio_base(cantidad)
    subtotal = cantidad * precio_unitario

    descuento_porcentaje = 0.0
    if forma_pago == "Al contado (3%)":
        descuento_porcentaje = 0.03
    elif forma_pago == "Crédito aprobado (1%)":
        descuento_porcentaje = 0.01

    descuento_monto = subtotal * descuento_porcentaje
    total = subtotal - descuento_monto
    ahorro_total = (120.0 * cantidad) - total if cantidad > 0 else 0.0

    return precio_unitario, subtotal, descuento_monto, total, ahorro_total


def crear_prompt(user_prompt):
    return f"""
Eres el Asistente Comercial Virtual de la empresa 'Masas Delicias del Caribe, S.R.L.'.
Respondes en español claro y profesional.

REGLAS IMPORTANTES:
1. NO inventes precios. Utiliza estrictamente la siguiente tabla de precios de referencia:
   - 1 a 49 paquetes: RD$ 120 por paquete
   - 50 a 99 paquetes: RD$ 112 por paquete
   - 100 a 249 paquetes: RD$ 105 por paquete
   - 250 a 499 paquetes: RD$ 98 por paquete
   - 500 a 999 paquetes: RD$ 92 por paquete
   - 1,000 o más paquetes: RD$ 85 por paquete
2. Descuentos por forma de pago (adicionales):
   - Al contado: 3% adicional.
   - A crédito aprobado: 1% adicional.
3. Si el usuario te pregunta sobre la aprobación de créditos, aclara amablemente que tú, como IA, no apruebas créditos ni confirmas pagos directos, y que deben comunicarse con el departamento administrativo.
4. Si te piden redactar un mensaje de cobro o recordatorio de pago atrasado, hazlo de forma sumamente cordial, respetuosa y profesional.

Consulta del usuario: {user_prompt}
"""






tab1, tab2, tab3 = st.tabs(["📊 Cotizador Mayorista", 
                            "🤖 Asistente Virtual con IA", 
                            "📜 Lista de Precios y Políticas"])

# TAB 1: COTIZADOR
with tab1:
    st.header("Calculadora de Cotizaciones")
    col1, col2 = st.columns(2)

    with col1:
        cantidad = st.number_input(
            "Cantidad de paquetes (Cada paquete contiene 12 unidades):",
            min_value=1,
            max_value=100000,
            value=100,
            step=50,
        )

        forma_pago = st.selectbox(
            "Forma de pago:",
            ["Ninguno / Regular", "Al contado (3%)", "Crédito aprobado (1%)"],
        )

    with col2:
        precio_unit, sub, desc, total, ahorro = calcular_cotizacion(cantidad, forma_pago)

        st.markdown("### Resumen de la Cotización")
        st.metric(label="Total a Pagar", value=f"RD$ {total:,.2f}")
        st.write(f"**Precio por paquete:** {precio_unit:,.2f}")
        st.write(f"**Subtotal inicial:** {sub:,.2f}")
        st.write(f"**Descuento aplicado:** {desc:,.2f}")
        if ahorro > 0:
            st.success(f"🎉 ¡Estás ahorrando RD$ {ahorro:,.2f} comparado con el precio base regular!")

        st.caption("Nota: Los precios son ficticios y no incluyen impuestos ni transporte.")

# TAB 2: ASISTENTE VIRTUAL CON IA
with tab2:
    st.header("Pregúntale al Asistente Comercial de IA")
    st.markdown(
        """Puedes consultarle dudas de precios, pedirle sugerencias de compra, o generar recordatorios de pago.
        *Ejemplo: '¿Cuánto me costarían 500 paquetes pagando al contado?' o 'Redacta un recordatorio amable para un cliente con balance atrasado'.*"""
    )

    user_prompt = st.text_area(
        "¿En qué puedo ayudarte hoy?",
        height=100,
        placeholder="Escribe tu consulta aquí...",
    )

    if st.button("Consultar IA") and user_prompt:
        respuesta = obtener_respuesta_ia(user_prompt)
        st.write(respuesta)

def obtener_respuesta_gemini(client, contexto_prompt):
    try:
        with st.spinner("🥟 Espere un momento, DeliciaBot lo asiste..."):
            response = client.models.generate_content(
                model="gemini-2.5-flash",  # Nota: asegúrate de usar un modelo válido como gemini-2.5-flash o gemini-1.5-flash
                contents=contexto_prompt
            )
        return response.text, None

    except Exception as e:
        st.error(f"Ocurrió un error al consultar Gemini: {e}")
        return None, str(e)

# TAB 3: LISTA DE PRECIOS Y POLÍTICAS
with tab3:
    st.header("Políticas Comerciales de Referencia")

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("Precios por Volumen")
        df_precios = pd.DataFrame(
            {
                "Rango de Paquetes": ["1-49", "50-99", "100-249", "250-499", "500-999", "1,000+"],
                "Precio por Unidad (RD$)": [120.00, 112.00, 105.00, 98.00, 92.00, 85.00],
            }
        )
        st.table(df_precios)

    with col_t2:
        st.subheader("Descuentos Adicionales")
        st.markdown(
            """- **Al Contado:** 3% de descuento adicional.
- **Crédito Aprobado:** 1% de descuento adicional.
- *Ambos descuentos se aplican sobre el precio correspondiente a la escala de volumen.*"""
        )

    st.info(
        """**Políticas Generales:**
- El precio de la cotización final se determina según la escala alcanzada por el total del pedido.
- Los créditos son autorizados única y exclusivamente por el departamento administrativo de la empresa."""
    )

# --- ESTILO VISUAL (tema claro con acento rojo en IA, compacto y ejecutivo) ---
st.markdown(
    """
    <style>
        .stApp {
            background: #f4f7f7;
            color: #0A8DB6;
        }

        .block-container {
            padding-top: 4rem;
            padding-bottom: 1.8rem;
        }

        div[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #eef2f2 0%, #edf0f0 100%);
            border-right: 1px solid rgba(0, 0, 0, 0.08);
        }

        .stTabs [role="tablist"] {
            gap: 0.65rem;
            margin-bottom: 0.5rem;
        }

        .stTabs [role="tab"] {
            background: rgba(0, 0, 0, 0.02);
            border: 1px solid rgba(0, 0, 0, 0.08);
            border-radius: 10px 10px 0 0;
            color: #1f2727;
            padding: 0.55rem 1rem;
            min-height: 0;
        }

        .stTabs [role="tab"][aria-selected="true"] {
            background: linear-gradient(180deg, #a51c1c 0%, #731010 100%);
            color: #ffffff;
            border-color: rgba(0, 0, 0, 0.08);
            box-shadow: 0 8px 18px rgba(100, 18, 18, 0.18);
        }

        h1 {
            margin-bottom: 0.2rem;
            font-size: 2.0rem;
            color: #1d2323;
        }

        h2 {
            font-size: 1.3rem;
            margin-top: 0.2rem;
            margin-bottom: 0.6rem;
            color: #252c2c;
        }

        h3 {
            font-size: 1.1rem;
            margin-top: 0.15rem;
            margin-bottom: 0.35rem;
            color: #1e2424;
        }

        .kpi-strip {
            display: flex;
            flex-wrap: wrap;
            gap: 0.75rem;
            margin: 0 0 0.9rem 0;
        }

        .kpi-chip {
            flex: 1 1 180px;
            min-width: 180px;
            background: linear-gradient(180deg, #ffffff 0%, #f3f6f6 100%);
            border: 1px solid rgba(0,0,0,0.07);
            border-radius: 14px;
            padding: 0.7rem 0.9rem;
            box-shadow: 0 8px 18px rgba(0,0,0,0.04);
        }

        .kpi-chip .label {
            font-size: 0.72rem;
            text-transform: uppercase;
            letter-spacing: 0.08em;
            color: #556060;
            margin-bottom: 0.15rem;
        }

        .kpi-chip .value {
            font-size: 1.2rem;
            font-weight: 700;
            color: #171d1d;
        }

        .kpi-chip .trend {
            margin-top: 0.25rem;
            font-size: 0.72rem;
            color: #8d1d1d;
        }

        .panel-light {
            background: rgba(255, 255, 255, 0.98);
            border: 1px solid rgba(0, 0, 0, 0.08);
            border-radius: 16px;
            padding: 1rem 1.05rem;
            box-shadow: 0 10px 22px rgba(0, 0, 0, 0.04);
            margin-bottom: 0.85rem;
        }

        .panel-ia {
            background: linear-gradient(180deg, rgba(255, 242, 242, 0.9) 0%, rgba(255, 255, 255, 0.98) 100%);
            border: 1px solid rgba(180, 29, 29, 0.25);
            border-radius: 16px;
            padding: 1rem 1.05rem;
            box-shadow: 0 10px 24px rgba(130, 18, 18, 0.08);
            margin-bottom: 0.85rem;
        }

        .panel-light h3, .panel-light h4, .panel-light h5,
        .panel-ia h3, .panel-ia h4, .panel-ia h5 {
            color: #1d2323;
            margin-top: 0;
        }

        .assistant-title {
            color: #8d1d1d;
            letter-spacing: 0.02em;
            font-size: 1.4rem;
            font-weight: 700;
            margin-bottom: 0.10rem;
        }

        .table-wrapper {
            background: rgba(255, 255, 255, 0.9);
            border-radius: 12px;
            padding: 0.4rem;
            border: 1px solid rgba(0, 0, 0, 0.08);
        }

        .stAlert {
            background: rgba(255, 255, 255, 0.8);
            border: 1px solid rgba(0, 0, 0, 0.08);
            color: #1d2323;
        }

        .stMetricValue {
            color: #1d2323;
        }

        .stDataFrame {
            background: #ffffff !important;
            border-radius: 12px;
            color: #1d2323 !important;
        }

        .stDataFrame div[data-testid="stDataFrame"] {
            background: #ffffff !important;
        }

        .stDataFrame table,
        .stDataFrame table thead th,
        .stDataFrame table tbody td,
        .stDataFrame .dataframe,
        .stDataFrame .dataframe thead tr th,
        .stDataFrame .dataframe tbody tr td {
            background: #ffffff !important;
            color: #1d2323 !important;
            border-color: rgba(0, 0, 0, 0.09) !important;
        }

        .stDataFrame table thead th {
            background: #f5f7f7 !important;
            color: #1d2323 !important;
            font-weight: 700;
        }

        .stDataFrame table tbody tr:nth-child(even) td {
            background: #fafbfb !important;
        }

        div[data-testid="stTextInputRootElement"],
        div[data-testid="stTextAreaRootElement"] {
            background: rgba(255, 255, 255, 0.9);
            border: 1px solid rgba(0, 0, 0, 0.08);
            border-radius: 12px;
        }

        div.stButton > button {
            background: linear-gradient(180deg, #8f1b1b 0%, #4d0b0b 100%);
            border: 1px solid #d95656;
            color: #fff;
            font-weight: 700;
            border-radius: 12px;
            box-shadow: 0 10px 22px rgba(120, 18, 18, 0.18);
            min-height: 2.5rem;
        }

        div.stButton > button:hover {
            background: linear-gradient(180deg, #a82222 0%, #621010 100%);
            border-color: #f0a0a0;
        }

        input, textarea, select {
            color: #1d2323 !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)
