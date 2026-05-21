from sqlalchemy import func, desc
from app.extensions import db
from app.models.setelan_models import Loja, Produto, Vendedor, Venda, Estoque, Meta, AlertaOperacional, ResumoExecutivo
from datetime import datetime

class SetelanService:
    @staticmethod
    def obter_kpis_globais():
        # Faturamento e Vendas (Apenas Concluídas)
        vendas_query = Venda.query.filter_by(status_venda='Concluída')
        faturamento = db.session.query(func.sum(Venda.valor_liquido)).filter_by(status_venda='Concluída').scalar() or 0
        qtd_vendas = vendas_query.count()
        margem_total = db.session.query(func.sum(Venda.margem_estimada)).filter_by(status_venda='Concluída').scalar() or 0
        
        ticket_medio = faturamento / qtd_vendas if qtd_vendas > 0 else 0
        margem_perc = (margem_total / faturamento * 100) if faturamento > 0 else 0
        
        # Metas
        metas = Meta.query.filter_by(categoria='Geral').all()
        total_meta = sum([float(m.meta_faturamento) for m in metas])
        atingimento_geral = (float(faturamento) / total_meta * 100) if total_meta > 0 else 0
        
        # Estoque e Alertas
        estoque_critico = Estoque.query.filter(Estoque.estoque_atual < Estoque.estoque_minimo).count()
        estoque_parado = Estoque.query.filter(Estoque.status_estoque == 'Parado').count()
        alertas_abertos = AlertaOperacional.query.filter_by(status_alerta='Aberto').count()

        return {
            "faturamento": faturamento,
            "qtd_vendas": qtd_vendas,
            "ticket_medio": ticket_medio,
            "margem_real": margem_total,
            "margem_perc": margem_perc,
            "atingimento_meta": atingimento_geral,
            "estoque_critico": estoque_critico,
            "estoque_parado": estoque_parado,
            "alertas_abertos": alertas_abertos
        }

    @staticmethod
    def ranking_lojas():
        # Agrupar vendas por loja
        results = db.session.query(
            Loja.nome_loja, 
            func.sum(Venda.valor_liquido).label('total'),
            func.count(Venda.id).label('contagem')
        ).join(Venda).filter(Venda.status_venda == 'Concluída')\
        .group_by(Loja.nome_loja).order_by(desc('total')).all()
        
        return results

    @staticmethod
    def ranking_produtos():
        results = db.session.query(
            Produto.nome_produto, 
            Produto.categoria,
            func.sum(Venda.valor_liquido).label('faturamento'),
            func.sum(Venda.quantidade).label('qtd')
        ).join(Venda).filter(Venda.status_venda == 'Concluída')\
        .group_by(Produto.nome_produto, Produto.categoria).order_by(desc('faturamento')).limit(10).all()
        
        return results

    @staticmethod
    def gerar_resumo_executivo_texto():
        kpis = SetelanService.obter_kpis_globais()
        rank = SetelanService.ranking_lojas()
        
        melhor_loja = rank[0][0] if rank else "N/A"
        pior_loja = rank[-1][0] if rank else "N/A"
        
        resumo = f"O grupo atingiu {kpis['atingimento_meta']:.1f}% da meta mensal até o momento. "
        resumo += f"As lojas {melhor_loja} e {rank[1][0] if len(rank)>1 else ''} apresentaram os maiores faturamentos. "
        resumo += f"A unidade {pior_loja} demanda atenção por performance abaixo da média regional. "
        resumo += f"Foram identificados {kpis['estoque_critico']} produtos com estoque crítico, sendo recomendada reposição imediata."
        
        return resumo

    @staticmethod
    def listar_alertas_prioritarios():
        # Se não houver alertas, gerar alguns baseados em regras
        if not AlertaOperacional.query.first():
            SetelanService.processar_regras_alerta()
        
        return AlertaOperacional.query.order_by(desc(AlertaOperacional.severidade)).limit(10).all()

    @staticmethod
    def processar_regras_alerta():
        # Exemplo de regra: Estoque Baixo
        criticos = Estoque.query.filter(Estoque.estoque_atual < Estoque.estoque_minimo).limit(5).all()
        for e in criticos:
            novo_alerta = AlertaOperacional(
                tipo_alerta='Estoque', loja_id=e.loja_id, produto_id=e.produto_id,
                severidade='Alta', descricao_alerta=f"Estoque crítico de {e.produto.nome_produto} na loja {e.loja.nome_loja}.",
                acao_sugerida="Realizar transferência entre lojas ou novo pedido ao CD."
            )
            db.session.add(novo_alerta)
        db.session.commit()

    @staticmethod
    def analise_mix_produtos():
        return db.session.query(
            Produto.categoria,
            func.count(Venda.id).label('qtd_vendas'),
            func.sum(Venda.valor_liquido).label('faturamento'),
            func.avg(Venda.margem_estimada / Venda.valor_liquido * 100).label('margem_media')
        ).join(Venda).filter(Venda.status_venda == 'Concluída')\
        .group_by(Produto.categoria).order_by(desc('faturamento')).all()

    @staticmethod
    def relatorio_metas():
        return db.session.query(
            Loja.nome_loja,
            Meta.meta_faturamento,
            Meta.realizado_faturamento,
            Meta.percentual_atingimento,
            Meta.status_meta
        ).join(Meta, Loja.id == Meta.loja_id).filter(Meta.categoria == 'Geral').all()
