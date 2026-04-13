import os
from datetime import datetime
import json
from pathlib import Path

# Configurações do sistema
APP_CONFIG = {
    'app_name': 'Sistema Financeiro - Fluxo de Caixa',
    'app_version': '2.1.0',
    'default_currency': 'BRL',
    'date_format': '%d/%m/%Y',
    'data_dir': Path('./data'),
    'db_file': 'financeiro.db',
    'backup_dir': Path('./backups'),
    'company_name': 'Sua Empresa',
    'company_logo': '💰'
}

# Cores do sistema
COLORS = {
    'primary': '#667eea',
    'secondary': '#764ba2',
    'success': '#27ae60',
    'danger': '#e74c3c',
    'warning': '#f39c12',
    'info': '#17a2b8',
    'receita': '#2ecc71',
    'despesa': '#e74c3c'
}

# Categorias padrão
DEFAULT_CATEGORIES = {
    'receitas': [
        {'id': 1, 'nome': 'Retail', 'cor': '#2ecc71'},
        {'id': 2, 'nome': 'Grandes Contas', 'cor': '#27ae60'},
        {'id': 3, 'nome': 'Maquinas KFB', 'cor': '#229954'},
        {'id': 4, 'nome': 'Máquinas Log Max', 'cor': '#1e8449'},
        {'id': 5, 'nome': 'Empréstimo Entrada', 'cor': '#145a32'}
    ],
    'despesas': [
        {'id': 101, 'nome': 'Fornecedores Nacionais', 'cor': '#e74c3c'},
        {'id': 102, 'nome': 'Fornecedores Importação', 'cor': '#c0392b'},
        {'id': 103, 'nome': 'Fornecedores Intercompany', 'cor': '#922b21'},
        {'id': 104, 'nome': 'KDB', 'cor': '#641e16'},
        {'id': 105, 'nome': 'KBI', 'cor': '#e74c3c'},
        {'id': 106, 'nome': 'KFAB', 'cor': '#c0392b'},
        {'id': 107, 'nome': 'Log Max', 'cor': '#922b21'},
        {'id': 108, 'nome': 'Quadco', 'cor': '#641e16'},
        {'id': 109, 'nome': 'TimberPro', 'cor': '#e74c3c'},
        {'id': 110, 'nome': 'Braccke', 'cor': '#c0392b'},
        {'id': 111, 'nome': 'Southstar', 'cor': '#922b21'},
        {'id': 112, 'nome': 'Komatsu America', 'cor': '#641e16'},
        {'id': 113, 'nome': 'Outros Intercompany', 'cor': '#e74c3c'},
        {'id': 114, 'nome': 'Impostos Faturamento', 'cor': '#c0392b'},
        {'id': 115, 'nome': 'Impostos sobre Importação Komatsu', 'cor': '#922b21'},
        {'id': 116, 'nome': 'Impostos sobre Importação Log Max', 'cor': '#641e16'},
        {'id': 117, 'nome': 'Outros impostos e taxas', 'cor': '#e74c3c'},
        {'id': 118, 'nome': 'RH', 'cor': '#c0392b'},
        {'id': 119, 'nome': 'Despesas Financeiras', 'cor': '#922b21'},
        {'id': 120, 'nome': 'Hedge Cambial', 'cor': '#641e16'},
        {'id': 121, 'nome': 'Despesas Bancárias', 'cor': '#e74c3c'},
        {'id': 122, 'nome': 'JCP/Dividendos - KFAB', 'cor': '#c0392b'},
        {'id': 123, 'nome': 'JCP/Dividendos - KBI', 'cor': '#922b21'},
        {'id': 124, 'nome': 'Empréstimo Saída', 'cor': '#641e16'},
        {'id': 125, 'nome': 'Juros', 'cor': '#e74c3c'}
    ]
}

# Permissões de usuário com ícones
USER_ROLES = {
    'admin': {
        'nome': 'Administrador',
        'icone': '👑',
        'permissoes': {
            'dashboard': True,
            'fluxo_caixa': True,
            'lancamentos': True,
            'relatorios': True,
            'configuracoes': True,
            'nova_receita': True,
            'nova_despesa': True,
            'todas_categorias': True
        }
    },
    'financeiro': {
        'nome': 'Financeiro',
        'icone': '💰',
        'permissoes': {
            'dashboard': True,
            'fluxo_caixa': True,
            'lancamentos': True,
            'relatorios': True,
            'configuracoes': True,
            'nova_receita': True,
            'nova_despesa': True,
            'todas_categorias': True
        }
    },
    'fiscal': {
        'nome': 'Fiscal',
        'icone': '📋',
        'permissoes': {
            'dashboard': True,
            'fluxo_caixa': False,
            'lancamentos': True,
            'relatorios': False,
            'configuracoes': False,
            'nova_receita': False,
            'nova_despesa': True,
            'todas_categorias': False,
            'categorias_permitidas': [114, 115, 116, 117]
        }
    },
    'gerente': {
        'nome': 'Gerente',
        'icone': '👔',
        'permissoes': {
            'dashboard': True,
            'fluxo_caixa': True,
            'lancamentos': True,
            'relatorios': True,
            'configuracoes': False,
            'nova_receita': True,
            'nova_despesa': True,
            'todas_categorias': True
        }
    },
    'operacional': {
        'nome': 'Operacional',
        'icone': '⚙️',
        'permissoes': {
            'dashboard': True,
            'fluxo_caixa': True,
            'lancamentos': False,
            'relatorios': False,
            'configuracoes': False,
            'nova_receita': False,
            'nova_despesa': False,
            'todas_categorias': False
        }
    }
}