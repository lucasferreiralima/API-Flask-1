from sqlalchemy import func
from app.models.operacao import Operacao
from app.extensions import db

class OperacaoService:
    @staticmethod
    def listar_todas():
        return Operacao.query.all()

    @staticmethod
    def buscar_por_id(operacao_id):
        return Operacao.query.get(operacao_id)

    @staticmethod
    def listar_pendencias():
        # Uma operação é pendente se status for 'Pendente documentação' OU se possui inconsistência
        return Operacao.query.filter(
            (Operacao.status == 'Pendente documentação') | 
            (Operacao.possui_inconsistencia == True)
        ).all()

    @staticmethod
    def calcular_indicadores():
        total = Operacao.query.count()
        convertidas = Operacao.query.filter(Operacao.status.in_(['Conta aberta', 'Aprovado'])).count()
        pendentes = Operacao.query.filter(
            (Operacao.status == 'Pendente documentação') | 
            (Operacao.possui_inconsistencia == True)
        ).count()
        em_analise = Operacao.query.filter(Operacao.status == 'Em análise').count()
        inconsistencias = Operacao.query.filter(Operacao.possui_inconsistencia == True).count()
        
        taxa_conversao = 0
        if total > 0:
            taxa_conversao = round((convertidas / total) * 100, 2)
            
        return {
            "total": total,
            "convertidas": convertidas,
            "pendentes": pendentes,
            "em_analise": em_analise,
            "inconsistencias": inconsistencias,
            "taxa_conversao": taxa_conversao
        }

    @staticmethod
    def agrupar_por_status():
        results = db.session.query(Operacao.status, func.count(Operacao.id)).group_by(Operacao.status).all()
        return {status: count for status, count in results}

    @staticmethod
    def agrupar_por_produto():
        results = db.session.query(Operacao.produto, func.count(Operacao.id)).group_by(Operacao.produto).all()
        return {produto: count for produto, count in results}

    @staticmethod
    def produtividade_por_responsavel():
        results = db.session.query(Operacao.responsavel, func.count(Operacao.id)).group_by(Operacao.responsavel).all()
        return {responsavel if responsavel else "Sem Responsável": count for responsavel, count in results}

    @staticmethod
    def produtividade_por_equipe():
        results = db.session.query(Operacao.equipe, func.count(Operacao.id)).group_by(Operacao.equipe).all()
        return {equipe if equipe else "Sem Equipe": count for equipe, count in results}

    @staticmethod
    def preparar_resumo_dashboard():
        return {
            "indicadores": OperacaoService.calcular_indicadores(),
            "por_status": OperacaoService.agrupar_por_status(),
            "por_produto": OperacaoService.agrupar_por_produto(),
            "por_responsavel": OperacaoService.produtividade_por_responsavel(),
            "por_equipe": OperacaoService.produtividade_por_equipe()
        }
