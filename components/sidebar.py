import streamlit as st
from datetime import datetime, date, timedelta
import pandas as pd

from data.database import DatabaseManager
from components.utils import format_currency, calculate_totals
import config

def render_sidebar(db: DatabaseManager):
    """Renderiza a sidebar com informações do usuário e resumos (SEM MENU DUPLICADO)"""
    
    with st.sidebar:
        # CSS personalizado para sidebar - SEM O CABEÇALHO FEIO
        st.markdown("""
        <style>
        /* Remover qualquer menu duplicado */
        .stRadio [role="radiogroup"] {
            display: none !important;
        }
        
        /* Estilo para a sidebar */
        section[data-testid="stSidebar"] {
            background: linear-gradient(180deg, #1a2634 0%, #2c3e50 100%) !important;
        }
        
        section[data-testid="stSidebar"] .stMarkdown {
            color: white !important;
        }
        
        /* Informações do usuário */
        .sidebar-user {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
            color: white;
            text-align: center;
        }
        
        .sidebar-user h3 {
            color: white !important;
            margin: 0;
            font-size: 1.2rem;
        }
        
        .sidebar-user p {
            color: rgba(255,255,255,0.9);
            margin: 0;
            font-size: 0.9rem;
        }
        
        /* Seções da sidebar */
        .sidebar-section {
            background: rgba(255,255,255,0.1);
            padding: 1rem;
            border-radius: 10px;
            margin-bottom: 1rem;
        }
        
        .sidebar-section h3 {
            color: white !important;
            font-size: 1rem;
            margin-bottom: 0.5rem;
        }
        
        /* Métricas */
        .sidebar-metric {
            background: rgba(255,255,255,0.1);
            padding: 0.5rem;
            border-radius: 8px;
            margin: 0.5rem 0;
        }
        
        .sidebar-metric label {
            color: rgba(255,255,255,0.8) !important;
            font-size: 0.8rem;
        }
        
        .sidebar-metric .metric-value {
            color: white !important;
            font-size: 1.1rem;
            font-weight: 700;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Informações do usuário (mais compacto)
        if 'user' in st.session_state and st.session_state.user:
            user = st.session_state.user
            role_icon = config.USER_ROLES.get(user.role, {}).get('icone', '👤')
            st.markdown(f"""
            <div class="sidebar-user">
                <h3>{role_icon} {user.nome}</h3>
                <p>@{user.username} · {user.role.capitalize()}</p>
            </div>
            """, unsafe_allow_html=True)
        
        # Filtros rápidos
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 📅 Período")
        
        periodo = st.selectbox(
            "Selecione o período",
            ["Mensal", "Semanal", "Trimestral", "Anual"],
            index=0,
            label_visibility="collapsed",
            key="sidebar_periodo"
        )
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Ações rápidas
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### ⚡ Ações Rápidas")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("💰 Receita", use_container_width=True, key="btn_receita"):
                st.session_state.nova_receita = True
                st.rerun()
        
        with col2:
            if st.button("💸 Despesa", use_container_width=True, key="btn_despesa"):
                st.session_state.nova_despesa = True
                st.rerun()
        
        if st.button("📊 Exportar", use_container_width=True, key="btn_exportar"):
            st.session_state.exportar_excel = True
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Resumo do mês
        st.markdown('<div class="sidebar-section">', unsafe_allow_html=True)
        st.markdown("### 📊 Resumo do Mês")
        
        hoje = date.today()
        inicio_mes = date(hoje.year, hoje.month, 1)
        
        transacoes_mes = db.get_transacoes_periodo(inicio_mes, hoje)
        totais = calculate_totals(transacoes_mes)
        
        st.markdown(f"""
        <div class="sidebar-metric">
            <label>💰 Receitas</label>
            <div class="metric-value">{format_currency(totais['receitas'])}</div>
        </div>
        <div class="sidebar-metric">
            <label>💸 Despesas</label>
            <div class="metric-value">{format_currency(totais['despesas'])}</div>
        </div>
        <div class="sidebar-metric">
            <label>⚖️ Saldo</label>
            <div class="metric-value">{format_currency(totais['receitas'] - totais['despesas'])}</div>
        </div>
        """, unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
        
        # Logout
        if st.button("🚪 Sair", use_container_width=True, key="btn_logout"):
            st.session_state.authenticated = False
            st.session_state.user = None
            st.rerun()