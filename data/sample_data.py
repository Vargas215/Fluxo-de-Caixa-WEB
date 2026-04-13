from data.models import Transacao, Usuario, Categoria
from datetime import datetime, date, timedelta
import random

# Usuários padrão
DEFAULT_USERS = [
    Usuario(
        id=1,
        nome="Administrador",
        username="admin",
        senha="admin123",
        role="admin",
        permissao={
            'dashboard': True,
            'fluxo_caixa': True,
            'lancamentos': True,
            'relatorios': True,
            'configuracoes': True,
            'nova_receita': True,
            'nova_despesa': True,
            'todas_categorias': True
        },
        ativo=True,
        data_criacao=datetime.now()
    ),
    Usuario(
        id=2,
        nome="Financeiro",
        username="financeiro",
        senha="fin123",
        role="financeiro",
        permissao={
            'dashboard': True,
            'fluxo_caixa': True,
            'lancamentos': True,
            'relatorios': True,
            'configuracoes': True,
            'nova_receita': True,
            'nova_despesa': True,
            'todas_categorias': True
        },
        ativo=True,
        data_criacao=datetime.now()
    ),
    Usuario(
        id=3,
        nome="Fiscal",
        username="fiscal",
        senha="fis123",
        role="fiscal",
        permissao={
            'dashboard': True,
            'fluxo_caixa': False,
            'lancamentos': True,
            'relatorios': False,
            'configuracoes': False,
            'nova_receita': False,
            'nova_despesa': True,
            'todas_categorias': False,
            'categorias_permitidas': [114, 115, 116, 117]
        },
        ativo=True,
        data_criacao=datetime.now()
    )
]

# Categorias padrão (as mesmas do seu sistema original)
DEFAULT_CATEGORIES = [
    # Receitas
    Categoria(id=1, nome="Retail", tipo="receita", cor="#2ecc71"),
    Categoria(id=2, nome="Grandes Contas", tipo="receita", cor="#27ae60"),
    Categoria(id=3, nome="Maquinas KFB", tipo="receita", cor="#229954"),
    Categoria(id=4, nome="Máquinas Log Max", tipo="receita", cor="#1e8449"),
    Categoria(id=5, nome="Empréstimo Entrada", tipo="receita", cor="#145a32"),
    
    # Despesas
    Categoria(id=101, nome="Fornecedores Nacionais", tipo="despesa", cor="#e74c3c"),
    Categoria(id=102, nome="Fornecedores Importação", tipo="despesa", cor="#c0392b"),
    Categoria(id=103, nome="Fornecedores Intercompany", tipo="despesa", cor="#922b21"),
    Categoria(id=104, nome="KDB", tipo="despesa", cor="#641e16"),
    Categoria(id=105, nome="KBI", tipo="despesa", cor="#e74c3c"),
    Categoria(id=106, nome="KFAB", tipo="despesa", cor="#c0392b"),
    Categoria(id=107, nome="Log Max", tipo="despesa", cor="#922b21"),
    Categoria(id=108, nome="Quadco", tipo="despesa", cor="#641e16"),
    Categoria(id=109, nome="TimberPro", tipo="despesa", cor="#e74c3c"),
    Categoria(id=110, nome="Braccke", tipo="despesa", cor="#c0392b"),
    Categoria(id=111, nome="Southstar", tipo="despesa", cor="#922b21"),
    Categoria(id=112, nome="Komatsu America", tipo="despesa", cor="#641e16"),
    Categoria(id=113, nome="Outros Intercompany", tipo="despesa", cor="#e74c3c"),
    Categoria(id=114, nome="Impostos Faturamento", tipo="despesa", cor="#c0392b"),
    Categoria(id=115, nome="Impostos sobre Importação Komatsu", tipo="despesa", cor="#922b21"),
    Categoria(id=116, nome="Impostos sobre Importação Log Max", tipo="despesa", cor="#641e16"),
    Categoria(id=117, nome="Outros impostos e taxas", tipo="despesa", cor="#e74c3c"),
    Categoria(id=118, nome="RH", tipo="despesa", cor="#c0392b"),
    Categoria(id=119, nome="Despesas Financeiras", tipo="despesa", cor="#922b21"),
    Categoria(id=120, nome="Hedge Cambial", tipo="despesa", cor="#641e16"),
    Categoria(id=121, nome="Despesas Bancárias", tipo="despesa", cor="#e74c3c"),
    Categoria(id=122, nome="JCP/Dividendos - KFAB", tipo="despesa", cor="#c0392b"),
    Categoria(id=123, nome="JCP/Dividendos - KBI", tipo="despesa", cor="#922b21"),
    Categoria(id=124, nome="Empréstimo Saída", tipo="despesa", cor="#641e16"),
    Categoria(id=125, nome="Juros", tipo="despesa", cor="#e74c3c")
]

# Dados de exemplo
def generate_sample_transactions(count=50):
    """Gera transações de exemplo"""
    transactions = []
    
    # Clientes e fornecedores de exemplo
    clientes = ["Cliente A", "Cliente B", "Cliente C", "Cliente D", "Cliente E"]
    fornecedores = ["Fornecedor X", "Fornecedor Y", "Fornecedor Z"]
    
    # Data inicial (últimos 90 dias)
    start_date = date.today() - timedelta(days=90)
    
    for i in range(count):
        # Tipo aleatório (70% receitas, 30% despesas)
        tipo = "receita" if random.random() < 0.7 else "despesa"
        
        # Data aleatória nos últimos 90 dias
        days_offset = random.randint(0, 90)
        trans_date = start_date + timedelta(days=days_offset)
        
        # Selecionar categoria baseada no tipo
        if tipo == "receita":
            categoria_id = random.choice([1, 2, 3, 4, 5])
            cliente = random.choice(clientes)
        else:
            categoria_id = random.choice([101, 102, 103, 114, 115, 116, 117, 118])
            cliente = random.choice(fornecedores)
        
        # Valor aleatório (entre 1000 e 50000 para receitas, 100 e 20000 para despesas)
        if tipo == "receita":
            valor = round(random.uniform(1000, 50000), 2)
        else:
            valor = round(random.uniform(100, 20000), 2)
        
        # Status (80% pago, 20% pendente)
        status = "pago" if random.random() < 0.8 else "pendente"
        
        transaction = Transacao(
            id=i + 1,
            tipo=tipo,
            data=trans_date,
            categoria_id=categoria_id,
            cliente=cliente,
            valor=valor,
            status=status,
            data_criacao=datetime.now() - timedelta(days=random.randint(1, 30)),
            origem="exemplo"
        )
        
        transactions.append(transaction)
    
    return transactions

SAMPLE_TRANSACTIONS = generate_sample_transactions(50)