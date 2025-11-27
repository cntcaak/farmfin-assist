import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import datetime
import os
from translations import LANGUAGES, get_text

# ==========================================
# 1. CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="FarmFin Assist | NABARD 2025",
    page_icon="🌾",
    layout="wide"
)

# Custom Styling
st.markdown("""
    <style>
    .main { background-color: #f0f8f5; }
    div.stButton > button:first-child {
        background-color: #2e7d32; color: white; border-radius: 8px; border: none;
    }
    div.stButton > button[kind="primary"] {
        background-color: #d32f2f !important; color: white !important;
    }
    h1, h2, h3 { color: #1b5e20; font-family: 'Sans-serif'; }
    </style>
    """, unsafe_allow_html=True)

# ==========================================
# 2. STATE & HELPERS
# ==========================================
def get_defaults():
    return {'name': '', 'land': 0.0, 'crop': 'Wheat', 'district': '', 'income': 0, 'expenses': 0, 'emi': 0}

if 'farmer_data' not in st.session_state:
    st.session_state.farmer_data = get_defaults()

if 'lang_code' not in st.session_state:
    st.session_state.lang_code = 'en'

def t(key):
    return get_text(st.session_state.lang_code, key)

def get_season_text():
    month = datetime.datetime.now().month
    if month >= 10 or month <= 3: return t('season_rabi')
    elif 4 <= month <= 5: return t('season_zaid')
    else: return t('season_kharif')

# ==========================================
# 3. SIDEBAR
# ==========================================
def sidebar_menu():
    st.sidebar.title("🌍 Language / भाषा")
    lang_names = list(LANGUAGES.keys())
    # Default to English index 0
    selected = st.sidebar.selectbox("Select", lang_names, index=0)
    st.session_state.lang_code = LANGUAGES[selected]
    
    st.sidebar.markdown("---")
    st.sidebar.title(t('title'))
    
    options = {
        "Home": t('nav_home'),
        "Profile": t('nav_profile'),
        "Health": t('nav_health'),
        "Schemes": t('nav_schemes'),
        "Calculator": t('nav_calc'),
        "Report": t('nav_report')
    }
    return st.sidebar.radio("Menu", list(options.keys()), format_func=lambda x: options[x])

# ==========================================
# 4. LOGIC
# ==========================================
def calculate_metrics(inc, exp, emi):
    yearly_emi = emi * 12
    net = inc - exp
    dscr = round(net / yearly_emi, 2) if yearly_emi > 0 else (10.0 if net > 0 else 0.0)
    score = 600
    if dscr > 1.5: score += 100
    elif dscr < 1.0: score -= 100
    if st.session_state.farmer_data['land'] > 2: score += 50
    return dscr, min(900, max(300, score))

# ==========================================
# 5. PAGES
# ==========================================
def page_home():
    # Image Logic
    img_files = ["farm_header.jpg", "farm_header.jpg.jpg", "farm_header.jpeg"]
    loaded = False
    col_l, col_img, col_r = st.columns([1, 2, 1])
    with col_img:
        for img in img_files:
            if os.path.exists(img):
                st.image(img, use_container_width=True)
                loaded = True
                break
    
    st.title(t('title'))
    st.subheader(t('subtitle'))
    st.info(t('intro'))
    
    c1, c2, c3 = st.columns(3)
    c1.metric(t('sup_lang'), "22")
    c2.metric(t('metric_interest'), "~7% (KCC)")
    c3.metric(t('metric_season'), get_season_text())

def page_profile():
    st.header(t('nav_profile'))
    with st.form("profile"):
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input(t('name'), st.session_state.farmer_data['name'])
            land = st.number_input(t('land_size'), min_value=0.0, value=float(st.session_state.farmer_data['land']))
        with c2:
            district = st.text_input(t('district'), st.session_state.farmer_data['district'])
            # Crops are hard to translate dynamically without a massive dict, keeping English for stability
            crop = st.selectbox(t('crop_type'), ["Wheat", "Rice", "Cotton", "Sugarcane", "Maize"])
        
        if st.form_submit_button(t('save_btn')):
            st.session_state.farmer_data.update({'name': name, 'land': land, 'district': district, 'crop': crop})
            st.success("✅ Saved!")

    if st.button(t('reset_btn'), type="primary"):
        st.session_state.farmer_data = get_defaults()
        st.rerun()

