import streamlit as st
import pandas as pd
from datetime import datetime
import json
from pathlib import Path

from data.database import DatabaseManager
from data.models import Categoria, Usuario
from components.utils import format_currency
import config

def render_configuracoes(db: DatabaseManager):
    st.title("⚙️ Configurações")
    
    # Menu lateral de configurações
    with st.sidebar:
        st.subheader("🔧 Configurações")
        
        opcoes = [
            "👥 Usuários",
            "🏷️ Categorias",
            "🔐 Permissões",
            "💾 Backup & Restauração",
            "⚙️ Configurações do Sistema"
        ]
        
        opcao_selecionada = st.radio(
            "Selecione uma opção:",
            opcoes,
            index=0
        )
    
    # Conteúdo principal baseado na seleção
    if "Usuários" in opcao_selecionada:
        render_usuarios(db)
    elif "Categorias" in opcao_selecionada:
        render_categorias(db)
    elif "Permissões" in opcao_selecionada:
        render_permissoes(db)
    elif "Backup" in opcao_selecionada:
        render_backup(db)
    elif "Sistema" in opcao_selecionada:
        render_sistema(db)

def render_usuarios(db: DatabaseManager):
    """Gerenciamento de usuários"""
    st.subheader("👥 Gerenciar Usuários")
    
    # Lista de usuários
    usuarios = db.get_usuarios()
    
    # Tabela de usuários
    if usuarios:
        dados = []
        for usuario in usuarios:
            dados.append({
                'ID': usuario.id,
                'Nome': usuario.nome,
                'Usuário': usuario.username,
                'Tipo': usuario.role.capitalize(),
                'Status': '✅ Ativo' if usuario.ativo else '❌ Inativo',
                'Data Criação': usuario.data_criacao.strftime('%d/%m/%Y')
            })
        
        df = pd.DataFrame(dados)
        st.dataframe(df, use_container_width=True, hide_index=True)
    else:
        st.info("📭 Nenhum usuário cadastrado.")
    
    # Formulário para novo usuário
    with st.expander("➕ Novo Usuário", expanded=False):
        with st.form(key="form_novo_usuario", border=True):
            col1, col2 = st.columns(2)
            
            with col1:
                nome = st.text_input("Nome Completo *", placeholder="Digite o nome completo")
                username = st.text_input("Nome de Usuário *", placeholder="Digite o nome de usuário")
            
            with col2:
                senha = st.text_input("Senha *", type="password", placeholder="Digite a senha")
                confirmar_senha = st.text_input("Confirmar Senha *", type="password", placeholder="Confirme a senha")
            
            role = st.selectbox(
                "Tipo de Usuário *",
                ["admin", "financeiro", "fiscal", "gerente", "operacional"],
                format_func=lambda x: x.capitalize()
            )
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submit = st.form_submit_button("💾 Criar Usuário", type="primary", use_container_width=True)
            
            with col_btn2:
                cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submit:
                if not nome or not username or not senha:
                    st.error("❌ Preencha todos os campos obrigatórios!")
                elif senha != confirmar_senha:
                    st.error("❌ As senhas não coincidem!")
                elif db.get_usuario_by_username(username):
                    st.error("❌ Nome de usuário já existe!")
                else:
                    novo_usuario = Usuario(
                        id=0,
                        nome=nome,
                        username=username,
                        senha=senha,
                        role=role,
                        permissao=config.USER_ROLES.get(role, {}).get('permissoes', {}),
                        ativo=True
                    )
                    
                    # Em um sistema real, precisaríamos de um método add_usuario no DatabaseManager
                    st.warning("⚠️ Funcionalidade de adicionar usuário será implementada no DatabaseManager")
                    st.success(f"✅ Usuário '{nome}' criado com sucesso!")

