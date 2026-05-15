from flask import jsonify
from app.api import api
from app.services.operacao_service import OperacaoService

@api.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "up", "api": "ok"}), 200

@api.route('/operacoes', methods=['GET'])
def get_operacoes():
    operacoes = OperacaoService.listar_todas()
    return jsonify([
        {
            "id": o.id,
            "cliente": o.cliente_nome,
            "produto": o.produto,
            "status": o.status,
            "responsavel": o.responsavel
        } for o in operacoes
    ]), 200

@api.route('/pendencias', methods=['GET'])
def get_pendencias():
    pendencias = OperacaoService.listar_pendencias()
    return jsonify([
        {
            "id": p.id,
            "cliente": p.cliente_nome,
            "produto": p.produto,
            "status": p.status,
            "inconsistencia": p.descricao_inconsistencia
        } for p in pendencias
    ]), 200

@api.route('/dashboard/resumo', methods=['GET'])
def get_dashboard_resumo():
    resumo = OperacaoService.preparar_resumo_dashboard()
    return jsonify(resumo), 200

@api.route('/indicadores', methods=['GET'])
def get_indicadores():
    indicadores = OperacaoService.calcular_indicadores()
    return jsonify(indicadores), 200
