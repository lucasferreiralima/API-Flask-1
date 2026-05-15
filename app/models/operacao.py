from datetime import datetime
from app.extensions import db

class Operacao(db.Model):
    __tablename__ = 'operacoes'

    id = db.Column(db.Integer, primary_key=True)
    data_atendimento = db.Column(db.Date, nullable=False, default=datetime.utcnow)
    cliente_nome = db.Column(db.String(150), nullable=False)
    cpf_cnpj = db.Column(db.String(20), nullable=False)
    produto = db.Column(db.String(100), nullable=False)
    status = db.Column(db.String(50), nullable=False)
    canal_origem = db.Column(db.String(100))
    responsavel = db.Column(db.String(100))
    equipe = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    valor_estimado = db.Column(db.Numeric(12, 2), default=0.0)
    observacao = db.Column(db.Text)
    possui_inconsistencia = db.Column(db.Boolean, default=False)
    descricao_inconsistencia = db.Column(db.Text)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Operacao {self.id} - {self.cliente_nome}>'

    @property
    def is_convertida(self):
        return self.status in ['Conta aberta', 'Aprovado']

    @property
    def is_pendente(self):
        return self.status == 'Pendente documentação' or self.possui_inconsistencia

    @property
    def is_em_analise(self):
        return self.status == 'Em análise'
