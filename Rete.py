import streamlit as st

# Configuración de página adaptable a móviles
st.set_page_config(page_title="Calculadora Retenciones", page_icon="🧮", layout="centered")

# --- VALOR DE LA UVT (Ejemplo para 2026) ---
VALOR_UVT = 52500  
BASE_SERVICIOS_UVT = 2
BASE_COMPRAS_UVT = 10
import streamlit as st

# Inicializar los estados de sesión para ambas calculadoras de forma independiente
if "items_servicios" not in st.session_state:
    st.session_state.items_servicios = []
if "items_compras" not in st.session_state:
    st.session_state.items_compras = []

st.title("🧮 Calculadora de Retenciones Express")
st.write("Suma de forma independiente tus compras y servicios para evaluar si aplican retención individualmente.")

st.markdown("---")

# ==========================================
# SECCIÓN 1: SELECCIÓN DEL PROVEEDOR
# ==========================================
st.subheader("1. Información del Proveedor")
perfil_proveedor = st.selectbox(
    "Tipo de proveedor que emite la cuenta/factura:", 
    ["Persona Jurídica", "Persona Natural - Declarante", "Persona Natural - NO Declarante"]
)

st.markdown("---")

# ==========================================
# SECCIÓN 2: CALCULADORA DE SERVICIOS
# ==========================================
st.subheader("🛠️ Calculadora de Servicios")
st.caption("Agrega aquí la mano de obra, mantenimientos, reparaciones, etc.")

with st.form("form_servicios", clear_on_submit=True):
    col_desc_s, col_val_s = st.columns([2, 1])
    with col_desc_s:
        desc_s = st.text_input("Descripción del servicio", placeholder="Ej. Mano de obra soplador", key="input_desc_s")
    with col_val_s:
        val_s = st.number_input("Valor ($)", min_value=0.0, step=10000.0, format="%.0f", key="input_val_s")
    
    btn_s = st.form_submit_button("➕ Agregar a Servicios")

if btn_s and val_s > 0:
    st.session_state.items_servicios.append({
        "descripcion": desc_s if desc_s else f"Servicio {len(st.session_state.items_servicios) + 1}",
        "valor": val_s
    })

# Mostrar y sumar servicios
total_servicios = 0.0
if st.session_state.items_servicios:
    for idx, item in enumerate(st.session_state.items_servicios):
        col_it_desc, col_it_val, col_it_del = st.columns([5, 3, 1])
        col_it_desc.write(f"• {item['descripcion']}")
        col_it_val.write(f"${item['valor']:,.0f}")
        if col_it_del.button("❌", key=f"del_s_{idx}"):
            st.session_state.items_servicios.pop(idx)
            st.rerun()
        total_servicios += item["valor"]
    
    if st.button("🗑️ Limpiar Servicios", key="clear_s"):
        st.session_state.items_servicios = []
        st.rerun()

st.metric(label="Total Servicios Acumulado", value=f"${total_servicios:,.0f}")

st.markdown("---")

# ==========================================
# SECCIÓN 3: CALCULADORA DE COMPRAS
# ==========================================
st.subheader("🛒 Calculadora de Compras")
st.caption("Agrega aquí los bienes físicos, materiales, repuestos o mercancía.")

with st.form("form_compras", clear_on_submit=True):
    col_desc_c, col_val_c = st.columns([2, 1])
    with col_desc_c:
        desc_c = st.text_input("Descripción del bien/repuesto", placeholder="Ej. Compra de empaques o zócalos", key="input_desc_c")
    with col_val_c:
        val_c = st.number_input("Valor ($)", min_value=0.0, step=10000.0, format="%.0f", key="input_val_c")
    
    btn_c = st.form_submit_button("➕ Agregar a Compras")

if btn_c and val_c > 0:
    st.session_state.items_compras.append({
        "descripcion": desc_c if desc_c else f"Compra {len(st.session_state.items_compras) + 1}",
        "valor": val_c
    })

# Mostrar y sumar compras
total_compras = 0.0
if st.session_state.items_compras:
    for idx, item in enumerate(st.session_state.items_compras):
        col_it_desc, col_it_val, col_it_del = st.columns([5, 3, 1])
        col_it_desc.write(f"• {item['descripcion']}")
        col_it_val.write(f"${item['valor']:,.0f}")
        if col_it_del.button("❌", key=f"del_c_{idx}"):
            st.session_state.items_compras.pop(idx)
            st.rerun()
        total_compras += item["valor"]
    
    if st.button("🗑️ Limpiar Compras", key="clear_c"):
        st.session_state.items_compras = []
        st.rerun()

