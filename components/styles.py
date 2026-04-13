import streamlit as st

def load_css():
    """Carrega estilos CSS personalizados que funcionam em temas claro e escuro"""
    st.markdown("""
    <style>
    /* Garantir que todos os textos tenham contraste adequado */
    .stMarkdown, .stText, p, li, span:not(.st-eb) {
        color: inherit !important;
    }
    
    /* Cabeçalhos com cor escura para fundo claro */
    h1, h2, h3, h4, h5, h6 {
        color: #2c3e50 !important;
    }
    
    /* Título principal com gradiente */
    h1 {
        background: linear-gradient(90deg, #667eea 0%, #764ba2 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        font-weight: 700 !important;
    }
    
    /* Fundo branco para métricas para garantir legibilidade */
    div[data-testid="stMetricValue"] {
        background-color: white !important;
        color: #2c3e50 !important;
        padding: 10px !important;
        border-radius: 8px !important;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    }
    
    /* Estilo para linhas de fim de semana na tabela */
    .weekend-row-css {
        background-color: #f0f0f0 !important;
    }
    
    /* Estilo para o dia atual na tabela */
    .today-row-css {
        background-color: #fff9e6 !important;
        border-left: 4px solid #ff9800 !important;
    }
    
    /* Container para categorias com retração */
    .categoria-container {
        border: 1px solid #e0e0e0;
        border-radius: 8px;
        margin-bottom: 10px;
        overflow: hidden;
        background-color: white;
    }
    
    .categoria-header {
        background-color: #f8f9fa;
        padding: 12px 15px;
        cursor: pointer;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-weight: 600;
        color: #2c3e50 !important;
        border-bottom: 1px solid #e0e0e0;
    }
    
    .categoria-header:hover {
        background-color: #e9ecef;
    }
    
    .categoria-content {
        padding: 15px;
        background-color: white;
    }
    
    /* Botões com texto escuro */
    .stButton > button {
        color: #2c3e50 !important;
        background-color: white !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 8px !important;
        font-weight: 600 !important;
    }
    
    .stButton > button:hover {
        background-color: #f8f9fa !important;
        border-color: #667eea !important;
    }
    
    /* Botão primário */
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;
        color: white !important;
        border: none !important;
    }
    
    /* Selectbox com texto escuro */
    .stSelectbox div[data-baseweb="select"] {
        background-color: white !important;
        color: #2c3e50 !important;
    }
    
    /* Input de texto */
    .stTextInput input {
        background-color: white !important;
        color: #2c3e50 !important;
    }
    
    /* Dataframe */
    .stDataFrame {
        background-color: white !important;
        border: 1px solid #e0e0e0 !important;
        border-radius: 10px !important;
    }
    
    /* Expander */
    .streamlit-expanderHeader {
        background-color: #f8f9fa !important;
        color: #2c3e50 !important;
        border-radius: 8px !important;
        border: 1px solid #e0e0e0 !important;
    }
    
    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%) !important;
    }
    
    section[data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        color: white !important;
    }
    
    /* Cards de métrica na sidebar */
    .sidebar-metric {
        background: rgba(255,255,255,0.1);
        padding: 0.75rem;
        border-radius: 8px;
        margin: 0.5rem 0;
    }
    
    .sidebar-metric label {
        color: rgba(255,255,255,0.9) !important;
    }
    
    .sidebar-metric .metric-value {
        color: white !important;
        font-size: 1.2rem;
        font-weight: 700;
    }
    
    /* Footer */
    .footer {
        text-align: center;
        padding: 1rem;
        color: #7f8c8d !important;
        font-size: 0.9rem;
    }
    </style>
    """, unsafe_allow_html=True)