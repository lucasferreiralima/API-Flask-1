from flask import render_template, request, redirect, url_for, flash
from app.web import web
from app.services.operacao_service import OperacaoService

@web.route('/')
def index():
    resumo = OperacaoService.preparar_resumo_dashboard()
    return render_template('dashboard.html', resumo=resumo)

@web.route('/operacoes')
def listar_operacoes():
    operacoes = OperacaoService.listar_todas()
    return render_template('operacoes.html', operacoes=operacoes)

@web.route('/pendencias')
def listar_pendencias():
    pendencias = OperacaoService.listar_pendencias()
    return render_template('pendencias.html', pendencias=pendencias)

@web.route('/operacoes/nova', methods=['GET', 'POST'])
def nova_operacao():
    if request.method == 'POST':
        OperacaoService.criar_operacao(request.form)
        return redirect(url_for('web.listar_operacoes'))
    return render_template('form_operacao.html')
