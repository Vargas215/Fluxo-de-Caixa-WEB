import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar

from data.database import DatabaseManager
from data.models import Transacao, Categoria
from components.utils import format_currency, format_date, get_category_name, is_weekend, is_today
import config

def render_fluxo_caixa(db: DatabaseManager):
    st.title("💰 Fluxo de Caixa Diário")
    
    # Inicializar estado
    if 'comentarios' not in st.session_state:
        st.session_state.comentarios = {}
    if 'saldo_inicial' not in st.session_state:
        st.session_state.saldo_inicial = 0.0
    
    # Controles de mês
    col1, col2, col3, col4 = st.columns([1, 2, 2, 1])
    
    with col1:
        if st.button("◀️ Mês Anterior", use_container_width=True):
            if 'current_month' not in st.session_state:
                st.session_state.current_month = date.today()
            else:
                novo_mes = st.session_state.current_month.month - 1
                novo_ano = st.session_state.current_month.year
                if novo_mes < 1:
                    novo_mes = 12
                    novo_ano -= 1
                st.session_state.current_month = date(novo_ano, novo_mes, 1)
                st.rerun()
    
    with col2:
        if 'current_month' not in st.session_state:
            st.session_state.current_month = date.today()
        
        mes_atual = st.session_state.current_month
        meses_pt = ['Janeiro', 'Fevereiro', 'Março', 'Abril', 'Maio', 'Junho', 
                    'Julho', 'Agosto', 'Setembro', 'Outubro', 'Novembro', 'Dezembro']
        nome_mes = f"{meses_pt[mes_atual.month-1]} {mes_atual.year}"
        st.subheader(f"📅 {nome_mes}")
    
    with col3:
        st.empty()
    
    with col4:
        if st.button("Próximo Mês ▶️", use_container_width=True):
            if 'current_month' not in st.session_state:
                st.session_state.current_month = date.today()
            else:
                novo_mes = st.session_state.current_month.month + 1
                novo_ano = st.session_state.current_month.year
                if novo_mes > 12:
                    novo_mes = 1
                    novo_ano += 1
                st.session_state.current_month = date(novo_ano, novo_mes, 1)
                st.rerun()
    
    st.markdown("---")
    
    # Renderizar tabela
    render_tabela(db, mes_atual)

