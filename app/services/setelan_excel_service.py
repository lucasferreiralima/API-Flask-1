import pandas as pd
import random
import io
from datetime import datetime, date, timedelta
from sqlalchemy import func
from app.extensions import db
from app.models.setelan_models import Loja, Produto, Vendedor, Venda, Estoque, Meta, AlertaOperacional, ResumoExecutivo

class SetelanExcelService:
    @staticmethod
    def limpar_dados():
        """Remove todos os dados das tabelas SeteLan para um reset completo."""
        try:
            db.session.query(Venda).delete()
            db.session.query(Estoque).delete()
            db.session.query(Meta).delete()
            db.session.query(AlertaOperacional).delete()
            db.session.query(Vendedor).delete()
            db.session.query(Produto).delete()
            db.session.query(Loja).delete()
            db.session.query(ResumoExecutivo).delete()
            db.session.commit()
            return True
        except Exception as e:
            db.session.rollback()
            print(f"Erro ao limpar dados: {e}")
            return False

    @staticmethod
    def popular_lojas_reais():
        if Loja.query.first(): return
        
        lojas_data = [
            {"nome": "Américas Shopping", "regiao": "Jacarepaguá/Barra", "tipo": "Shopping", "perfil": "Alto fluxo shopping"},
            {"nome": "Caxias Shopping", "regiao": "Baixada Fluminense", "tipo": "Shopping", "perfil": "Loja de shopping regional"},
            {"nome": "Copacabana", "regiao": "Zona Sul RJ", "tipo": "Rua", "perfil": "Loja de rua premium"},
            {"nome": "Icaraí", "regiao": "Niterói", "tipo": "Rua", "perfil": "Loja de rua premium"},
            {"nome": "Ilha Plaza Shopping", "regiao": "Zona Norte RJ", "tipo": "Shopping", "perfil": "Loja de shopping regional"},
            {"nome": "Madureira Shopping", "regiao": "Zona Norte RJ", "tipo": "Shopping", "perfil": "Alto fluxo popular"},
            {"nome": "Nova Iguaçu Calçadão", "regiao": "Baixada Fluminense", "tipo": "Calçadão", "perfil": "Alto fluxo popular"},
            {"nome": "Nova Iguaçu 2", "regiao": "Baixada Fluminense", "tipo": "Rua", "perfil": "Loja de bairro"},
            {"nome": "Passeio Shopping", "regiao": "Zona Oeste RJ", "tipo": "Shopping", "perfil": "Alto fluxo popular"},
            {"nome": "Santa Cruz Shopping", "regiao": "Zona Oeste RJ", "tipo": "Shopping", "perfil": "Loja de bairro"},
            {"nome": "Shopping Grande Rio", "regiao": "Baixada Fluminense", "tipo": "Shopping", "perfil": "Alto fluxo shopping"},
            {"nome": "Shopping Metropolitano", "regiao": "Jacarepaguá/Barra", "tipo": "Shopping", "perfil": "Alto fluxo shopping"},
            {"nome": "Taquara Plaza Shopping", "regiao": "Jacarepaguá/Barra", "tipo": "Shopping", "perfil": "Loja de shopping regional"},
            {"nome": "West Shopping", "regiao": "Zona Oeste RJ", "tipo": "Shopping", "perfil": "Alto fluxo popular"}
        ]
        
        for l in lojas_data:
            nova_loja = Loja(
                nome_loja=l['nome'], regiao_operacional=l['regiao'], 
                tipo_loja=l['tipo'], perfil_loja=l['perfil'],
                cidade="Rio de Janeiro" if l['regiao'] != "Niterói" else "Niterói",
                uf="RJ", meta_base_mensal=random.randint(80000, 250000)
            )
            db.session.add(nova_loja)
        db.session.commit()

    @staticmethod
    def popular_produtos_simulados():
        if Produto.query.first(): return
        
        categorias = {
            "Planos": ["Plano Controle", "Plano Pós", "Plano Pré", "TIM Black"],
            "Internet": ["Internet Residencial"],
            "Aparelhos": ["Aparelho Samsung", "Aparelho Motorola", "Aparelho iPhone"],
            "Acessórios": ["Carregador", "Capinha", "Película"],
            "Chips": ["Chip TIM"],
            "Seguros": ["Seguro Aparelho"],
            "Serviços": ["Serviço adicional"]
        }
        
        for cat, prods in categorias.items():
            for p in prods:
                tipo = "Recorrente" if cat in ["Planos", "Internet"] else "Venda única"
                custo = random.uniform(10, 3000)
                margem = random.uniform(0.1, 0.4)
                preco = custo * (1 + margem)
                
                novo_prod = Produto(
                    nome_produto=p, categoria=cat, tipo_receita=tipo,
                    preco_medio=preco, custo_medio=custo,
                    margem_percentual_padrao=margem * 100,
                    ativo=True
                )
                db.session.add(novo_prod)
        db.session.commit()

    @staticmethod
    def gerar_massa_dados_ficticios(num_vendas=2000, limpar=False):
        """
        Gera uma base massiva de vendedores, vendas, estoque e metas.
        """
        if limpar:
            SetelanExcelService.limpar_dados()

        # 1. Garantir Lojas e Produtos
        SetelanExcelService.popular_lojas_reais()
        SetelanExcelService.popular_produtos_simulados()
        
        lojas = Loja.query.all()
        produtos = Produto.query.all()
        
        # 2. Gerar Vendedores (5 a 8 por loja)
        if not Vendedor.query.first():
            nomes_v = ["Roberto", "Carla", "André", "Juliana", "Marcos", "Patrícia", "Sérgio", "Fernanda", "Tiago", "Bárbara"]
            sobrenomes_v = ["Silva", "Costa", "Oliveira", "Melo", "Santos", "Ferreira", "Lima", "Souza"]
            
            for lj in lojas:
                for _ in range(random.randint(5, 8)):
                    v = Vendedor(
                        nome_vendedor=f"{random.choice(nomes_v)} {random.choice(sobrenomes_v)}",
                        loja_id=lj.id, cargo=random.choice(["Vendedor", "Consultor", "Supervisor"]),
                        meta_individual_mensal=float(lj.meta_base_mensal or 0) / 6
                    )
                    db.session.add(v)
            db.session.commit()
        
        vendedores = Vendedor.query.all()
        
        # 3. Gerar Vendas
        if not Venda.query.first():
            hoje = datetime.now()
            for _ in range(num_vendas):
                lj = random.choice(lojas)
                vendedores_da_loja = [v for v in vendedores if v.loja_id == lj.id]
                if not vendedores_da_loja: continue
                
                vd = random.choice(vendedores_da_loja)
                pd_item = random.choice(produtos)
                
                qtd = random.randint(1, 3)
                v_bruto = float(pd_item.preco_medio) * qtd
                desc = v_bruto * random.uniform(0, 0.1) if random.random() > 0.7 else 0
                v_liq = v_bruto - desc
                custo_t = float(pd_item.custo_medio) * qtd
                
                nova_venda = Venda(
                    data_venda=hoje - timedelta(days=random.randint(0, 30), hours=random.randint(0, 23)),
                    loja_id=lj.id, vendedor_id=vd.id, produto_id=pd_item.id,
                    quantidade=qtd, valor_bruto=v_bruto, desconto=desc,
                    valor_liquido=v_liq, custo_estimado=custo_t,
                    margem_estimada=v_liq - custo_t,
                    forma_pagamento=random.choice(["Cartão de Crédito", "Pix", "Dinheiro", "Boleto"]),
                    canal_venda=random.choice(["Loja física", "WhatsApp", "Indicação"]),
                    status_venda="Concluída" if random.random() > 0.05 else "Cancelada"
                )
                db.session.add(nova_venda)
            db.session.commit()

        # 4. Gerar Estoque e Metas (Garantindo Casos Críticos)
        if not Estoque.query.first():
            for lj in lojas:
                for pd_item in produtos:
                    # Alguns produtos nascem críticos intencionalmente
                    is_critico = random.random() < 0.15
                    estoque_atual = random.randint(0, 5) if is_critico else random.randint(15, 60)
                    
                    est = Estoque(
                        loja_id=lj.id, produto_id=pd_item.id,
                        estoque_atual=estoque_atual,
                        estoque_minimo=10,
                        estoque_ideal=40, 
                        giro_medio_diario=random.uniform(0.5, 3.0),
                        status_estoque='Crítico' if estoque_atual < 10 else 'Saudável'
                    )
                    db.session.add(est)
        
        if not Meta.query.first():
            for lj in lojas:
                # Meta Geral da Loja
                dificuldade = 1.3 if lj.nome_loja in ["Santa Cruz Shopping", "Nova Iguaçu 2"] else 1.0
                meta_valor = float(lj.meta_base_mensal or 0) * dificuldade
                
                # Calcular realizado real das vendas geradas
                realizado_decimal = db.session.query(func.sum(Venda.valor_liquido)).filter_by(loja_id=lj.id, status_venda='Concluída').scalar() or 0
                realizado = float(realizado_decimal)
                
                m = Meta(
                    ano=2026, mes=5, loja_id=lj.id, categoria="Geral",
                    meta_faturamento=meta_valor,
                    realizado_faturamento=realizado,
                    percentual_atingimento=(realizado / meta_valor * 100) if meta_valor > 0 else 0,
                    dias_restantes=10
                )
                db.session.add(m)
        
        db.session.commit()
        return True

    @staticmethod
    def exportar_para_excel():
        """
        Gera um arquivo Excel com várias abas contendo toda a base simulada.
        """
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            # Exportar cada tabela principal
            pd.read_sql("SELECT * FROM setelan_lojas", db.engine).to_excel(writer, sheet_name='Lojas', index=False)
            pd.read_sql("SELECT * FROM setelan_produtos", db.engine).to_excel(writer, sheet_name='Produtos', index=False)
            pd.read_sql("SELECT * FROM setelan_vendas", db.engine).to_excel(writer, sheet_name='Vendas', index=False)
            pd.read_sql("SELECT * FROM setelan_vendedores", db.engine).to_excel(writer, sheet_name='Vendedores', index=False)
            pd.read_sql("SELECT * FROM setelan_estoques", db.engine).to_excel(writer, sheet_name='Estoque', index=False)
            pd.read_sql("SELECT * FROM setelan_metas", db.engine).to_excel(writer, sheet_name='Metas', index=False)
            
        output.seek(0)
        return output
