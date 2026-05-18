from datetime import datetime
from app.extensions import db

class StagingOperacao(db.Model):
    """
    Tabela temporária para armazenar dados da planilha antes da confirmação final.
    """
    __tablename__ = 'staging_operacoes'

    id = db.Column(db.Integer, primary_key=True)
    importacao_token = db.Column(db.String(50), nullable=False) # Para identificar a sessão de upload
    
    # Campos idênticos ao modelo Operacao
    data_atendimento = db.Column(db.Date)
    cliente_nome = db.Column(db.String(150))
    cpf_cnpj = db.Column(db.String(20))
    produto = db.Column(db.String(100))
    status = db.Column(db.String(50))
    canal_origem = db.Column(db.String(100))
    responsavel = db.Column(db.String(100))
    equipe = db.Column(db.String(100))
    cidade = db.Column(db.String(100))
    uf = db.Column(db.String(2))
    valor_estimado = db.Column(db.Numeric(12, 2))
    observacao = db.Column(db.Text)
    possui_inconsistencia = db.Column(db.Boolean, default=False)
    descricao_inconsistencia = db.Column(db.Text)
    
    # Metadados da importação
    status_importacao = db.Column(db.String(20)) # 'novo', 'duplicado', 'erro'
    motivo_erro = db.Column(db.Text)
    data_processamento = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "cliente": self.cliente_nome,
            "produto": self.produto,
            "status": self.status,
            "status_importacao": self.status_importacao,
            "motivo_erro": self.motivo_erro
        }
