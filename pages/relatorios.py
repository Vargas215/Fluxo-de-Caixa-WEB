import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date, timedelta
import calendar

from data.database import DatabaseManager
from components.utils import format_currency
import config

def render_relatorios(db: DatabaseManager):
    st.title("📊 Relatórios")
    
    # Seleção do tipo de relatório
    tipo_relatorio = st.selectbox(
        "📋 Selecione o tipo de relatório",
        [
            "Fluxo de Caixa Mensal",
            "Receitas vs Despesas",
            "Por Categoria",
            "Evolução Anual",
            "Top Clientes/Fornecedores"
        ],
        index=0
    )
    
    # Filtros comuns
    col1, col2, col3 = st.columns([1, 1, 1])
    
    with col1:
        ano = st.number_input("Ano", min_value=2020, max_value=2030, value=date.today().year)
    
    with col2:
        if tipo_relatorio == "Fluxo de Caixa Mensal":
            mes = st.selectbox("Mês", list(range(1, 13)), format_func=lambda x: calendar.month_name[x])
        else:
            mes = None
    
    with col3:
        st.write("")  # Espaçador
        if st.button("📈 Gerar Relatório", type="primary", use_container_width=True):
            st.session_state.gerar_relatorio = True
    
    # Gerar relatório baseado na seleção
    if 'gerar_relatorio' in st.session_state and st.session_state.gerar_relatorio:
        st.markdown("---")
        
        if tipo_relatorio == "Fluxo de Caixa Mensal":
            gerar_relatorio_fluxo_caixa(db, ano, mes)
        elif tipo_relatorio == "Receitas vs Despesas":
            gerar_relatorio_receitas_despesas(db, ano)
        elif tipo_relatorio == "Por Categoria":
            gerar_relatorio_por_categoria(db, ano)
        elif tipo_relatorio == "Evolução Anual":
            gerar_relatorio_evolucao_anual(db, ano)
        elif tipo_relatorio == "Top Clientes/Fornecedores":
            gerar_relatorio_top_clientes(db, ano)

def gerar_relatorio_fluxo_caixa(db: DatabaseManager, ano: int, mes: int):
    """Gera relatório de fluxo de caixa mensal"""
    st.subheader(f"📈 Fluxo de Caixa - {calendar.month_name[mes]} {ano}")
    
    # Obter transações do mês
    transacoes = db.get_transacoes_mes(ano, mes)
    
    if not transacoes:
        st.info("📭 Nenhuma transação encontrada para este período.")
        return
    
    # Calcular dias no mês
    dias_no_mes = calendar.monthrange(ano, mes)[1]
    
    # Preparar dados por dia
    dias = []
    receitas_diarias = []
    despesas_diarias = []
    saldos_diarios = []
    
    saldo_acumulado = 0
    
    for dia in range(1, dias_no_mes + 1):
        data_dia = date(ano, mes, dia)
        
        # Calcular receitas e despesas do dia
        receitas_dia = sum(t.valor for t in transacoes if t.data.day == dia and t.tipo == 'receita')
        despesas_dia = sum(t.valor for t in transacoes if t.data.day == dia and t.tipo == 'despesa')
        
        saldo_dia = receitas_dia - despesas_dia
        saldo_acumulado += saldo_dia
        
        dias.append(f"{dia}")
        receitas_diarias.append(receitas_dia)
        despesas_diarias.append(despesas_dia)
        saldos_diarios.append(saldo_acumulado)
    
    # Criar gráfico de linha
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=dias,
        y=receitas_diarias,
        mode='lines+markers',
        name='Receitas',
        line=dict(color=config.COLORS['receita'], width=3),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=dias,
        y=despesas_diarias,
        mode='lines+markers',
        name='Despesas',
        line=dict(color=config.COLORS['despesa'], width=3),
        marker=dict(size=6)
    ))
    
    fig.add_trace(go.Scatter(
        x=dias,
        y=saldos_diarios,
        mode='lines+markers',
        name='Saldo Acumulado',
        line=dict(color=config.COLORS['secondary'], width=2, dash='dash'),
        marker=dict(size=4)
    ))
    
    fig.update_layout(
        title=f"Evolução Diária - {calendar.month_name[mes]} {ano}",
        xaxis_title='Dia do Mês',
        yaxis_title='Valor (R$)',
        hovermode='x unified',
        height=500
    )
    
    fig.update_yaxes(tickprefix='R$ ')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de resumo
    st.subheader("📋 Resumo Mensal")
    
    # Calcular totais
    total_receitas = sum(receitas_diarias)
    total_despesas = sum(despesas_diarias)
    saldo_final = total_receitas - total_despesas
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("💰 Total Receitas", format_currency(total_receitas))
    
    with col2:
        st.metric("💸 Total Despesas", format_currency(total_despesas))
    
    with col3:
        st.metric("⚖️ Saldo Final", format_currency(saldo_final), 
                 delta=format_currency(saldo_final))
    
    # Detalhamento por categoria
    st.subheader("🏷️ Detalhamento por Categoria")
    
    categorias_receitas = {}
    categorias_despesas = {}
    
    for t in transacoes:
        categoria = db.get_categoria(t.categoria_id)
        if categoria:
            if t.tipo == 'receita':
                categorias_receitas[categoria.nome] = categorias_receitas.get(categoria.nome, 0) + t.valor
            else:
                categorias_despesas[categoria.nome] = categorias_despesas.get(categoria.nome, 0) + t.valor
    
    col1, col2 = st.columns(2)
    
    with col1:
        if categorias_receitas:
            st.write("**📈 Receitas por Categoria:**")
            for cat, valor in sorted(categorias_receitas.items(), key=lambda x: x[1], reverse=True):
                percentual = (valor / total_receitas * 100) if total_receitas > 0 else 0
                st.write(f"- {cat}: {format_currency(valor)} ({percentual:.1f}%)")
        else:
            st.info("Sem receitas neste período")
    
    with col2:
        if categorias_despesas:
            st.write("**📉 Despesas por Categoria:**")
            for cat, valor in sorted(categorias_despesas.items(), key=lambda x: x[1], reverse=True):
                percentual = (valor / total_despesas * 100) if total_despesas > 0 else 0
                st.write(f"- {cat}: {format_currency(valor)} ({percentual:.1f}%)")
        else:
            st.info("Sem despesas neste período")