st.metric(label="Total Compras Acumulado", value=f"${total_compras:,.0f}")

st.markdown("---")

# ==========================================
# SECCIÓN 4: CONSOLIDADO Y DECISIÓN DE RETENCIÓN
# ==========================================
st.subheader("📊 Diagnóstico Consolidado")

if total_servicios == 0 and total_compras == 0:
    st.info("Agrega conceptos en las secciones de arriba para ver el análisis de retención.")
else:
    # 1. Evaluación de Servicios
    base_min_servicios = BASE_SERVICIOS_UVT * VALOR_UVT
    aplica_rete_servicios = total_servicios >= base_min_servicios
    tarifa_s = 0.0
    rete_s = 0.0
    
    if aplica_rete_servicios:
        if perfil_proveedor == "Persona Jurídica":
            tarifa_s = 4.0
        elif perfil_proveedor == "Persona Natural - Declarante":
            tarifa_s = 4.0
        else:
            tarifa_s = 6.0
        rete_s = total_servicios * (tarifa_s / 100)

    # 2. Evaluación de Compras
    base_min_compras = BASE_COMPRAS_UVT * VALOR_UVT
    aplica_rete_compras = total_compras >= base_min_compras
    tarifa_c = 0.0
    rete_c = 0.0
    
    if aplica_rete_compras:
        if perfil_proveedor == "Persona Jurídica":
            tarifa_c = 2.5
        else:
            tarifa_c = 3.5
        rete_c = total_compras * (tarifa_c / 100)

    # 3. Presentar Resultados en Tabla Limpia
    st.markdown("### Resumen por concepto")
    
    # Crear estructura visual de tabla para que sea fácil de entender
    st.write(f"**Proveedor:** {perfil_proveedor}")
    
    tabla_datos = [
        {
            "Concepto": "🛠️ Servicios",
            "Monto Ingresado": f"${total_servicios:,.0f}",
            "Base Mínima (UVT)": f"${base_min_servicios:,.0f} (4 UVT)",
            "¿Supera Base?": "SÍ" if aplica_rete_servicios else "NO",
            "Tarifa": f"{tarifa_s}%" if aplica_rete_servicios else "N/A",
            "Retención": f"${rete_s:,.0f}" if aplica_rete_servicios else "$0"
        },
        {
            "Concepto": "🛒 Compras",
            "Monto Ingresado": f"${total_compras:,.0f}",
            "Base Mínima (UVT)": f"${base_min_compras:,.0f} (27 UVT)",
            "¿Supera Base?": "SÍ" if aplica_rete_compras else "NO",
            "Tarifa": f"{tarifa_c}%" if aplica_rete_compras else "N/A",
            "Retención": f"${rete_c:,.0f}" if aplica_rete_compras else "$0"
        }
    ]
    st.table(tabla_datos)

    # Totales Finales con conversión explícita a float para evitar errores de tipo
    total_factura = float(total_servicios + total_compras)
    total_retenciones = float(rete_s + rete_c)
    neto_a_pagar = float(total_factura - total_retenciones)

    # Evitar que neto_a_pagar sea negativo por algún error de redondeo o entrada
    if neto_a_pagar < 0:
        neto_a_pagar = 0.0

    st.markdown("---")
    st.markdown("### Resumen de Pago")
    
    col_f1, col_f2, col_f3 = st.columns(3)
    
    # Formateamos los valores en variables de texto antes de pasarlos a st.metric
    val_factura = f"${total_factura:,.0f}"
    val_retenciones = f"${total_retenciones:,.0f}"
    val_neto = f"${neto_a_pagar:,.0f}"
    
    col_f1.metric(label="Total Facturado (Bruto)", value=val_factura)
    
    # El delta solo se muestra si realmente hay retenciones que restar
    if total_retenciones > 0:
        col_f2.metric(
            label="Total Retenciones", 
            value=val_retenciones, 
            delta=f"-{val_retenciones}", 
            delta_color="inverse"
        )
    else:
        col_f2.metric(label="Total Retenciones", value="$0")
        
    col_f3.metric(label="Neto a Pagar al Proveedor", value=val_neto)