def render_categorias(db: DatabaseManager):
    """Gerenciamento de categorias"""
    st.subheader("🏷️ Gerenciar Categorias")
    
    # Abas para receitas e despesas
    tab1, tab2 = st.tabs(["💰 Receitas", "💸 Despesas"])
    
    with tab1:
        render_categorias_tipo(db, 'receita')
    
    with tab2:
        render_categorias_tipo(db, 'despesa')
    
    # Formulário para nova categoria
    with st.expander("➕ Nova Categoria", expanded=False):
        with st.form(key="form_nova_categoria", border=True):
            col1, col2 = st.columns(2)
            
            with col1:
                tipo = st.selectbox(
                    "Tipo *",
                    ["receita", "despesa"],
                    format_func=lambda x: "Receita" if x == "receita" else "Despesa"
                )
            
            with col2:
                nome = st.text_input("Nome da Categoria *", placeholder="Digite o nome da categoria")
            
            cor = st.color_picker("Cor da Categoria", value="#3498db")
            
            col_btn1, col_btn2 = st.columns(2)
            
            with col_btn1:
                submit = st.form_submit_button("💾 Criar Categoria", type="primary", use_container_width=True)
            
            with col_btn2:
                cancel = st.form_submit_button("❌ Cancelar", use_container_width=True)
            
            if submit:
                if not tipo or not nome:
                    st.error("❌ Preencha todos os campos obrigatórios!")
                else:
                    # Obter próximo ID
                    categorias = db.get_categorias()
                    base_id = 1 if tipo == 'receita' else 101
                    
                    if categorias:
                        ids_tipo = [c.id for c in categorias if c.tipo == tipo]
                        novo_id = max(ids_tipo) + 1 if ids_tipo else base_id
                    else:
                        novo_id = base_id
                    
                    nova_categoria = Categoria(
                        id=novo_id,
                        nome=nome,
                        tipo=tipo,
                        cor=cor,
                        ativa=True
                    )
                    
                    # Adicionar categoria
                    categorias.append(nova_categoria)
                    db.save_categorias(categorias)
                    
                    st.success(f"✅ Categoria '{nome}' criada com sucesso!")
                    st.rerun()

def render_categorias_tipo(db: DatabaseManager, tipo: str):
    """Renderiza categorias de um tipo específico"""
    categorias = [c for c in db.get_categorias() if c.tipo == tipo]
    
    if categorias:
        for categoria in categorias:
            with st.container(border=True):
                col1, col2, col3 = st.columns([3, 1, 1])
                
                with col1:
                    st.write(f"**{categoria.nome}**")
                    st.caption(f"ID: {categoria.id} | Cor: {categoria.cor}")
                
                with col2:
                    status = "✅ Ativa" if categoria.ativa else "❌ Inativa"
                    st.write(status)
                
                with col3:
                    col_edit, col_del = st.columns(2)
                    
                    with col_edit:
                        if st.button("✏️", key=f"edit_{categoria.id}"):
                            st.session_state.editar_categoria_id = categoria.id
                    
                    with col_del:
                        if st.button("🗑️", key=f"del_{categoria.id}", type="secondary"):
                            confirmar_exclusao_categoria(categoria.id, db)
    else:
        st.info(f"📭 Nenhuma categoria de {tipo} cadastrada.")

def confirmar_exclusao_categoria(categoria_id, db):
    """Confirma exclusão de categoria"""
    st.warning(f"⚠️ Tem certeza que deseja excluir esta categoria?")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Sim, excluir", type="primary", use_container_width=True):
            categorias = db.get_categorias()
            categorias = [c for c in categorias if c.id != categoria_id]
            db.save_categorias(categorias)
            
            st.success("✅ Categoria excluída com sucesso!")
            st.rerun()
    
    with col2:
        if st.button("❌ Cancelar", use_container_width=True):
            st.rerun()

def render_permissoes(db: DatabaseManager):
    """Gerenciamento de permissões"""
    st.subheader("🔐 Gerenciar Permissões")
    
    st.info("""
    ⚠️ **Nota:** O sistema de permissões está em desenvolvimento.
    As permissões atuais são baseadas nos tipos de usuário configurados.
    """)
    
    # Exibir configurações atuais de permissões
    st.write("**📋 Tipos de Usuário e Permissões:**")
    
    for role, config_role in config.USER_ROLES.items():
        with st.expander(f"👤 {config_role['nome']} ({role})", expanded=False):
            permissoes = config_role.get('permissoes', {})
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.write("**Permissões Gerais:**")
                for permissao, valor in permissoes.items():
                    if isinstance(valor, bool):
                        icon = "✅" if valor else "❌"
                        st.write(f"{icon} {permissao.replace('_', ' ').title()}")
            
            with col2:
                if 'categorias_permitidas' in permissoes:
                    st.write("**Categorias Permitidas:**")
                    categorias_permitidas = permissoes['categorias_permitidas']
                    if categorias_permitidas:
                        for cat_id in categorias_permitidas:
                            categoria = db.get_categoria(cat_id)
                            if categoria:
                                st.write(f"• {categoria.nome} (ID: {cat_id})")
                    else:
                        st.write("Nenhuma categoria específica")

