import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
from typing import List

from data.database import DatabaseManager
from data.models import Transacao
from components.utils import format_currency, calculate_totals, is_weekend, is_today
import config

def render_dashboard(db: DatabaseManager):
    # Título principal com estilo
    st.markdown('<h1 class="dashboard-title">📊 Painel de Controle Financeiro</h1>', unsafe_allow_html=True)
    
    # Filtros do dashboard
    with st.container(border=True):
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            periodo = st.selectbox(
                "Período",
                ["Este Mês", "Mês Passado", "Últimos 3 Meses", "Este Ano", "Personalizado"],
                index=0
            )
        
        with col2:
            if periodo == "Personalizado":
                data_inicio = st.date_input("Data Início")
            else:
                st.write("")  # Espaço vazio
        
        with col3:
            if periodo == "Personalizado":
                data_fim = st.date_input("Data Fim")
            else:
                if st.button("🔄 Atualizar", use_container_width=True, type="primary"):
                    st.rerun()
    
    # Determinar período
    hoje = date.today()
    
    if periodo == "Este Mês":
        data_inicio = date(hoje.year, hoje.month, 1)
        data_fim = hoje
    elif periodo == "Mês Passado":
        if hoje.month == 1:
            data_inicio = date(hoje.year - 1, 12, 1)
            data_fim = date(hoje.year, hoje.month, 1) - timedelta(days=1)
        else:
            data_inicio = date(hoje.year, hoje.month - 1, 1)
            data_fim = date(hoje.year, hoje.month, 1) - timedelta(days=1)
    elif periodo == "Últimos 3 Meses":
        data_inicio = hoje - timedelta(days=90)
        data_fim = hoje
    elif periodo == "Este Ano":
        data_inicio = date(hoje.year, 1, 1)
        data_fim = hoje
    else:  # Personalizado
        if 'data_inicio' not in locals():
            data_inicio = hoje - timedelta(days=30)
        if 'data_fim' not in locals():
            data_fim = hoje
    
    # Buscar transações
    transacoes = db.get_transacoes_periodo(data_inicio, data_fim)
    
    # Calcular totais
    receitas = sum(t.valor for t in transacoes if t.tipo == 'receita')
    despesas = sum(t.valor for t in transacoes if t.tipo == 'despesa')
    saldo = receitas - despesas
    
    # Cards de resumo
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            label="💰 Receitas Totais",
            value=format_currency(receitas),
            delta=f"{len([t for t in transacoes if t.tipo == 'receita'])} lançamentos"
        )
    
    with col2:
        st.metric(
            label="💸 Despesas Totais",
            value=format_currency(despesas),
            delta=f"{len([t for t in transacoes if t.tipo == 'despesa'])} lançamentos",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            label="⚖️ Saldo do Período",
            value=format_currency(saldo),
            delta=f"{((saldo/receitas*100) if receitas > 0 else 0):.1f}% de margem"
        )
    
    # Gráficos
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📊 Distribuição Receitas vs Despesas")
        
        if transacoes:
            # Gráfico de pizza
            fig_pizza = go.Figure(data=[go.Pie(
                labels=['Receitas', 'Despesas'],
                values=[receitas, despesas],
                hole=0.4,
                marker=dict(colors=[config.COLORS['receita'], config.COLORS['despesa']]),
                textinfo='label+percent',
                texttemplate='%{label}<br>%{percent:.1%}',
                hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}<extra></extra>'
            )])
            
            fig_pizza.update_layout(
                showlegend=False,
                height=400,
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)'
            )
            
            st.plotly_chart(fig_pizza, use_container_width=True)
        else:
            st.info("📭 Sem dados para exibir o gráfico.")
    
    with col2:
        st.subheader("📈 Evolução Diária")
        
        # Calcular evolução
        if transacoes:
            # Agrupar por dia
            df_dias = pd.DataFrame([
                {
                    'data': t.data,
                    'tipo': t.tipo,
                    'valor': t.valor
                } for t in transacoes
            ])
            
            df_dias['data'] = pd.to_datetime(df_dias['data'])
            
            # Criar série de datas completa
            datas_range = pd.date_range(start=data_inicio, end=data_fim, freq='D')
            df_evolucao = pd.DataFrame({'data': datas_range})
            
            # Calcular receitas e despesas por dia
            df_receitas = df_dias[df_dias['tipo'] == 'receita'].groupby('data')['valor'].sum().reset_index()
            df_despesas = df_dias[df_dias['tipo'] == 'despesa'].groupby('data')['valor'].sum().reset_index()
            
            df_evolucao = df_evolucao.merge(df_receitas, on='data', how='left').rename(columns={'valor': 'receitas'})
            df_evolucao = df_evolucao.merge(df_despesas, on='data', how='left').rename(columns={'valor': 'despesas'})
            
            df_evolucao = df_evolucao.fillna(0)
            df_evolucao['saldo'] = df_evolucao['receitas'] - df_evolucao['despesas']
            df_evolucao['saldo_acumulado'] = df_evolucao['saldo'].cumsum()
            
            # Gráfico de linha
            fig_linha = go.Figure()
            
            fig_linha.add_trace(go.Scatter(
                x=df_evolucao['data'],
                y=df_evolucao['receitas'],
                mode='lines+markers',
                name='Receitas',
                line=dict(color=config.COLORS['receita'], width=2),
                marker=dict(size=4)
            ))
            
            fig_linha.add_trace(go.Scatter(
                x=df_evolucao['data'],
                y=df_evolucao['despesas'],
                mode='lines+markers',
                name='Despesas',
                line=dict(color=config.COLORS['despesa'], width=2),
                marker=dict(size=4)
            ))
            
            fig_linha.add_trace(go.Scatter(
                x=df_evolucao['data'],
                y=df_evolucao['saldo_acumulado'],
                mode='lines',
                name='Saldo Acumulado',
                line=dict(color=config.COLORS['secondary'], width=3, dash='dash')
            ))
            
            fig_linha.update_layout(
                height=400,
                xaxis_title='Data',
                yaxis_title='Valor (R$)',
                hovermode='x unified',
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                legend=dict(
                    yanchor="top",
                    y=0.99,
                    xanchor="left",
                    x=0.01
                )
            )
            
            fig_linha.update_yaxes(tickprefix='R$ ')
            
            st.plotly_chart(fig_linha, use_container_width=True)
        else:
            st.info("📭 Sem dados para exibir o gráfico.")
    
    # Últimos lançamentos
    st.subheader("📝 Últimos Lançamentos")
    
    if transacoes:
        # Ordenar por data (mais recente primeiro)
        transacoes_recentes = sorted(transacoes, key=lambda x: x.data, reverse=True)[:10]
        
        # Criar tabela HTML
        html_table = '<table class="finance-table"><thead><tr>'
        html_table += '<th>Data</th><th>Tipo</th><th>Categoria</th><th>Cliente/Fornecedor</th><th>Valor</th><th>Status</th>'
        html_table += '</tr></thead><tbody>'
        
        for t in transacoes_recentes:
            categoria = db.get_categoria(t.categoria_id)
            
            html_table += '<tr>'
            html_table += f'<td>{t.data.strftime("%d/%m/%Y")}</td>'
            html_table += f'<td>{"💰" if t.tipo == "receita" else "💸"}</td>'
            html_table += f'<td>{categoria.nome if categoria else "N/A"}</td>'
            html_table += f'<td>{t.cliente or "-"}</td>'
            
            valor_class = "positive-value" if t.tipo == "receita" else "negative-value"
            html_table += f'<td class="{valor_class}">{format_currency(t.valor)}</td>'
            
            status_icon = "✅" if t.status == "pago" else "⏳"
            html_table += f'<td>{status_icon} {t.status.capitalize()}</td>'
            
            html_table += '</tr>'
        
        html_table += '</tbody></table>'
        
        st.markdown(html_table, unsafe_allow_html=True)
    else:
        st.info("📭 Nenhum lançamento encontrado para o período selecionado.")