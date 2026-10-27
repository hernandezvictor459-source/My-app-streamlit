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

# --- ESTILO VISUAL (tema claro con acento rojo en IA, compacto y ejecutivo) ---
st.markdown(
    """
    <style>
        .stApp {
            background: #f4f7f7;
            color: #1d2323;
        }

        .block-container {
            padding-top: 0.8rem;
            padding-bottom: 2rem;
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

# Título principal del encabezado
st.title("🥟 Masas Delicias del Caribe, S.R.L.")
st.subheader("Asistente Comercial Inteligente y Cotizador Mayorista")

# Panel ejecutivo compactado con KPI chips
st.markdown(
    """
    <div class="kpi-strip">
        <div class="kpi-chip">
            <div class="label">Volumen</div>
            <div class="value">1,240</div>
            <div class="trend">+12.4% vs. mes anterior</div>
        </div>
        <div class="kpi-chip">
            <div class="label">Descuento promedio</div>
            <div class="value">2.8%</div>
            <div class="trend">Ajuste por forma de pago</div>
        </div>
        <div class="kpi-chip">
            <div class="label">Pedidos activos</div>
            <div class="value">18</div>
            <div class="trend">6 por aprobación</div>
        </div>
        <div class="kpi-chip">
            <div class="label">Ahorro estimado</div>
            <div class="value">RD$ 45,200</div>
            <div class="trend">Respaldo por volumen</div>
        </div>
    </div>
    """,
    unsafe_allow_html=True,
)

# Campo para API key en la barra lateral
def obtener_clave_google():
    """Obtiene la API Key priorizando entrada del usuario, luego env vars y secrets."""
    clave = st.session_state.get("google_api_key", "google_api_key")
    if not clave:
        clave = os.environ.get("GOOGLE_API_KEY", ("GOOGLE_API_KEY")
    if not clave:
        try:
            clave = st.secrets.get("GOOGLE_API_KEY"), ("")
        except Exception:
            clave = ""
    return str(clave).strip() if clave else ""



def validar_clave_google(clave):
    """Valida formato básico de la clave antes de intentar usarla."""
    if not clave:
        return False, "No hay una Google API Key disponible."
    if len(clave) < 10:
        return False, "La gemini API Key parece incompleta o inválida."
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
    3. Si el usuario te pregunta sobre aprobación de créditos, aclara amablemente que tú, como IA, no apruebas créditos ni confirmas pagos directos, y que deben comunicarse con el departamento administrativo de la empresa.
    4. Si te piden redactar un mensaje de cobro o recordatorio de pago atrasado, hazlo de forma cordial, respetuosa y profesional.
    5. Si no tienes información suficiente para responder, dilo con honestidad y sugiere cómo obtenerla.

    Consulta del usuario: {user_prompt}
    """


def generar_respuesta_local(user_prompt):
    """Respuesta alternativa cuando no hay API key configurada."""
    texto = (user_prompt or "").strip()
    if not texto:
        return "Escribe una consulta para comenzar."

    texto_lower = texto.lower()

    if "500" in texto_lower and "contado" in texto_lower:
        return (
            "Con 500 paquetes, el precio base aplica la escala de 500 a 999 paquetes: RD$ 92 por paquete. "
            "Si paga al contado, hay un descuento adicional del 3%. "
            "El cálculo estimado sería: 500 × 92 = RD$ 46,000 antes del descuento; con 3% adicional, el total final aproximado es RD$ 44,620."
        )

    if "precio" in texto_lower or "cuánto" in texto_lower or "costo" in texto_lower:
        if any(num in texto_lower for num in ["1", "2", "3", "4", "5", "6", "7", "8", "9", "0"]):
            return (
                "La política comercial es por rangos de volumen: 1-49 paquetes a RD$ 120, 50-99 a RD$ 112, "
                "100-249 a RD$ 105, 250-499 a RD$ 98, 500-999 a RD$ 92 y 1,000+ a RD$ 85. "
                "Además, al contado aplica 3% y crédito aprobado 1% adicional."
            )

    if "recordatorio" in texto_lower or "cobro" in texto_lower or "pago atrasado" in texto_lower:
        return (
            "Estimado cliente, le recordamos que su saldo pendiente requiere atención. "
            "Agradecemos su pronta gestión para regularizar la cuota correspondiente. "
            "Si desea, podemos ayudarle a preparar un mensaje más formal o más amable según su caso."
        )

    if "crédito" in texto_lower or "aprob" in texto_lower:
        return (
            "Para aprobación de crédito, la política indica que esta decisión la realiza exclusivamente el departamento administrativo. "
            "Como asistente virtual, no puedo aprobar ni confirmar pagos directos; por favor, comuníquese con la oficina administrativa para gestionar la solicitud."
        )

    if "descuento" in texto_lower:
        return (
            "Los descuentos adicionales son: 3% al contado y 1% en crédito aprobado. Ambos se aplican sobre el precio según el rango de volumen del pedido."
        )

    return (
        "Sin clave de Google configurada, esta sesión está funcionando en modo local con la información comercial de la empresa. "
        "La política vigente indica: 1-49 = RD$ 120, 50-99 = RD$ 112, 100-249 = RD$ 105, 250-499 = RD$ 98, 500-999 = RD$ 92 y 1,000+ = RD$ 85. "
        "También aplica 3% al contado y 1% en crédito aprobado."
    )


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
    st.markdown('<div class="panel-light"><h3>Calculadora de Cotizaciones</h3></div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)

    with col1:
        cantidad = st.number_input(
            "Cantidad de paquetes (Cada paquete contiene 12 unidades):",
            min_value=1,
            max_value=100000,
            value=100,
            step=50,
            help="Cada paquete equivale a 12 unidades."
        )

        forma_pago = st.selectbox(
            "Forma de pago:",
            ["Ninguno / Regular", "Al contado (3%)", "Crédito aprobado (1%)"]
        )

    with col2:
        precio_unit, sub, desc, total, ahorro = calcular_cotizacion(cantidad, forma_pago)

        st.markdown('<div class="panel-light">', unsafe_allow_html=True)
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
        '<div class="panel-ia"><div class="assistant-title">🤖 Asistente Virtual con IA</div></div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        """Puedes consultarle dudas de precios, pedirle sugerencias de compra, o generar recordatorios de pago.
        *Ejemplo: '¿Cuánto me costarían 500 paquetes pagando al contado?' o 'Redacta un recordatorio amable para un cliente con balance atrasado'.*"""
    )

    st.markdown('<div class="panel-ia">', unsafe_allow_html=True)
    user_prompt = st.text_area("¿En qué puedo ayudarte hoy?", height=120, placeholder="Escribe tu consulta aquí...")

    if st.button("Enviar Consulta", use_container_width=True):
        clave_actual = obtener_clave_google()
        es_valida, mensaje = validar_clave_google(clave_actual)

        if not clave_actual:
            with st.spinner("Generando respuesta con información comercial local..."):
                respuesta = generar_respuesta_local(user_prompt)
                st.markdown("### Respuesta del Asistente:")
                st.write(respuesta)
                st.caption("Modo local activado: no se usa Google API Key.")
        else:
            if not es_valida:
                st.warning(f"⚠️ {mensaje}")
                st.info("Se usará la respuesta local porque la clave no es válida o no existe.")
                with st.spinner("Generando respuesta con información comercial local..."):
                    respuesta = generar_respuesta_local(user_prompt)
                    st.markdown("### Respuesta del Asistente:")
                    st.write(respuesta)
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
    st.markdown('<div class="panel-light"><h3>Políticas Comerciales de Referencia</h3></div>', unsafe_allow_html=True)

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
        <div class="panel-light">
            <strong>Políticas Generales:</strong>
            <ul>
                <li>El precio de la cotización final se determina según la escala alcanzada por el total del pedido.</li>
                <li>Los créditos son autorizados única y exclusivamente por el departamento administrativo de la empresa.</li>
            </ul>
        </div>
        """,
        unsafe_allow_html=True,
    )