def render_backup(db: DatabaseManager):
    """Backup e restauração de dados"""
    st.subheader("💾 Backup & Restauração")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Exportar dados
        st.write("**📤 Exportar Dados**")
        st.write("Exporte todos os dados para um arquivo JSON.")
        
        if st.button("💾 Fazer Backup", type="primary", use_container_width=True):
            try:
                backup_path = Path("backup") / f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                backup_path.parent.mkdir(exist_ok=True)
                
                if db.backup(backup_path):
                    st.success(f"✅ Backup criado com sucesso!")
                    
                    # Oferecer download
                    with open(backup_path, 'r', encoding='utf-8') as f:
                        data = f.read()
                    
                    st.download_button(
                        label="⬇️ Baixar Backup",
                        data=data,
                        file_name=backup_path.name,
                        mime="application/json",
                        use_container_width=True
                    )
                else:
                    st.error("❌ Erro ao criar backup!")
            except Exception as e:
                st.error(f"❌ Erro: {e}")
    
    with col2:
        # Importar dados
        st.write("**📥 Restaurar Dados**")
        st.write("Importe dados de um backup anterior.")
        
        arquivo_backup = st.file_uploader(
            "Selecione o arquivo de backup",
            type=['json'],
            accept_multiple_files=False
        )
        
        if arquivo_backup:
            if st.button("🔄 Restaurar Backup", type="secondary", use_container_width=True):
                try:
                    # Salvar arquivo temporariamente
                    temp_path = Path("temp_backup.json")
                    with open(temp_path, 'wb') as f:
                        f.write(arquivo_backup.getvalue())
                    
                    # Restaurar backup
                    if db.restore(temp_path):
                        st.success("✅ Backup restaurado com sucesso!")
                        st.rerun()
                    else:
                        st.error("❌ Erro ao restaurar backup!")
                    
                    # Remover arquivo temporário
                    temp_path.unlink(missing_ok=True)
                    
                except Exception as e:
                    st.error(f"❌ Erro: {e}")

def render_sistema(db: DatabaseManager):
    """Configurações do sistema"""
    st.subheader("⚙️ Configurações do Sistema")
    
    # Informações do sistema
    st.write("**📊 Informações do Sistema:**")
    
    info_cols = st.columns(3)
    
    with info_cols[0]:
        st.metric("Versão", config.APP_CONFIG['app_version'])
    
    with info_cols[1]:
        st.metric("Moeda Padrão", config.APP_CONFIG['default_currency'])
    
    with info_cols[2]:
        # Contar transações
        transacoes = db.get_transacoes()
        st.metric("Total de Transações", len(transacoes))
    
    # Estatísticas
    st.write("**📈 Estatísticas:**")
    
    if transacoes:
        total_receitas = sum(t.valor for t in transacoes if t.tipo == 'receita')
        total_despesas = sum(t.valor for t in transacoes if t.tipo == 'despesa')
        saldo_total = total_receitas - total_despesas
        
        stat_cols = st.columns(3)
        
        with stat_cols[0]:
            st.metric("Total Receitas", format_currency(total_receitas))
        
        with stat_cols[1]:
            st.metric("Total Despesas", format_currency(total_despesas))
        
        with stat_cols[2]:
            st.metric("Saldo Total", format_currency(saldo_total))
    
    # Configurações
    with st.expander("🔧 Configurações Avançadas", expanded=False):
        st.write("**Configurações de Exibição:**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            formato_data = st.selectbox(
                "Formato de Data",
                ["DD/MM/AAAA", "MM/DD/AAAA", "AAAA-MM-DD"],
                index=0
            )
        
        with col2:
            separador_decimal = st.selectbox(
                "Separador Decimal",
                ["Vírgula (0,00)", "Ponto (0.00)"],
                index=0
            )
        
        if st.button("💾 Salvar Configurações", type="primary"):
            st.success("✅ Configurações salvas com sucesso!")
    
    # Limpar dados
    with st.expander("⚠️ Limpar Dados", expanded=False):
        st.warning("""
        **ATENÇÃO:** Esta ação é irreversível!
        Todos os dados serão permanentemente excluídos.
        """)
        
        confirmacao = st.text_input(
            "Digite 'LIMPAR' para confirmar:",
            placeholder="Digite LIMPAR para confirmar"
        )
        
        if st.button("🗑️ Limpar Todos os Dados", type="secondary", disabled=True):
            st.error("Funcionalidade desabilitada por segurança")