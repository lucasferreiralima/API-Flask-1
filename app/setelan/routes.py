from flask import render_template, redirect, url_for, send_file
from app.setelan import setelan
from app.services.setelan_service import SetelanService
from app.services.setelan_excel_service import SetelanExcelService
from app.models.setelan_models import Loja, Produto, Estoque, Meta, Vendedor, Venda, AlertaOperacional

@setelan.route('/')
def index():
    # Garantir que existam dados mínimos
    if not Loja.query.first():
        return redirect(url_for('setelan.setup_data'))
    
    kpis = SetelanService.obter_kpis_globais()
    ranking = SetelanService.ranking_lojas()
    alertas = SetelanService.listar_alertas_prioritarios()
    return render_template('setelan/dashboard.html', kpis=kpis, ranking=ranking, alertas=alertas)

@setelan.route('/lojas')
def desempenho_lojas():
    ranking = SetelanService.ranking_lojas()
    return render_template('setelan/lojas.html', ranking=ranking)

@setelan.route('/estoque')
def estoque_reposicao():
    estoques = Estoque.query.filter(Estoque.estoque_atual <= Estoque.estoque_minimo).all()
    return render_template('setelan/estoque.html', estoques=estoques)

@setelan.route('/resumo')
def resumo_executivo():
    texto = SetelanService.gerar_resumo_executivo_texto()
    kpis = SetelanService.obter_kpis_globais()
    return render_template('setelan/resumo.html', texto=texto, kpis=kpis)

@setelan.route('/produtos')
def mix_produtos():
    mix = SetelanService.analise_mix_produtos()
    return render_template('setelan/produtos.html', mix=mix)

@setelan.route('/metas')
def metas_comerciais():
    metas_data = SetelanService.relatorio_metas()
    return render_template('setelan/metas.html', metas_data=metas_data)

@setelan.route('/engine')
def data_engine():
    return render_template('setelan/engine.html')

@setelan.route('/setup-data')
def setup_data():
    SetelanExcelService.gerar_massa_dados_ficticios(num_vendas=1500, limpar=True)
    return redirect(url_for('setelan.index'))

@setelan.route('/download-base')
def baixar_base():
    output = SetelanExcelService.exportar_para_excel()
    return send_file(
        output,
        mimetype='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        as_attachment=True,
        download_name='base_setelan_insight_completa.xlsx'
    )