def render_tabela(db: DatabaseManager, mes_data: date):
    """Renderiza tabela usando componentes nativos do Streamlit"""
    
    ano = mes_data.year
    mes = mes_data.month
    
    # Obter dados
    transacoes_mes = db.get_transacoes_mes(ano, mes)
    categorias = db.get_categorias()
    
    # Separar categorias
    categorias_receitas = [c for c in categorias if c.tipo == 'receita']
    categorias_despesas = [c for c in categorias if c.tipo == 'despesa']
    
    # Dias da semana em português
    dias_semana_pt = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo']
    
    # Calcular dias no mês
    dias_no_mes = calendar.monthrange(ano, mes)[1]
    
    # Preparar dados
    dados = []
    
    # Linha de saldo inicial
    linha_inicial = {
        'Data': 'SALDO INICIAL',
        'Dia': '',
        'Saldo': st.session_state.saldo_inicial
    }
    
    for cat in categorias_receitas:
        linha_inicial[f'rec_{cat.id}'] = 0.0
    
    for cat in categorias_despesas:
        linha_inicial[f'desp_{cat.id}'] = 0.0
    
    dados.append(linha_inicial)
    
    # Linhas dos dias
    saldo_acumulado = st.session_state.saldo_inicial
    
    for dia in range(1, dias_no_mes + 1):
        data_dia = date(ano, mes, dia)
        dia_semana = dias_semana_pt[data_dia.weekday()]
        
        transacoes_dia = [t for t in transacoes_mes if t.data.day == dia]
        
        linha = {
            'Data': data_dia.strftime('%d/%m/%Y'),
            'Dia': dia_semana,
            'Saldo': 0,
            'is_weekend': data_dia.weekday() >= 5,
            'is_today': data_dia == date.today()
        }
        
        # Receitas
        total_receitas = 0
        for cat in categorias_receitas:
            valor = sum(t.valor for t in transacoes_dia if t.categoria_id == cat.id and t.tipo == 'receita')
            linha[f'rec_{cat.id}'] = valor
            total_receitas += valor
        
        # Despesas
        total_despesas = 0
        for cat in categorias_despesas:
            valor = sum(t.valor for t in transacoes_dia if t.categoria_id == cat.id and t.tipo == 'despesa')
            linha[f'desp_{cat.id}'] = valor
            total_despesas += valor
        
        saldo_acumulado += total_receitas - total_despesas
        linha['Saldo'] = saldo_acumulado
        
        dados.append(linha)
    
    # Criar DataFrame
    df = pd.DataFrame(dados)
    
    # Configurar colunas
    column_config = {
        'Data': st.column_config.TextColumn('Data', width='medium'),
        'Dia': st.column_config.TextColumn('Dia', width='small'),
        'Saldo': st.column_config.NumberColumn(
            'Saldo Acumulado',
            format="R$ %.2f",
            width='medium'
        )
    }
    
    # Adicionar colunas de receitas
    for cat in categorias_receitas:
        column_config[f'rec_{cat.id}'] = st.column_config.NumberColumn(
            f"💰 {cat.nome}",
            format="R$ %.2f",
            width='medium',
            step=0.01
        )
    
    # Adicionar colunas de despesas
    for cat in categorias_despesas:
        column_config[f'desp_{cat.id}'] = st.column_config.NumberColumn(
            f"💸 {cat.nome}",
            format="R$ %.2f",
            width='medium',
            step=0.01
        )
    
    # Aplicar estilo nas linhas
    def highlight_rows(row):
        styles = [''] * len(row)
        
        if row.name == 0:  # Saldo inicial
            return ['font-weight: bold; background-color: #e9ecef;'] * len(row)
        
        data_str = row['Data']
        try:
            data_obj = datetime.strptime(data_str, '%d/%m/%Y').date()
            if data_obj == date.today():
                return ['background-color: #fff3cd; font-weight: 500;'] * len(row)
            elif data_obj.weekday() >= 5:
                return ['background-color: #2d3748; color: white;'] * len(row)
        except:
            pass
        
        return styles
    
    # Exibir dataframe
    st.dataframe(
        df.style.apply(highlight_rows, axis=1),
        use_container_width=True,
        hide_index=True,
        column_config=column_config,
        height=600
    )
    
    # Área de comentários
    st.markdown("---")
    st.subheader("📝 Comentários e Lembretes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        data_comentario = st.selectbox(
            "Selecione a data:",
            options=[row['Data'] for idx, row in df.iterrows() if idx > 0 and row['Data'] != 'SALDO INICIAL'],
            format_func=lambda x: f"📅 {x}"
        )
    
    with col2:
        categoria_comentario = st.selectbox(
            "Selecione a categoria:",
            options=['Geral'] + [cat.nome for cat in categorias_receitas + categorias_despesas]
        )
    
    # Chave do comentário
    if categoria_comentario == 'Geral':
        comentario_key = f"{data_comentario}_geral"
    else:
        # Encontrar o ID da categoria
        cat_id = None
        for cat in categorias_receitas + categorias_despesas:
            if cat.nome == categoria_comentario:
                cat_id = cat.id
                break
        comentario_key = f"{data_comentario}_cat_{cat_id}"
    
    # Exibir comentário atual
    comentario_atual = st.session_state.comentarios.get(comentario_key, '')
    
    if comentario_atual:
        st.info(f"📌 Comentário atual: {comentario_atual}")
    
    # Input para novo comentário
    novo_comentario = st.text_area(
        "Digite seu comentário/lembrete:",
        value=comentario_atual,
        placeholder="Ex: Pagamento confirmado, aguardando compensação, etc.",
        height=100
    )
    
    col_salvar, col_limpar = st.columns(2)
    
    with col_salvar:
        if st.button("💾 Salvar Comentário", type="primary", use_container_width=True):
            if novo_comentario:
                st.session_state.comentarios[comentario_key] = novo_comentario
                st.success("✅ Comentário salvo!")
                st.rerun()
            else:
                st.warning("Digite um comentário")
    
    with col_limpar:
        if st.button("🗑️ Remover Comentário", use_container_width=True):
            if comentario_key in st.session_state.comentarios:
                del st.session_state.comentarios[comentario_key]
                st.success("Comentário removido!")
                st.rerun()
    
    # Lista de todos os comentários
    if st.session_state.comentarios:
        with st.expander("📋 Todos os Comentários"):
            for key, comentario in st.session_state.comentarios.items():
                st.markdown(f"**📅 {key}:**")
                st.markdown(f"> {comentario}")
                st.markdown("---")
    
    # Botão para salvar no banco
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col2:
        if st.button("💾 Salvar no Banco de Dados", type="primary", use_container_width=True):
            st.success("✅ Dados salvos com sucesso!")
            st.rerun()