def page_health():
    st.header(t('nav_health'))
    c1, c2 = st.columns(2)
    with c1:
        inc = st.number_input(t('income_annual'), value=st.session_state.farmer_data['income'])
        exp = st.number_input(t('expenses_annual'), value=st.session_state.farmer_data['expenses'])
    with c2:
        emi = st.number_input(t('loan_emi'), value=st.session_state.farmer_data['emi'])
        
    if st.button(t('calc_health')):
        st.session_state.farmer_data.update({'income': inc, 'expenses': exp, 'emi': emi})
        dscr, score = calculate_metrics(inc, exp, emi)
        
        st.divider()
        m1, m2 = st.columns(2)
        m1.metric(t('dscr_score'), dscr)
        m2.metric(t('credit_score'), score)
        
        if dscr < 1.0: 
            st.error(t('risk_high'))
            st.write(t('health_tip_bad'))
        else: 
            st.success(t('risk_safe'))
            st.write(t('health_tip_good'))
            
        fig, ax = plt.subplots()
        ax.bar(['Inc', 'Exp'], [inc, exp], color=['#4CAF50', '#d32f2f'])
        st.pyplot(fig)

    st.markdown("---")
    if st.button(t('reset_btn'), type="primary", key="reset_health"):
        st.session_state.farmer_data['income'] = 0
        st.rerun()

def page_schemes():
    st.header(t('nav_schemes'))
    st.markdown(f"### {t('scheme_title')}")
    st.markdown(t('scheme_1'))
    st.markdown(t('scheme_2'))
    st.markdown(t('scheme_3'))

def page_calculator():
    st.header(t('nav_calc'))
    c1, c2 = st.columns(2)
    area = c1.number_input(t('calc_area'), 1.0)
    yield_val = c2.number_input(t('calc_yield'), 20.0)
    price = c1.number_input(t('calc_price'), 2000.0)
    cost = c2.number_input(t('calc_cost'), 15000.0)
    
    if st.button(t('calc_run')):
        profit = (area * yield_val * price) - (area * cost)
        st.metric(t('est_profit'), f"₹ {profit:,.2f}")
        if profit > 0: st.success(t('res_profit'))
        else: st.error(t('res_loss'))
        
    st.markdown("---")
    if st.button(t('reset_btn'), type="primary", key="reset_calc"):
        st.rerun()

def page_report():
    st.header(t('nav_report'))
    if st.button("Generate PDF"):
        pdf = FPDF()
        pdf.add_page()
        pdf.set_font("Arial", size=16)
        pdf.cell(200, 10, txt="FarmFin Assist Report", ln=1, align='C')
        pdf.line(10, 20, 200, 20)
        pdf.set_font("Arial", size=12)
        pdf.ln(20)
        # We keep report text in English/Latin to avoid Font errors in PDF generation
        pdf.cell(200, 10, txt=f"Name: {st.session_state.farmer_data['name']}", ln=1)
        pdf.cell(200, 10, txt=f"District: {st.session_state.farmer_data['district']}", ln=1)
        pdf.output("report.pdf")
        with open("report.pdf", "rb") as f:
            st.download_button(t('download_pdf'), f, file_name="Farmer_Report.pdf")

# ==========================================
# 6. ROUTER
# ==========================================
selection = sidebar_menu()

if selection == "Home": page_home()
elif selection == "Profile": page_profile()
elif selection == "Health": page_health()
elif selection == "Schemes": page_schemes()
elif selection == "Calculator": page_calculator()
elif selection == "Report": page_report()
