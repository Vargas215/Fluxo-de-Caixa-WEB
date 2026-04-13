import streamlit as st
import pandas as pd
from datetime import datetime, date
from data.database import DatabaseManager
from data.models import Transacao, Categoria
from components.utils import format_currency, format_date, get_category_name
import config

def render_lancamentos(db: DatabaseManager):
    st.title("📋 Lançamentos")
    
    # Filtros
    with st.container(border=True):
        col1, col2, col3, col4 = st.columns([2, 1, 1, 1])
        
        with col1:
            busca = st.text_input("🔍 Buscar lançamentos...", placeholder="Digite cliente, categoria ou valor")
        
        with col2:
            tipo_filtro = st.selectbox(
                "Tipo",
                ["Todos", "Receita", "Despesa"],
                index=0
            )
        
        with col3:
            status_filtro = st.selectbox(
                "Status",
                ["Todos", "Pago", "Pendente"],
                index=0
            )
        
        with col4:
            st.write("")  # Espaçador
            if st.button("🔍 Filtrar", use_container_width=True):
                st.rerun()
    
    # Botão para novo lançamento
    if st.button("➕ Novo Lançamento", type="primary"):
        st.session_state.novo_lancamento = True
    
    # Obter todos os lançamentos
    transacoes = db.get_transacoes()
    
    # Aplicar filtros
    if busca:
        transacoes = filtrar_por_busca(transacoes, busca, db)
    
    if tipo_filtro != "Todos":
        transacoes = [t for t in transacoes if t.tipo == tipo_filtro.lower()]
    
    if status_filtro != "Todos":
        transacoes = [t for t in transacoes if t.status.lower() == status_filtro.lower()]
    
    # Ordenar por data (mais recente primeiro)
    transacoes = sorted(transacoes, key=lambda x: x.data, reverse=True)
    
    # Exibir contador
    st.caption(f"📊 Total de {len(transacoes)} lançamentos encontrados")
    
    # Tabela de lançamentos
    if transacoes:
        render_tabela_lancamentos(transacoes, db)
    else:
        st.info("📭 Nenhum lançamento encontrado com os filtros aplicados.")
    
    # Modal para novo lançamento (se acionado)
    if 'novo_lancamento' in st.session_state and st.session_state.novo_lancamento:
        render_modal_novo_lancamento(db)

def filtrar_por_busca(transacoes, busca, db):
    """Filtra transações com base na busca"""
    resultados = []
    busca = busca.lower()
    
    for t in transacoes:
        # Buscar por cliente
        if t.cliente and busca in t.cliente.lower():
            resultados.append(t)
            continue
        
        # Buscar por categoria
        categoria = db.get_categoria(t.categoria_id)
        if categoria and busca in categoria.nome.lower():
            resultados.append(t)
            continue
        
        # Buscar por valor
        if busca.replace(',', '.').replace('r$', '').strip().isdigit():
            valor_busca = float(busca.replace(',', '.').replace('r$', '').strip())
            if abs(t.valor - valor_busca) < 0.01:
                resultados.append(t)
                continue
        
        # Buscar por tipo
        if busca in t.tipo.lower():
            resultados.append(t)
            continue
    
    return resultados

