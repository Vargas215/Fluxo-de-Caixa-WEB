import streamlit as st
from datetime import datetime, date
from typing import List, Dict, Optional
import pandas as pd

from config import COLORS, USER_ROLES
from data.models import Transacao, Categoria

def format_currency(value: float) -> str:
    """Formata valor como moeda brasileira"""
    if value is None:
        return "R$ 0,00"
    return f"R$ {value:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

def format_date(dt: date) -> str:
    """Formata data no padrão brasileiro"""
    if dt is None:
        return ""
    return dt.strftime("%d/%m/%Y")

def format_datetime(dt: datetime) -> str:
    """Formata datetime no padrão brasileiro"""
    if dt is None:
        return ""
    return dt.strftime("%d/%m/%Y %H:%M:%S")

def get_category_name(categoria_id: int, categorias: List[Categoria]) -> str:
    """Obtém nome da categoria pelo ID"""
    for cat in categorias:
        if cat.id == categoria_id:
            return cat.nome
    return "Categoria não encontrada"

def check_permission(user_role: str, permission: str) -> bool:
    """Verifica se usuário tem permissão"""
    if user_role == 'admin':
        return True
    
    role_config = USER_ROLES.get(user_role, {})
    permissions = role_config.get('permissoes', {})
    return permissions.get(permission, False)

def can_access_category(user_role: str, categoria_id: int) -> bool:
    """Verifica se usuário pode acessar determinada categoria"""
    if user_role == 'admin':
        return True
    
    role_config = USER_ROLES.get(user_role, {})
    permissions = role_config.get('permissoes', {})
    
    if permissions.get('todas_categorias', False):
        return True
    
    allowed_categories = permissions.get('categorias_permitidas', [])
    return categoria_id in allowed_categories

def calculate_totals(transacoes: List[Transacao]) -> Dict[str, float]:
    """Calcula totais de receitas, despesas e saldo"""
    receitas = sum(t.valor for t in transacoes if t.tipo == 'receita')
    despesas = sum(t.valor for t in transacoes if t.tipo == 'despesa')
    saldo = receitas - despesas
    
    return {
        'receitas': receitas,
        'despesas': despesas,
        'saldo': saldo
    }

def calculate_monthly_totals(transacoes: List[Transacao], ano: int, mes: int) -> Dict:
    """Calcula totais por dia do mês"""
    from datetime import date
    
    # Filtra transações do mês
    transacoes_mes = [
        t for t in transacoes 
        if t.data.year == ano and t.data.month == mes
    ]
    
    # Inicializa dicionários
    dias_no_mes = 31  # Simplificado
    resultado = {
        'receitas': {},
        'despesas': {},
        'saldo_inicial': {},
        'saldo_final': {}
    }
    
    # Para simplificar, começamos com saldo zero
    saldo_atual = 0
    
    for dia in range(1, dias_no_mes + 1):
        data_dia = date(ano, mes, dia)
        
        # Receitas do dia
        receitas_dia = sum(
            t.valor for t in transacoes_mes 
            if t.tipo == 'receita' and t.data.day == dia
        )
        
        # Despesas do dia
        despesas_dia = sum(
            t.valor for t in transacoes_mes 
            if t.tipo == 'despesa' and t.data.day == dia
        )
        
        # Saldo do dia
        saldo_dia = receitas_dia - despesas_dia
        
        resultado['receitas'][dia] = receitas_dia
        resultado['despesas'][dia] = despesas_dia
        resultado['saldo_inicial'][dia] = saldo_atual
        resultado['saldo_final'][dia] = saldo_atual + saldo_dia
        
        saldo_atual += saldo_dia
    
    return resultado

def show_success_message(message: str):
    """Exibe mensagem de sucesso com ícone"""
    st.success(f"✅ {message}")

def show_error_message(message: str):
    """Exibe mensagem de erro com ícone"""
    st.error(f"❌ {message}")

def show_warning_message(message: str):
    """Exibe mensagem de aviso com ícone"""
    st.warning(f"⚠️ {message}")

def show_info_message(message: str):
    """Exibe mensagem informativa com ícone"""
    st.info(f"ℹ️ {message}")

def is_weekend(data: date) -> bool:
    """Verifica se a data é fim de semana"""
    # 5 = Sábado, 6 = Domingo
    return data.weekday() >= 5

def is_today(data: date) -> bool:
    """Verifica se a data é hoje"""
    return data == date.today()