def gerar_relatorio_receitas_despesas(db: DatabaseManager, ano: int):
    """Gera relatório de receitas vs despesas por mês"""
    st.subheader(f"📊 Receitas vs Despesas - {ano}")
    
    # Preparar dados por mês
    meses = []
    receitas_mensais = []
    despesas_mensais = []
    saldos_mensais = []
    
    for mes in range(1, 13):
        transacoes_mes = db.get_transacoes_mes(ano, mes)
        
        receitas = sum(t.valor for t in transacoes_mes if t.tipo == 'receita')
        despesas = sum(t.valor for t in transacoes_mes if t.tipo == 'despesa')
        saldo = receitas - despesas
        
        meses.append(calendar.month_abbr[mes])
        receitas_mensais.append(receitas)
        despesas_mensais.append(despesas)
        saldos_mensais.append(saldo)
    
    # Gráfico de barras
    fig = go.Figure()
    
    fig.add_trace(go.Bar(
        x=meses,
        y=receitas_mensais,
        name='Receitas',
        marker_color=config.COLORS['receita']
    ))
    
    fig.add_trace(go.Bar(
        x=meses,
        y=despesas_mensais,
        name='Despesas',
        marker_color=config.COLORS['despesa']
    ))
    
    fig.update_layout(
        title=f"Receitas vs Despesas - {ano}",
        xaxis_title='Mês',
        yaxis_title='Valor (R$)',
        barmode='group',
        height=500
    )
    
    fig.update_yaxes(tickprefix='R$ ')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela de dados
    st.subheader("📋 Dados Mensais")
    
    dados_tabela = []
    for i, mes in enumerate(meses):
        dados_tabela.append({
            'Mês': calendar.month_name[i+1],
            'Receitas': receitas_mensais[i],
            'Despesas': despesas_mensais[i],
            'Saldo': saldos_mensais[i],
            'Margem (%)': (saldos_mensais[i] / receitas_mensais[i] * 100) if receitas_mensais[i] > 0 else 0
        })
    
    df = pd.DataFrame(dados_tabela)
    
    # Formatar valores
    df['Receitas'] = df['Receitas'].apply(lambda x: format_currency(x))
    df['Despesas'] = df['Despesas'].apply(lambda x: format_currency(x))
    df['Saldo'] = df['Saldo'].apply(lambda x: format_currency(x))
    df['Margem (%)'] = df['Margem (%)'].apply(lambda x: f"{x:.1f}%")
    
    st.dataframe(df, use_container_width=True, hide_index=True)

