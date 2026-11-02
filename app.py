import os
import pandas as pd
import streamlit as st
from openai import OpenAI

# --- CONFIGURACIÓN DE PÁGINA ---
st.set_page_config(
    page_title="Asistente Comercial - Masas Delicias del Caribe",
    page_icon="🥟",
    layout="wide",
)

# Título principal
st.title("🥟 Masas Delicias del Caribe, S.R.L.")
st.subheader("Asistente Comercial Inteligente y Cotizador Mayorista")

# --- FUNCIONES DE NEGOCIO ---
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
    if forma_pago == "Al contado (5%)":
        descuento_porcentaje = 0.05
    elif forma_pago == "Crédito aprobado (3%)":
        descuento_porcentaje = 0.03

    descuento_monto = subtotal * descuento_porcentaje
    total = subtotal - descuento_monto
    ahorro_total = (120.0 * cantidad) - total if cantidad > 0 else 0.0

    return precio_unitario, subtotal, descuento_monto, total, ahorro_total


# --- PROMPT DE SISTEMA COMERCIAL ---
SYSTEM_PROMPT = """Eres el Asistente Comercial Virtual de la empresa 'Masas Delicias del Caribe, S.R.L.'.
Respondes en español claro, cordial y profesional.

REGLAS IMPORTANTES:
1. NO inventes precios. Utiliza estrictamente la siguiente tabla de precios de referencia:
   - 1 a 49 paquetes: RD$ 120 por paquete
   - 50 a 99 paquetes: RD$ 112 por paquete
   - 100 a 249 paquetes: RD$ 105 por paquete
   - 250 a 499 paquetes: RD$ 98 por paquete
   - 500 a 999 paquetes: RD$ 92 por paquete
   - 1,000 o más paquetes: RD$ 85 por paquete
2. Descuentos por forma de pago (adicionales):
   - Al contado: 5% adicional.
   - A crédito aprobado: 3% adicional.
3. Si el usuario te pregunta sobre la aprobación de créditos, aclara amablemente que tú, como IA, no apruebas créditos ni confirmas pagos directos, y que deben comunicarse con el departamento administrativo.
4. Si te piden redactar un mensaje de cobro o recordatorio de pago atrasado, hazlo de forma sumamente cordial, respetuosa y profesional.
"""


# --- CLIENTE OPENROUTER (OPENAI COMPATIBLE) ---
def obtener_configuracion_llm():
    api_key = ""
    try:
        api_key = st.secrets.get("OPENROUTER_API_KEY", "")
    except Exception:
        pass
    if not api_key:
        api_key = os.environ.get("OPENROUTER_API_KEY", "")

    base_url = "https://openrouter.ai/api/v1"
    try:
        base_url = st.secrets.get("OPENROUTER_BASE_URL", base_url)
    except Exception:
        pass
    if os.environ.get("OPENROUTER_BASE_URL"):
        base_url = os.environ.get("OPENROUTER_BASE_URL")

    modelo = "deepseek/deepseek-v4.1-flash-1017"
    try:
        modelo = st.secrets.get("OPENROUTER_MODEL", modelo)
    except Exception:
        pass
    if os.environ.get("OPENROUTER_MODEL"):
        modelo = os.environ.get("OPENROUTER_MODEL")

    return api_key, base_url, modelo


def obtener_cliente_openrouter():
    api_key, base_url, _ = obtener_configuracion_llm()
    if not api_key or api_key == "pega_aqui_tu_api_key_de_openrouter":
        return None

    if "openai_client" not in st.session_state or st.session_state.get("_cached_api_key") != api_key:
        try:
            st.session_state["openai_client"] = OpenAI(
                api_key=api_key,
                base_url=base_url,
                default_headers={
                    "HTTP-Referer": "https://masasdelicias.local",
                    "X-Title": "Masas Delicias del Caribe Asistente",
                },
            )
            st.session_state["_cached_api_key"] = api_key
        except Exception:
            st.session_state["openai_client"] = None

    return st.session_state.get("openai_client")


def obtener_respuesta_ia(user_prompt):
    api_key, _, modelo = obtener_configuracion_llm()
    if not api_key or api_key == "pega_aqui_tu_api_key_de_openrouter":
        return (
            "⚠️ **API Key no configurada.**\n\n"
            "Por favor, abre el archivo `.streamlit/secrets.toml` y reemplaza "
            "`\"pega_aqui_tu_api_key_de_openrouter\"` por tu clave real de OpenRouter."
        )

    client = obtener_cliente_openrouter()
    if client is None:
        return "⚠️ Error al inicializar el cliente de OpenRouter. Revisa tu clave y configuración."

    try:
        with st.spinner(f"🥟 Consultando al asistente ({modelo})..."):
            completion = client.chat.completions.create(
                model=modelo,
                messages=[
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                temperature=0.3,
            )

        respuesta = completion.choices[0].message.content
        if respuesta:
            return respuesta.strip()
        return "No se recibió respuesta del modelo."

    except Exception as e:
        return f"Ocurrió un error al consultar OpenRouter ({modelo}): {e}"


# --- TABS ---
tab1, tab2, tab3 = st.tabs(["📊 Cotizador Mayorista", "🤖 Asistente Virtual con IA", "📜 Lista de Precios y Políticas"])

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
            ["Ninguno / Regular", "Al contado (5%)", "Crédito aprobado (3%)"],
        )

    with col2:
        precio_unit, sub, desc, total, ahorro = calcular_cotizacion(cantidad, forma_pago)

        st.markdown("### Resumen de la Cotización")
        st.metric(label="Total a Pagar", value=f"RD$ {total:,.2f}")
        st.write(f"**Precio por Paquete:** {precio_unit:,.2f}")
        st.write(f"**Subtotal Inicial:** {sub:,.2f}")
        st.write(f"**Descuento Aplicado:** {desc:,.2f}")
        if ahorro > 0:
            st.success(f"🎉 ¡Te Estas Ahorrando RD$ {ahorro:,.2f} comparado con el precio base regular!")

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
            """- **Al Contado:** 5% de descuento adicional.
- **Crédito Aprobado:** 3% de descuento adicional.
- *Ambos descuentos se aplican sobre el precio correspondiente a la escala de volumen.*"""
        )

    st.info(
        """**Políticas Generales:**
- El precio de la cotización final se determina según la escala alcanzada por el total del pedido.
- Los créditos son autorizados única y exclusivamente por el departamento administrativo de la empresa."""
    )

# --- ESTILO VISUAL ---
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
