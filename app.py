import os
import json
import pandas as pd
import streamlit as st
from google import genai

# Configuración de página
st.set_page_config(
    page_title="Asistente Comercial - Masas Delicias del Caribe",
    page_icon="🥟",
    layout="wide"
)

# --- ESTILO VISUAL (tema rojo elegante) ---
st.markdown(
    """
    <style>
        .stApp {
            background: linear-gradient(135deg, #180606 0%, #3d0909 35%, #5e0d0d 100%);
            color: #fff4f4;
        }

        .block-container {
            padding-top: 1.2rem;
            padding-bottom: 2rem;
        }

        div[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #2a0303 0%, #4d0909 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.08);
        }

        .stTabs [role="tablist"] {
            gap: 0.75rem;
        }

        .stTabs [role="tab"] {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px 12px 0 0;
            color: #f7dcdc;
            padding: 0.7rem 1.2rem;
        }

        .stTabs [role="tab"][aria-selected="true"] {
            background: linear-gradient(180deg, #7a1212 0%, #4a0909 100%);
            color: #ffffff;
            border-color: rgba(255, 255, 255, 0.12);
            box-shadow: 0 10px 22px rgba(0, 0, 0, 0.2);
        }

        .panel-red {
            background: rgba(45, 9, 9, 0.92);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 18px;
            padding: 1.2rem 1.3rem;
            box-shadow: 0 12px 28px rgba(0, 0, 0, 0.28);
            margin-bottom: 1rem;
        }

        .panel-red h3, .panel-red h4, .panel-red h5 {
            color: #fff1f1;
            margin-top: 0;
        }

        .assistant-title {
            color: #ffd7d7;
            letter-spacing: 0.02em;
            font-size: 1.5rem;
            font-weight: 700;
            margin-bottom: 0.25rem;
        }

        .metric-box {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.07);
            border-radius: 14px;
            padding: 0.75rem 1rem;
        }

        .table-wrapper {
            background: rgba(255, 255, 255, 0.04);
            border-radius: 14px;
            padding: 0.5rem;
            border: 1px solid rgba(255, 255, 255, 0.08);
        }

        .stAlert {
            background: rgba(255, 255, 255, 0.04);
            border: 1px solid rgba(255, 255, 255, 0.08);
            color: #fff4f4;
        }

        .stMetricValue {
            color: #fff2f2;
        }

        .stDataFrame {
            background: rgba(255, 255, 255, 0.03);
            border-radius: 12px;
        }

        div[data-testid="stTextInputRootElement"],
        div[data-testid="stTextAreaRootElement"] {
            background: rgba(255, 255, 255, 0.03);
            border: 1px solid rgba(255, 255, 255, 0.08);
            border-radius: 12px;
        }

        input, textarea, select {
            color: #fff !important;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

# Título principal del encabezado
st.title("🥟 Masas Delicias del Caribe, S.R.L.")
st.subheader("Asistente Comercial Inteligente y Cotizador Mayorista")

# Campo para API key en la barra lateral
def obtener_clave_google():
    """Obtiene la API Key priorizando entrada del usuario, luego env vars y secrets."""
    clave = st.session_state.get("google_api_key", "")
    if not clave:
        clave = os.environ.get("GOOGLE_API_KEY", "")
    if not clave:
        try:
            clave = st.secrets.get("GOOGLE_API_KEY", "")
        except Exception:
            clave = ""
    return str(clave).strip() if clave else ""


def validar_clave_google(clave):
    """Valida formato básico de la clave antes de intentar usarla."""
    if not clave:
        return False, "No hay una Google API Key disponible."
    if len(clave) < 10:
        return False, "La Google API Key parece incompleta o inválida."
    return True, ""


def construir_prompt_usuario(user_prompt):
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
    3. Si el usuario te pregunta sobre aprobación de créditos, aclara amablemente que tú, como IA, no apruebas créditos ni confirmas pagos directos, y que deben comunicarse con el departamento administrativo.
    4. Si te piden redactar un mensaje de cobro o recordatorio de pago atrasado, hazlo de forma cordial, respetuosa y profesional.
    5. Si no tienes información suficiente para responder, dilo con honestidad y sugiere cómo obtenerla.

    Consulta del usuario: {user_prompt}
    """


def obtener_respuesta_gemini(final_key, user_prompt):
    if not user_prompt or not user_prompt.strip():
        raise ValueError("Escribe una consulta antes de enviar.")

    modelos_disponibles = [
        "gemini-2.0-flash",
        "gemini-2.5-flash",
        "gemini-3.5-flash-lite",
    ]

    ultimo_error = None
    client = genai.Client(api_key=final_key)

    for modelo in modelos_disponibles:
        try:
            response = client.models.generate_content(
                model=modelo,
                contents=construir_prompt_usuario(user_prompt),
            )
            texto = getattr(response, "text", "")
            if not texto or not str(texto).strip():
                raise ValueError("La API respondió vacía. Intenta nuevamente.")
            return str(texto).strip()
        except Exception as e:
            ultimo_error = e
            mensaje = str(e).lower()
            if "404" in str(e) or "not_found" in mensaje:
                continue
            raise

    raise RuntimeError(
        f"No se pudo conectar con ningún modelo disponible de Gemini. Último error: {ultimo_error}"
    )


def mostrar_error_api(error):
    mensaje = str(error).lower()

    if "api key" in mensaje or "authentication" in mensaje or "unauthorized" in mensaje or "forbidden" in mensaje:
        return "⚠️ La Google API Key no es válida, no tiene permisos o está vencida."
    if "quota" in mensaje or "rate limit" in mensaje or "too many requests" in mensaje:
        return "⚠️ La API de Gemini está temporalmente sobrecargada o excedió su cuota. Intenta más tarde."
    if "model" in mensaje and "not found" in mensaje:
        return "⚠️ El modelo solicitado no está disponible para esta cuenta."
    if "timeout" in mensaje or "timed out" in mensaje:
        return "⚠️ La solicitud tardó demasiado tiempo. Reintenta más tarde."
    return f"⚠️ No se pudo procesar la consulta. Detalle técnico: {error}"


st.sidebar.caption("La clave se guarda solo en la sesión del navegador o en variables de entorno/secrets del servidor.")

st.sidebar.markdown("<div class='panel-red'> <h4>Acceso AI</h4> </div>", unsafe_allow_html=True)

google_api_key = st.sidebar.text_input(
    "Google API Key",
    type="password",
    key="google_api_key",
    help="Ingresa tu clave aquí o configúrala como GOOGLE_API_KEY en variables de entorno o secrets."
)

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


tab1, tab2, tab3 = st.tabs(["📊 Cotizador Mayorista", "🤖 Asistente Virtual con IA", "📜 Lista de Precios y Políticas"])

# TAB 1: COTIZADOR
with tab1:
    st.markdown('<div class="panel-red"><h3>Calculadora de Cotizaciones</h3></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        cantidad = st.number_input(
            "Cantidad de paquetes (Cada paquete contiene 12 unidades):",
            min_value=1,
            max_value=100000,
            value=100,
            step=50
        )

        forma_pago = st.selectbox(
            "Forma de pago:",
            ["Ninguno / Regular", "Al contado (3%)", "Crédito aprobado (1%)"]
        )

    with col2:
        precio_unit, sub, desc, total, ahorro = calcular_cotizacion(cantidad, forma_pago)

        st.markdown('<div class="panel-red">', unsafe_allow_html=True)
        st.markdown("### Resumen de la Cotización")
        st.metric(label="Total a Pagar", value=f"RD$ {total:,.2f}")
        st.write(f"**Precio por paquete:** {precio_unit:,.2f}")
        st.write(f"**Subtotal inicial:** {sub:,.2f}")
        st.write(f"**Descuento aplicado:** {desc:,.2f}")
        if ahorro > 0:
            st.success(f"🎉 ¡Estás ahorrando RD$ {ahorro:,.2f} comparado con el precio base regular!")
        st.caption("Nota: Los precios son ficticios y no incluyen impuestos ni transporte.")
        st.markdown('</div>', unsafe_allow_html=True)

# TAB 2: ASISTENTE VIRTUAL CON IA
with tab2:
    st.markdown(
        '<div class="panel-red"><div class="assistant-title">🤖 Asistente Virtual con IA</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """Puedes consultarle dudas de precios, pedirle sugerencias de compra, o generar recordatorios de pago.
        *Ejemplo: '¿Cuánto me costarían 500 paquetes pagando al contado?' o 'Redacta un recordatorio amable para un cliente con balance atrasado'.*"""
    )

    st.markdown('<div class="panel-red">', unsafe_allow_html=True)
    user_prompt = st.text_area("¿En qué puedo ayudarte hoy?", height=120, placeholder="Escribe tu consulta aquí...")

    if st.button("Enviar Consulta", use_container_width=True):
        clave_actual = obtener_clave_google()
        es_valida, mensaje = validar_clave_google(clave_actual)

        if not es_valida:
            st.warning(f"⚠️ {mensaje}")
            st.info("Puedes ingresar la API key en la barra lateral o configurarla como GOOGLE_API_KEY en variables de entorno o secrets.")
        else:
            with st.spinner("Procesando respuesta con Gemini..."):
                try:
                    respuesta = obtener_respuesta_gemini(clave_actual, user_prompt)
                    st.markdown("### Respuesta del Asistente:")
                    st.write(respuesta)
                except ValueError as e:
                    st.error(f"⚠️ {e}")
                except Exception as e:
                    st.error(mostrar_error_api(e))
    st.markdown('</div>', unsafe_allow_html=True)

# TAB 3: LISTA DE PRECIOS Y POLÍTICAS
with tab3:
    st.markdown('<div class="panel-red"><h3>Políticas Comerciales de Referencia</h3></div>', unsafe_allow_html=True)

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.subheader("Precios por Volumen")
        df_precios = pd.DataFrame({
            "Rango de Paquetes": ["1-49", "50-99", "100-249", "250-499", "500-999", "1,000+"],
            "Precio por Unidad (RD$)": [120.00, 112.00, 105.00, 98.00, 92.00, 85.00]
        })
        st.markdown('<div class="table-wrapper">', unsafe_allow_html=True)
        st.table(df_precios)
        st.markdown('</div>', unsafe_allow_html=True)

    with col_t2:
        st.subheader("Descuentos Adicionales")
        st.markdown(
            """- **Al Contado:** 3% de descuento adicional.
- **Crédito Aprobado:** 1% de descuento adicional.
- *Ambos descuentos se aplican sobre el precio correspondiente a la escala de volumen.*"""
        )

    st.markdown(
        """
        <div class="panel-red">
            <strong>Políticas Generales:</strong>
            <ul>
                <li>El precio de la cotización final se determina según la escala alcanzada por el total del pedido.</li>
                <li>Los créditos son autorizados única y exclusivamente por el departamento administrativo de la empresa.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
