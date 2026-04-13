import streamlit as st 
from streamlit_option_menu import option_menu
import pandas as pd
from datetime import datetime, date
import os
from pathlib import Path

# Configuração da página - MUST BE FIRST
st.set_page_config(
    page_title="Sistema Financeiro - Fluxo de Caixa",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS FORTE e agressivo para garantir visibilidade
st.markdown("""
<style>
    /* Reset completo para garantir visibilidade */
    .main > div {
        background-color: #ffffff !important;
    }
    
    /* Títulos em preto e negrito */
    h1, h2, h3, h4, h5, h6 {
        color: #000000 !important;
        font-weight: 700 !important;
    }
    
    h1 {
        font-size: 2.5rem !important;
        border-bottom: 3px solid #667eea !important;
        padding-bottom: 10px !important;
        margin-bottom: 20px !important;
    }
    
    /* Texto normal em preto */
    p, span, div, label, .stMarkdown, .stText {
        color: #000000 !important;
    }
    
    /* Dashboard title */
    .dashboard-title {
        font-size: 2.2rem !important;
        font-weight: 700 !important;
        color: #000000 !important;
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 20px !important;
    }
    
    /* Cards de métrica com texto preto */
    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        padding: 20px !important;
        border-radius: 15px !important;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1) !important;
    }
    
    div[data-testid="stMetric"] label {
        color: white !important;
        font-size: 1rem !important;
        font-weight: 500 !important;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricValue"] {
        color: white !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
        background-color: transparent !important;
    }
    
    div[data-testid="stMetric"] div[data-testid="stMetricDelta"] {
        color: rgba(255,255,255,0.9) !important;
    }
    
    /* Selectbox com texto preto */
    .stSelectbox div[data-baseweb="select"] {
        background-color: #f8f9fa !important;
        border: 1px solid #ced4da !important;
    }
    
    .stSelectbox div[data-baseweb="select"] span {
        color: #000000 !important;
    }
    
    /* Botões */
    .stButton > button {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        border: 1px solid #ced4da !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background-color: #e9ecef !important;
        border-color: #667eea !important;
    }
    
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    /* DataFrame */
    .stDataFrame {
        border: 1px solid #dee2e6 !important;
        border-radius: 10px !important;
        background-color: white !important;
    }
    
    .stDataFrame td, .stDataFrame th {
        color: #000000 !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        border: 1px solid #dee2e6 !important;
        font-weight: 600 !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1a2634 0%, #2c3e50 100%) !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* Cards da sidebar */
    .sidebar-user {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        padding: 1.5rem !important;
        border-radius: 15px !important;
        margin-bottom: 1.5rem !important;
        color: white !important;
    }
    
    .sidebar-user h3 {
        color: white !important;
    }
    
    .sidebar-metric {
        background: rgba(255,255,255,0.1) !important;
        padding: 1rem !important;
        border-radius: 10px !important;
        margin: 0.5rem 0 !important;
    }
    
    .sidebar-metric label {
        color: rgba(255,255,255,0.9) !important;
    }
    
    .sidebar-metric .metric-value {
        color: white !important;
        font-size: 1.2rem !important;
        font-weight: 700 !important;
    }
    
    /* Footer */
    .footer {
        text-align: center !important;
        padding: 1rem !important;
        color: #6c757d !important;
        font-size: 0.9rem !important;
        border-top: 1px solid #dee2e6 !important;
        margin-top: 2rem !important;
    }
    
    /* Info boxes */
    .stAlert {
        background-color: #f8f9fa !important;
        color: #000000 !important;
        border: 1px solid #dee2e6 !important;
    }
    
    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px !important;
        background-color: #f8f9fa !important;
        padding: 10px !important;
        border-radius: 10px !important;
    }
    
    .stTabs [data-baseweb="tab"] {
        color: #000000 !important;
        font-weight: 600 !important;
    }
    
    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important !important;
    }
    
    /* Linhas de fim de semana */
    .weekend-row {
        background-color: #f8f9fa !important;
    }
    
    /* Linha do dia atual */
    .today-row {
        background-color: #fff3cd !important;
        border-left: 4px solid #ffc107 !important;
    }
    
    /* Tabela HTML personalizada */
    .finance-table {
        width: 100%;
        border-collapse: collapse;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        background-color: white;
        border: 1px solid #dee2e6;
        border-radius: 10px;
        overflow: hidden;
    }
    
    .finance-table th {
        background-color: #2c3e50;
        color: white !important;
        padding: 12px;
        text-align: left;
        font-weight: 600;
        font-size: 0.9rem;
    }
    
    .finance-table td {
        padding: 10px 12px;
        border-bottom: 1px solid #e9ecef;
        color: #000000 !important;
    }
    
    .finance-table tr:hover {
        background-color: #f8f9fa !important;
    }
    
    .finance-table .weekend-row {
        background-color: #f1f3f5;
    }
    
    .finance-table .today-row {
        background-color: #fff3cd;
        border-left: 4px solid #ffc107;
    }
    
    /* Valor positivo */
    .positive-value {
        color: #27ae60 !important;
        font-weight: 600 !important;
    }
    
    /* Valor negativo */
    .negative-value {
        color: #e74c3c !important;
        font-weight: 600 !important;
    }
</style>
""", unsafe_allow_html=True)

# Importar módulos
from data.database import DatabaseManager
from components.sidebar import render_sidebar
from components.utils import format_currency, show_info_message
import config

# Inicializar banco de dados
@st.cache_resource
def init_database():
    return DatabaseManager()

db = init_database()

# Sistema de autenticação
def check_authentication():
    """Verifica se usuário está autenticado"""
    if 'authenticated' not in st.session_state:
        st.session_state.authenticated = False
    if 'user' not in st.session_state:
        st.session_state.user = None
    
    return st.session_state.authenticated

def login():
    """Tela de login"""
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        st.markdown('<h1 style="text-align: center; color: #000000;">💰 Sistema Financeiro</h1>', unsafe_allow_html=True)
        st.markdown('<p style="text-align: center; font-size: 1.2rem; color: #000000;">Fluxo de Caixa</p>', unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)
        
        with st.container(border=True):
            with st.form("login_form"):
                username = st.text_input("👤 Usuário", placeholder="Digite seu usuário")
                password = st.text_input("🔒 Senha", type="password", placeholder="Digite sua senha")
                
                col_btn1, col_btn2 = st.columns(2)
                with col_btn1:
                    submit = st.form_submit_button("🚀 Entrar", type="primary", use_container_width=True)
                with col_btn2:
                    st.form_submit_button("🧹 Limpar", use_container_width=True)
            
            if submit:
                user = db.get_usuario_by_username(username)
                
                if user and user.senha == password and user.ativo:
                    st.session_state.authenticated = True
                    st.session_state.user = user
                    st.rerun()
                else:
                    st.error("❌ Usuário ou senha incorretos!")
            
            st.info("""
            **Credenciais de Teste:**
            - admin / admin123
            - financeiro / fin123
            - fiscal / fis123
            """)

def main_app():
    """Aplicação principal após login"""
    
    # Menu principal
    selected = option_menu(
        menu_title=None,
        options=["Dashboard", "Fluxo de Caixa", "Lançamentos", "Relatórios", "Configurações"],
        icons=["house-fill", "cash-stack", "list-check", "graph-up", "gear-fill"],
        menu_icon="cast",
        default_index=0,
        orientation="horizontal",
        styles={
            "container": {"padding": "0!important", "background-color": "transparent"},
            "icon": {"color": "#667eea", "font-size": "1.2rem"},
            "nav-link": {
                "font-size": "1rem",
                "text-align": "center",
                "margin": "0px",
                "color": "#000000",
                "font-weight": "600",
                "padding": "0.75rem 1rem",
                "border-radius": "8px",
            },
            "nav-link-selected": {
                "background": "linear-gradient(135deg, #667eea 0%, #764ba2 100%)",
                "color": "white !important",
                "font-weight": "700",
            },
        }
    )
    
    # Sidebar
    render_sidebar(db)
    
    # Conteúdo principal
    if selected == "Dashboard":
        from pages.dashboard import render_dashboard
        render_dashboard(db)
    
    elif selected == "Fluxo de Caixa":
        from pages.fluxo_caixa import render_fluxo_caixa
        render_fluxo_caixa(db)
    
    elif selected == "Lançamentos":
        from pages.lancamentos import render_lancamentos
        render_lancamentos(db)
    
    elif selected == "Relatórios":
        from pages.relatorios import render_relatorios
        render_relatorios(db)
    
    elif selected == "Configurações":
        from pages.configuracoes import render_configuracoes
        render_configuracoes(db)
    
    # Footer
    st.markdown('<div class="footer">', unsafe_allow_html=True)
    st.markdown(f"💰 **Sistema Financeiro v{config.APP_CONFIG['app_version']}** | Desenvolvido pela área de crédito da Komatsu Forest")
    st.markdown('</div>', unsafe_allow_html=True)

# Ponto de entrada
def main():
    if check_authentication():
        main_app()
    else:
        login()

if __name__ == "__main__":
    main()