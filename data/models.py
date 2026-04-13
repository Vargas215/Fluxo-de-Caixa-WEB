from dataclasses import dataclass, asdict
from datetime import datetime, date
from typing import Optional, List, Dict
import json

@dataclass
class Transacao:
    id: int
    tipo: str  # 'receita' ou 'despesa'
    data: date
    categoria_id: int
    cliente: Optional[str]
    valor: float
    status: str = 'pago'
    data_criacao: datetime = datetime.now()
    origem: str = 'sistema'
    
    def to_dict(self):
        data_dict = asdict(self)
        data_dict['data'] = self.data.isoformat()
        data_dict['data_criacao'] = self.data_criacao.isoformat()
        return data_dict
    
    @classmethod
    def from_dict(cls, data_dict):
        data_dict = data_dict.copy()
        data_dict['data'] = date.fromisoformat(data_dict['data'])
        data_dict['data_criacao'] = datetime.fromisoformat(data_dict['data_criacao'])
        return cls(**data_dict)

@dataclass
class Usuario:
    id: int
    nome: str
    username: str
    senha: str
    role: str
    permissao: Dict = None
    ativo: bool = True
    data_criacao: datetime = datetime.now()
    
    def to_dict(self):
        data_dict = asdict(self)
        data_dict['data_criacao'] = self.data_criacao.isoformat()
        return data_dict
    
    @classmethod
    def from_dict(cls, data_dict):
        data_dict = data_dict.copy()
        data_dict['data_criacao'] = datetime.fromisoformat(data_dict['data_criacao'])
        return cls(**data_dict)

@dataclass
class Categoria:
    id: int
    nome: str
    tipo: str  # 'receita' ou 'despesa'
    cor: str = '#3498db'
    ativa: bool = True