def gerar_relatorio_por_categoria(db: DatabaseManager, ano: int):
    """Gera relatório por categoria"""
    st.subheader(f"🏷️ Relatório por Categoria - {ano}")
    
    # Obter todas as transações do ano
    transacoes_ano = []
    for mes in range(1, 13):
        transacoes_ano.extend(db.get_transacoes_mes(ano, mes))
    
    if not transacoes_ano:
        st.info("📭 Nenhuma transação encontrada para este ano.")
        return
    
    # Agrupar por categoria
    dados_categorias = {}
    
    for t in transacoes_ano:
        categoria = db.get_categoria(t.categoria_id)
        if categoria:
            chave = f"{categoria.nome} ({'Receita' if t.tipo == 'receita' else 'Despesa'})"
            if chave not in dados_categorias:
                dados_categorias[chave] = {
                    'tipo': t.tipo,
                    'valor': 0,
                    'quantidade': 0
                }
            dados_categorias[chave]['valor'] += t.valor
            dados_categorias[chave]['quantidade'] += 1
    
    # Criar gráfico de pizza
    labels = list(dados_categorias.keys())
    valores = [dados_categorias[label]['valor'] for label in labels]
    
    # Gerar cores baseadas no tipo
    cores = []
    for label in labels:
        if 'Receita' in label:
            cores.append(config.COLORS['receita'])
        else:
            cores.append(config.COLORS['despesa'])
    
    fig = px.pie(
        names=labels,
        values=valores,
        title=f"Distribuição por Categoria - {ano}",
        color_discrete_sequence=cores
    )
    
    fig.update_traces(
        textinfo='percent+label+value',
        texttemplate='%{label}<br>%{value:,.2f}<br>(%{percent})',
        hovertemplate='<b>%{label}</b><br>Valor: R$ %{value:,.2f}<br>Percentual: %{percent}'
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Tabela detalhada
    st.subheader("📋 Detalhamento por Categoria")
    
    dados_tabela = []
    for label, dados in dados_categorias.items():
        dados_tabela.append({
            'Categoria': label,
            'Tipo': 'Receita' if dados['tipo'] == 'receita' else 'Despesa',
            'Valor Total': dados['valor'],
            'Quantidade': dados['quantidade'],
            'Média': dados['valor'] / dados['quantidade'] if dados['quantidade'] > 0 else 0
        })
    
    df = pd.DataFrame(dados_tabela)
    df = df.sort_values('Valor Total', ascending=False)
    
    # Formatar valores
    df['Valor Total'] = df['Valor Total'].apply(lambda x: format_currency(x))
    df['Média'] = df['Média'].apply(lambda x: format_currency(x))
    
    st.dataframe(df, use_container_width=True, hide_index=True)

def gerar_relatorio_evolucao_anual(db: DatabaseManager, ano: int):
    """Gera relatório de evolução anual"""
    st.subheader(f"📈 Evolução Anual - {ano}")
    
    # Obter dados do ano anterior para comparação
    ano_anterior = ano - 1
    
    dados_atual = []
    dados_anterior = []
    
    for mes in range(1, 13):
        # Ano atual
        transacoes_atual = db.get_transacoes_mes(ano, mes)
        receitas_atual = sum(t.valor for t in transacoes_atual if t.tipo == 'receita')
        despesas_atual = sum(t.valor for t in transacoes_atual if t.tipo == 'despesa')
        
        # Ano anterior
        transacoes_anterior = db.get_transacoes_mes(ano_anterior, mes)
        receitas_anterior = sum(t.valor for t in transacoes_anterior if t.tipo == 'receita')
        despesas_anterior = sum(t.valor for t in transacoes_anterior if t.tipo == 'despesa')
        
        dados_atual.append({
            'mes': calendar.month_abbr[mes],
            'receitas': receitas_atual,
            'despesas': despesas_atual,
            'saldo': receitas_atual - despesas_atual
        })
        
        dados_anterior.append({
            'mes': calendar.month_abbr[mes],
            'receitas': receitas_anterior,
            'despesas': despesas_anterior,
            'saldo': receitas_anterior - despesas_anterior
        })
    
    # Criar gráfico comparativo
    fig = go.Figure()
    
    fig.add_trace(go.Scatter(
        x=[d['mes'] for d in dados_atual],
        y=[d['saldo'] for d in dados_atual],
        mode='lines+markers',
        name=f'Saldo {ano}',
        line=dict(color=config.COLORS['success'], width=3)
    ))
    
    fig.add_trace(go.Scatter(
        x=[d['mes'] for d in dados_anterior],
        y=[d['saldo'] for d in dados_anterior],
        mode='lines+markers',
        name=f'Saldo {ano_anterior}',
        line=dict(color=config.COLORS['warning'], width=2, dash='dash')
    ))
    
    fig.update_layout(
        title=f"Evolução do Saldo - Comparativo {ano_anterior} vs {ano}",
        xaxis_title='Mês',
        yaxis_title='Saldo (R$)',
        hovermode='x unified',
        height=500
    )
    
    fig.update_yaxes(tickprefix='R$ ')
    
    st.plotly_chart(fig, use_container_width=True)
    
    # Métricas comparativas
    st.subheader("📊 Comparativo Anual")
    
    total_receitas_atual = sum(d['receitas'] for d in dados_atual)
    total_despesas_atual = sum(d['despesas'] for d in dados_atual)
    total_saldo_atual = total_receitas_atual - total_despesas_atual
    
    total_receitas_anterior = sum(d['receitas'] for d in dados_anterior)
    total_despesas_anterior = sum(d['despesas'] for d in dados_anterior)
    total_saldo_anterior = total_receitas_anterior - total_despesas_anterior
    
    # Calcular variações
    variacao_receitas = ((total_receitas_atual - total_receitas_anterior) / total_receitas_anterior * 100) if total_receitas_anterior > 0 else 0
    variacao_despesas = ((total_despesas_atual - total_despesas_anterior) / total_despesas_anterior * 100) if total_despesas_anterior > 0 else 0
    variacao_saldo = ((total_saldo_atual - total_saldo_anterior) / abs(total_saldo_anterior) * 100) if total_saldo_anterior != 0 else 0
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            f"💰 Receitas {ano}",
            format_currency(total_receitas_atual),
            delta=f"{variacao_receitas:+.1f}% vs {ano_anterior}"
        )
    
    with col2:
        st.metric(
            f"💸 Despesas {ano}",
            format_currency(total_despesas_atual),
            delta=f"{variacao_despesas:+.1f}% vs {ano_anterior}"
        )
    
    with col3:
        st.metric(
            f"⚖️ Saldo {ano}",
            format_currency(total_saldo_atual),
            delta=f"{variacao_saldo:+.1f}% vs {ano_anterior}"
        )