def render_tabela_lancamentos(transacoes, db):
    """Renderiza tabela de lançamentos"""
    
    # Preparar dados para a tabela
    dados = []
    for t in transacoes:
        categoria = db.get_categoria(t.categoria_id)
        
        dados.append({
            'ID': t.id,
            'Data': t.data.strftime('%d/%m/%Y'),
            'Tipo': '💰 Receita' if t.tipo == 'receita' else '💸 Despesa',
            'Categoria': categoria.nome if categoria else 'N/A',
            'Cliente/Fornecedor': t.cliente or '-',
            'Valor': t.valor,
            'Status': t.status,
            'Ações': t.id
        })
    
    # Criar DataFrame
    df = pd.DataFrame(dados)
    
    # Configurar colunas
    column_config = {
        'ID': st.column_config.NumberColumn('ID', width='small'),
        'Data': st.column_config.TextColumn('Data', width='small'),
        'Tipo': st.column_config.TextColumn('Tipo', width='small'),
        'Categoria': st.column_config.TextColumn('Categoria', width='medium'),
        'Cliente/Fornecedor': st.column_config.TextColumn('Cliente/Fornecedor', width='large'),
        'Valor': st.column_config.NumberColumn('Valor', format="R$ %.2f", width='medium'),
        'Status': st.column_config.TextColumn('Status', width='small'),
        'Ações': st.column_config.Column('Ações', width='medium')
    }
    
    # Exibir tabela
    st.dataframe(
        df,
        use_container_width=True,
        hide_index=True,
        column_config=column_config,
        height=500
    )
    
    # Adicionar botões de ação para cada linha
    for t in transacoes:
        with st.expander(f"Ações para Lançamento #{t.id}", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                if st.button(f"✏️ Editar #{t.id}", key=f"edit_{t.id}", use_container_width=True):
                    st.session_state.editar_lancamento_id = t.id
                    st.rerun()
            
            with col2:
                if st.button(f"👁️ Detalhes #{t.id}", key=f"view_{t.id}", use_container_width=True):
                    mostrar_detalhes_lancamento(t, db)
            
            with col3:
                if st.button(f"🗑️ Excluir #{t.id}", key=f"delete_{t.id}", use_container_width=True, type="secondary"):
                    confirmar_exclusao(t.id, db)

def mostrar_detalhes_lancamento(transacao, db):
    """Mostra detalhes de um lançamento"""
    categoria = db.get_categoria(transacao.categoria_id)
    
    with st.container(border=True):
        st.subheader(f"📋 Detalhes do Lançamento #{transacao.id}")
        
        col1, col2 = st.columns(2)
        
        with col1:
            st.write(f"**Data:** {format_date(transacao.data)}")
            st.write(f"**Tipo:** {'Receita' if transacao.tipo == 'receita' else 'Despesa'}")
            st.write(f"**Categoria:** {categoria.nome if categoria else 'N/A'}")
            st.write(f"**Cliente/Fornecedor:** {transacao.cliente or '-'}")
        
        with col2:
            st.write(f"**Valor:** {format_currency(transacao.valor)}")
            st.write(f"**Status:** {transacao.status.capitalize()}")
            st.write(f"**Data de Criação:** {format_date(transacao.data_criacao.date())}")
            st.write(f"**Origem:** {transacao.origem.capitalize()}")

def confirmar_exclusao(transacao_id, db):
    """Confirma exclusão de um lançamento"""
    st.warning(f"⚠️ Tem certeza que deseja excluir o lançamento #{transacao_id}?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button(f"✅ Sim, excluir #{transacao_id}", type="primary", use_container_width=True):
            if db.delete_transacao(transacao_id):
                st.success(f"✅ Lançamento #{transacao_id} excluído com sucesso!")
                st.rerun()
            else:
                st.error(f"❌ Erro ao excluir lançamento #{transacao_id}")
    
    with col2:
        if st.button(f"❌ Cancelar", use_container_width=True):
            st.rerun()

def render_modal_novo_lancamento(db):
    """Renderiza modal para novo lançamento"""
    st.subheader("➕ Novo Lançamento")
    
    with st.form(key="form_novo_lancamento", border=True):
        col1, col2 = st.columns(2)
        
        with col1:
            tipo = st.selectbox(
                "Tipo *",
                ["receita", "despesa"],
                format_func=lambda x: "Receita" if x == "receita" else "Despesa"
            )
            
            data_lancamento = st.date_input("Data *", value=date.today())
            
            # Obter categorias baseadas no tipo
            categorias = db.get_categorias()
            categorias_filtradas = [c for c in categorias if c.tipo == tipo]
            
            if not categorias_filtradas:
                st.error("Nenhuma categoria disponível para este tipo!")
                categoria_id = None
            else:
                categoria_id = st.selectbox(
                    "Categoria *",
                    options=[c.id for c in categorias_filtradas],
                    format_func=lambda x: next((c.nome for c in categorias_filtradas if c.id == x), "")
                )
        
        with col2:
            cliente = st.text_input("Cliente/Fornecedor", placeholder="Opcional")
            
            valor = st.number_input(
                "Valor (R$) *",
                min_value=0.01,
                step=0.01,
                format="%.2f"
            )
            
            status = st.selectbox(
                "Status",
                ["pago", "pendente"],
                format_func=lambda x: "Pago" if x == "pago" else "Pendente"
            )
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            submit = st.form_submit_button("💾 Salvar Lançamento", type="primary", use_container_width=True)
        
        with col_btn2:
            cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
        
        if submit:
            if not categoria_id:
                st.error("Selecione uma categoria!")
            else:
                nova_transacao = Transacao(
                    id=0,
                    tipo=tipo,
                    data=data_lancamento,
                    categoria_id=categoria_id,
                    cliente=cliente if cliente else None,
                    valor=valor,
                    status=status,
                    origem='manual'
                )
                
                novo_id = db.add_transacao(nova_transacao)
                st.success(f"✅ Lançamento #{novo_id} criado com sucesso!")
                st.session_state.novo_lancamento = False
                st.rerun()
        
        if cancel:
            st.session_state.novo_lancamento = False
            st.rerun()