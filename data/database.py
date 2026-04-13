import json
import sqlite3
from pathlib import Path
from typing import List, Optional, Dict, Any
from datetime import datetime, date
import pandas as pd

from .models import Transacao, Usuario, Categoria
from config import APP_CONFIG

class DatabaseManager:
    def __init__(self):
        self.data_dir = APP_CONFIG['data_dir']
        self.data_dir.mkdir(exist_ok=True)
        
        self.transacoes_file = self.data_dir / 'transacoes.json'
        self.usuarios_file = self.data_dir / 'usuarios.json'
        self.categorias_file = self.data_dir / 'categorias.json'
        
        self.init_database()
    
    def init_database(self):
        """Inicializa o banco de dados com dados padrão se necessário"""
        
        # Inicializar transações
        if not self.transacoes_file.exists():
            self.save_transacoes([])
        
        # Inicializar usuários
        if not self.usuarios_file.exists():
            from .sample_data import DEFAULT_USERS
            self.save_usuarios(DEFAULT_USERS)
        
        # Inicializar categorias
        if not self.categorias_file.exists():
            from .sample_data import DEFAULT_CATEGORIES
            self.save_categorias(DEFAULT_CATEGORIES)
    
    # Operações com Transações
    def get_transacoes(self) -> List[Transacao]:
        try:
            with open(self.transacoes_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [Transacao.from_dict(item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_transacoes(self, transacoes: List[Transacao]):
        data = [t.to_dict() for t in transacoes]
        with open(self.transacoes_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def add_transacao(self, transacao: Transacao) -> int:
        transacoes = self.get_transacoes()
        if not transacoes:
            transacao.id = 1
        else:
            transacao.id = max(t.id for t in transacoes) + 1
        transacoes.append(transacao)
        self.save_transacoes(transacoes)
        return transacao.id
    
    def update_transacao(self, transacao: Transacao) -> bool:
        transacoes = self.get_transacoes()
        for i, t in enumerate(transacoes):
            if t.id == transacao.id:
                transacoes[i] = transacao
                self.save_transacoes(transacoes)
                return True
        return False
    
    def delete_transacao(self, transacao_id: int) -> bool:
        transacoes = self.get_transacoes()
        new_transacoes = [t for t in transacoes if t.id != transacao_id]
        if len(new_transacoes) != len(transacoes):
            self.save_transacoes(new_transacoes)
            return True
        return False
    
    def get_transacao(self, transacao_id: int) -> Optional[Transacao]:
        transacoes = self.get_transacoes()
        for t in transacoes:
            if t.id == transacao_id:
                return t
        return None
    
    # Operações com Usuários
    def get_usuarios(self) -> List[Usuario]:
        try:
            with open(self.usuarios_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [Usuario.from_dict(item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_usuarios(self, usuarios: List[Usuario]):
        data = [u.to_dict() for u in usuarios]
        with open(self.usuarios_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_usuario_by_username(self, username: str) -> Optional[Usuario]:
        usuarios = self.get_usuarios()
        for usuario in usuarios:
            if usuario.username == username:
                return usuario
        return None
    
    # Operações com Categorias
    def get_categorias(self) -> List[Categoria]:
        try:
            with open(self.categorias_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            return [Categoria(**item) for item in data]
        except (FileNotFoundError, json.JSONDecodeError):
            return []
    
    def save_categorias(self, categorias: List[Categoria]):
        data = [c.__dict__ for c in categorias]
        with open(self.categorias_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
    
    def get_categoria(self, categoria_id: int) -> Optional[Categoria]:
        categorias = self.get_categorias()
        for cat in categorias:
            if cat.id == categoria_id:
                return cat
        return None
    
    # Métodos utilitários
    def get_transacoes_periodo(self, data_inicio: date, data_fim: date) -> List[Transacao]:
        transacoes = self.get_transacoes()
        return [t for t in transacoes if data_inicio <= t.data <= data_fim]
    
    def get_transacoes_mes(self, ano: int, mes: int) -> List[Transacao]:
        transacoes = self.get_transacoes()
        return [t for t in transacoes if t.data.year == ano and t.data.month == mes]
    
    def export_to_excel(self, filepath: Path):
        """Exporta dados para Excel"""
        transacoes = self.get_transacoes()
        if not transacoes:
            return False
        
        df = pd.DataFrame([t.to_dict() for t in transacoes])
        
        # Converter datas para formato string
        df['data'] = pd.to_datetime(df['data']).dt.strftime('%d/%m/%Y')
        df['data_criacao'] = pd.to_datetime(df['data_criacao']).dt.strftime('%d/%m/%Y %H:%M:%S')
        
        # Reordenar colunas
        col_order = ['id', 'data', 'tipo', 'categoria_id', 'cliente', 'valor', 'status', 'data_criacao', 'origem']
        df = df[col_order]
        
        df.to_excel(filepath, index=False)
        return True
    
    def backup(self, backup_path: Path):
        """Realiza backup completo dos dados"""
        backup_data = {
            'transacoes': [t.to_dict() for t in self.get_transacoes()],
            'usuarios': [u.to_dict() for u in self.get_usuarios()],
            'categorias': [c.__dict__ for c in self.get_categorias()],
            'backup_date': datetime.now().isoformat()
        }
        
        with open(backup_path, 'w', encoding='utf-8') as f:
            json.dump(backup_data, f, indent=2, ensure_ascii=False)
        
        return True
    
    def restore(self, backup_path: Path):
        """Restaura dados de backup"""
        try:
            with open(backup_path, 'r', encoding='utf-8') as f:
                backup_data = json.load(f)
            
            # Restaurar transações
            transacoes = [Transacao.from_dict(t) for t in backup_data.get('transacoes', [])]
            self.save_transacoes(transacoes)
            
            # Restaurar usuários
            usuarios = [Usuario.from_dict(u) for u in backup_data.get('usuarios', [])]
            self.save_usuarios(usuarios)
            
            # Restaurar categorias
            categorias = [Categoria(**c) for c in backup_data.get('categorias', [])]
            self.save_categorias(categorias)
            
            return True
        except Exception as e:
            print(f"Erro ao restaurar backup: {e}")
            return False