def gerar_relatorio_top_clientes(db: DatabaseManager, ano: int):
    """Gera relatório dos top clientes/fornecedores"""
    st.subheader(f"👥 Top Clientes/Fornecedores - {ano}")
    
    # Obter todas as transações do ano
    transacoes_ano = []
    for mes in range(1, 13):
        transacoes_ano.extend(db.get_transacoes_mes(ano, mes))
    
    # Agrupar por cliente/fornecedor
    clientes_receitas = {}
    fornecedores_despesas = {}
    
    for t in transacoes_ano:
        if t.cliente:
            if t.tipo == 'receita':
                clientes_receitas[t.cliente] = clientes_receitas.get(t.cliente, 0) + t.valor
            else:
                fornecedores_despesas[t.cliente] = fornecedores_despesas.get(t.cliente, 0) + t.valor
    
    # Top 10 clientes
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**🏆 Top 10 Clientes (Receitas)**")
        
        if clientes_receitas:
            top_clientes = sorted(clientes_receitas.items(), key=lambda x: x[1], reverse=True)[:10]
            
            dados = []
            for cliente, valor in top_clientes:
                dados.append({
                    'Cliente': cliente,
                    'Valor': format_currency(valor)
                })
            
            df_clientes = pd.DataFrame(dados)
            st.dataframe(df_clientes, use_container_width=True, hide_index=True)
        else:
            st.info("Sem dados de clientes")
    
    with col2:
        st.write("**🏆 Top 10 Fornecedores (Despesas)**")
        
        if fornecedores_despesas:
            top_fornecedores = sorted(fornecedores_despesas.items(), key=lambda x: x[1], reverse=True)[:10]
            
            dados = []
            for fornecedor, valor in top_fornecedores:
                dados.append({
                    'Fornecedor': fornecedor,
                    'Valor': format_currency(valor)
                })
            
            df_fornecedores = pd.DataFrame(dados)
            st.dataframe(df_fornecedores, use_container_width=True, hide_index=True)
        else:
            st.info("Sem dados de fornecedores")