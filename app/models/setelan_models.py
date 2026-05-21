from datetime import datetime
from app.extensions import db

class Loja(db.Model):
    __tablename__ = 'setelan_lojas'
    id = db.Column(db.Integer, primary_key=True)
    nome_loja = db.Column(db.String(100), nullable=False)
    tipo_loja = db.Column(db.String(50)) # Shopping, Rua, Calçadão
    endereco = db.Column(db.String(255))
    bairro = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    cep = db.Column(db.String(10))
    regiao_operacional = db.Column(db.String(100))
    perfil_loja = db.Column(db.String(100))
    gerente_responsavel = db.Column(db.String(100))
    status_loja = db.Column(db.String(20), default='Ativa')
    meta_base_mensal = db.Column(db.Numeric(12, 2), default=0.0)

    # Relacionamentos com cascata para deleção segura
    vendas = db.relationship('Venda', backref='loja', cascade="all, delete-orphan", lazy=True)
    vendedores = db.relationship('Vendedor', backref='loja', cascade="all, delete-orphan", lazy=True)
    estoques = db.relationship('Estoque', backref='loja', cascade="all, delete-orphan", lazy=True)
    metas = db.relationship('Meta', backref='loja', cascade="all, delete-orphan", lazy=True)

class Produto(db.Model):
    __tablename__ = 'setelan_produtos'
    id = db.Column(db.Integer, primary_key=True)
    nome_produto = db.Column(db.String(150), nullable=False)
    categoria = db.Column(db.String(100))
    subcategoria = db.Column(db.String(100))
    tipo_receita = db.Column(db.String(50)) # Recorrente, Venda única
    preco_medio = db.Column(db.Numeric(10, 2), default=0.0)
    custo_medio = db.Column(db.Numeric(10, 2), default=0.0)
    margem_percentual_padrao = db.Column(db.Numeric(5, 2), default=0.0)
    produto_estrategico = db.Column(db.Boolean, default=False)
    ativo = db.Column(db.Boolean, default=True)

    vendas = db.relationship('Venda', backref='produto', lazy=True)
    estoques = db.relationship('Estoque', backref='produto', lazy=True)

class Vendedor(db.Model):
    __tablename__ = 'setelan_vendedores'
    id = db.Column(db.Integer, primary_key=True)
    nome_vendedor = db.Column(db.String(150), nullable=False)
    loja_id = db.Column(db.Integer, db.ForeignKey('setelan_lojas.id'), nullable=False)
    cargo = db.Column(db.String(50))
    data_admissao = db.Column(db.Date)
    status_vendedor = db.Column(db.String(20), default='Ativo')
    meta_individual_mensal = db.Column(db.Numeric(10, 2), default=0.0)

    vendas = db.relationship('Venda', backref='vendedor', lazy=True)

class Venda(db.Model):
    __tablename__ = 'setelan_vendas'
    id = db.Column(db.Integer, primary_key=True)
    data_venda = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    loja_id = db.Column(db.Integer, db.ForeignKey('setelan_lojas.id'), nullable=False)
    vendedor_id = db.Column(db.Integer, db.ForeignKey('setelan_vendedores.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('setelan_produtos.id'), nullable=False)
    quantidade = db.Column(db.Integer, default=1)
    valor_bruto = db.Column(db.Numeric(12, 2), nullable=False)
    desconto = db.Column(db.Numeric(12, 2), default=0.0)
    valor_liquido = db.Column(db.Numeric(12, 2), nullable=False)
    custo_estimado = db.Column(db.Numeric(12, 2), default=0.0)
    margem_estimada = db.Column(db.Numeric(12, 2), default=0.0)
    forma_pagamento = db.Column(db.String(50))
    canal_venda = db.Column(db.String(50))
    status_venda = db.Column(db.String(20), default='Concluída')
    campanha = db.Column(db.String(100))
    observacao = db.Column(db.Text)

class Estoque(db.Model):
    __tablename__ = 'setelan_estoques'
    id = db.Column(db.Integer, primary_key=True)
    data_referencia = db.Column(db.Date, default=datetime.utcnow)
    loja_id = db.Column(db.Integer, db.ForeignKey('setelan_lojas.id'), nullable=False)
    produto_id = db.Column(db.Integer, db.ForeignKey('setelan_produtos.id'), nullable=False)
    estoque_atual = db.Column(db.Integer, default=0)
    estoque_minimo = db.Column(db.Integer, default=0)
    estoque_ideal = db.Column(db.Integer, default=0)
    giro_medio_diario = db.Column(db.Numeric(10, 2), default=0.0)
    dias_ate_ruptura = db.Column(db.Integer)
    ultima_reposicao = db.Column(db.Date)
    status_estoque = db.Column(db.String(20)) # Crítico, Atenção, Saudável, Excesso, Parado
    sugestao_reposicao = db.Column(db.Integer, default=0)

class Meta(db.Model):
    __tablename__ = 'setelan_metas'
    id = db.Column(db.Integer, primary_key=True)
    ano = db.Column(db.Integer, nullable=False)
    mes = db.Column(db.Integer, nullable=False)
    loja_id = db.Column(db.Integer, db.ForeignKey('setelan_lojas.id'), nullable=False)
    categoria = db.Column(db.String(50))
    meta_faturamento = db.Column(db.Numeric(12, 2), default=0.0)
    meta_quantidade = db.Column(db.Integer, default=0)
    realizado_faturamento = db.Column(db.Numeric(12, 2), default=0.0)
    realizado_quantidade = db.Column(db.Integer, default=0)
    percentual_atingimento = db.Column(db.Numeric(5, 2), default=0.0)
    valor_faltante = db.Column(db.Numeric(12, 2), default=0.0)
    dias_restantes = db.Column(db.Integer, default=1)
    necessidade_diaria = db.Column(db.Numeric(12, 2), default=0.0)
    status_meta = db.Column(db.String(20)) # Acima da meta, Dentro do esperado, Atenção, Crítico

class AlertaOperacional(db.Model):
    __tablename__ = 'setelan_alertas'
    id = db.Column(db.Integer, primary_key=True)
    data_alerta = db.Column(db.DateTime, default=datetime.utcnow)
    tipo_alerta = db.Column(db.String(50)) # Meta, Estoque, Vendas, Margem, Produto, Loja
    loja_id = db.Column(db.Integer, db.ForeignKey('setelan_lojas.id'))
    produto_id = db.Column(db.Integer, db.ForeignKey('setelan_produtos.id'))
    severidade = db.Column(db.String(20)) # Baixa, Média, Alta, Crítica
    descricao_alerta = db.Column(db.Text)
    acao_sugerida = db.Column(db.Text)
    status_alerta = db.Column(db.String(20), default='Aberto')

class ResumoExecutivo(db.Model):
    __tablename__ = 'setelan_resumos'
    id = db.Column(db.Integer, primary_key=True)
    periodo = db.Column(db.String(50))
    indicador = db.Column(db.String(100))
    valor = db.Column(db.String(50))
    analise = db.Column(db.Text)
    recomendacao = db.Column(db.Text)
    data_geracao = db.Column(db.DateTime, default=datetime.utcnow)
