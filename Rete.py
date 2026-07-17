import streamlit as st

# Configuración de página adaptable a móviles
st.set_page_config(page_title="Calculadora Retenciones", page_icon="🧮", layout="centered")

# --- VALOR DE LA UVT (Ejemplo para 2026) ---
VALOR_UVT = 52500  
BASE_SERVICIOS_UVT = 10
BASE_COMPRAS_UVT = 2

# Inicializar la lista de ítems en la sesión para que no se borren al interactuar
if "items_calculadora" not in st.session_state:
    st.session_state.items_calculadora = []

st.title("🧮 Calculadora de Retenciones Express")
st.write("Suma los conceptos de tu cotización o factura y evalúa la retención en la fuente.")

st.markdown("---")

# ==========================================
# SECCIÓN 1: CALCULADORA / SUMADORA DE ÍTEMS
# ==========================================
st.subheader("1. Sumadora de Conceptos")

# Formulario para agregar ítems sin recargar la app por cada letra escrita
with st.form("agregar_item_form", clear_on_submit=True):
    col_desc, col_val = st.columns([2, 1])
    with col_desc:
        descripcion = st.text_input("Descripción del trabajo / repuesto", placeholder="Ej. Cambio de zócalo")
    with col_val:
        valor = st.number_input("Valor ($)", min_value=0.0, step=10000.0, format="%.0f")
    
    boton_agregar = st.form_submit_button("➕ Agregar a la lista")

if boton_agregar and valor > 0:
    # Agregar ítem a la lista en el estado de sesión
    st.session_state.items_calculadora.append({
        "descripcion": descripcion if descripcion else f"Ítem {len(st.session_state.items_calculadora) + 1}",
        "valor": valor
    })

# Mostrar la lista de ítems agregados
monto_total = 0.0
if st.session_state.items_calculadora:
    st.write("**Ítems agregados:**")
    for idx, item in enumerate(st.session_state.items_calculadora):
        col_item_desc, col_item_val, col_item_borrar = st.columns([5, 3, 1])
        col_item_desc.write(f"• {item['descripcion']}")
        col_item_val.write(f"${item['valor']:,.0f}")
        
        # Botón para eliminar un ítem específico
        if col_item_borrar.button("❌", key=f"del_{idx}"):
            st.session_state.items_calculadora.pop(idx)
            st.rerun()
            
        monto_total += item["valor"]
    
    # Botón para limpiar toda la lista
    if st.button("🗑️ Limpiar calculadora"):
        st.session_state.items_calculadora = []
        st.rerun()
else:
    st.info("La calculadora está vacía. Agrega los ítems de tu cotización arriba.")

# Mostrar el total acumulado de forma destacada
st.metric(label="Monto Total Acumulado (Base Gravable)", value=f"${monto_total:,.0f}")

st.markdown("---")

# ==========================================
# SECCIÓN 2: PARÁMETROS TRIBUTARIOS
# ==========================================
st.subheader("2. Parámetros de Retención")

col_tipo, col_prov = st.columns(2)

with col_tipo:
    tipo_transaccion = st.selectbox(
        "Tipo de transacción", 
        ["Servicios (General)", "Compras (General)"]
    )

with col_prov:
    perfil_proveedor = st.selectbox(
        "Tipo de proveedor", 
        ["Persona Jurídica", "Persona Natural - Declarante", "Persona Natural - NO Declarante"]
    )

st.markdown("---")

# ==========================================
# SECCIÓN 3: CÁLCULO DE LA RETENCIÓN
# ==========================================
st.subheader("3. Resultado del Análisis")

if monto_total <= 0:
    st.warning("Agrega conceptos en la sección 1 para calcular la retención.")
else:
    aplica_rete = False
    tarifa = 0.0
    base_minima = 0.0
    
    if "Servicios" in tipo_transaccion:
        base_minima = BASE_SERVICIOS_UVT * VALOR_UVT
        if monto_total >= base_minima:
            aplica_rete = True
            if perfil_proveedor == "Persona Jurídica":
                tarifa = 4.0
            elif perfil_proveedor == "Persona Natural - Declarante":
                tarifa = 4.0
            else:  # No declarante
                tarifa = 6.0
                
    elif "Compras" in tipo_transaccion:
        base_minima = BASE_COMPRAS_UVT * VALOR_UVT
        if monto_total >= base_minima:
            aplica_rete = True
            if perfil_proveedor == "Persona Jurídica":
                tarifa = 2.5
            else: # Persona natural (Declarante o No Declarante suele ser 3.5% general en compras)
                tarifa = 3.5

    # Renderizar resultados
    col_res1, col_res2 = st.columns(2)
    with col_res1:
        st.write(f"**Base mínima requerida:** ${base_minima:,.0f} ({base_minima/VALOR_UVT:.0f} UVT)")
        st.write(f"**Tu valor acumulado:** ${monto_total:,.0f}")
        
    with col_res2:
        if aplica_rete:
            valor_retencion = monto_total * (tarifa / 100)
            neto_pagar = monto_total - valor_retencion
            
            st.error(f"⚠️ **SÍ APLICA RETENCIÓN**")
            st.metric(label=f"Retención a Practicar ({tarifa}%)", value=f"${valor_retencion:,.0f}")
            st.metric(label="Neto a Pagar al Proveedor", value=f"${neto_pagar:,.0f}")
        else:
            st.success("✅ **NO APLICA RETENCIÓN**")
            st.write("El monto acumulado no supera el tope mínimo legal establecido para este concepto.")
