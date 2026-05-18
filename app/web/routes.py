import os
from flask import render_template, request, redirect, url_for, flash, current_app, send_file
from werkzeug.utils import secure_filename
from app.web import web
from app.services.operacao_service import OperacaoService
from app.services.importacao_service import ImportacaoService

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
    return render_template('form_operacao.html', operacao=None)

@web.route('/operacoes/editar/<int:id>', methods=['GET', 'POST'])
def editar_operacao(id):
    operacao = OperacaoService.buscar_por_id(id)
    if not operacao:
        return "Operação não encontrada", 404
    
    if request.method == 'POST':
        OperacaoService.atualizar_operacao(id, request.form)
        return redirect(url_for('web.listar_operacoes'))
    
    return render_template('form_operacao.html', operacao=operacao)

@web.route('/importar', methods=['GET', 'POST'])
def importar():
    if request.method == 'POST':
        if 'file' not in request.files:
            return redirect(request.url)
        
        file = request.files['file']
        if file.filename == '':
            return redirect(request.url)
            
        if file:
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'static/uploads')
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)
                
            file_path = os.path.join(upload_folder, filename)
            file.save(file_path)
            
            token, error = ImportacaoService.processar_planilha(file_path)
            os.remove(file_path) # Limpar arquivo após processar
            
            if error:
                return error, 400
                
            return redirect(url_for('web.preview_importacao', token=token))
            
    return render_template('importar.html')

@web.route('/importar/preview/<token>')
def preview_importacao(token):
    resumo = ImportacaoService.obter_resumo_staging(token)
    return render_template('importar_preview.html', resumo=resumo)

@web.route('/importar/confirmar/<token>')
def confirmar_importacao(token):
    count = ImportacaoService.confirmar_importacao(token)
    return redirect(url_for('web.listar_operacoes'))

@web.route('/importar/cancelar/<token>')
def cancelar_importacao(token):
    ImportacaoService.cancelar_importacao(token)
    return redirect(url_for('web.importar'))

@web.route('/importar/exemplo')
def baixar_exemplo():
    output = ImportacaoService.gerar_planilha_exemplo()
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='exemplo_importacao_vettoreflow.xlsx'
    )

@web.route('/importar/exemplo-erros')
def baixar_exemplo_erros():
    output = ImportacaoService.gerar_planilha_erros()
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='exemplo_com_erros_vettoreflow.xlsx'
    )
