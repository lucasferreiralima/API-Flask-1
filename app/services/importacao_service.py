import pandas as pd
import uuid
from datetime import datetime
from app.models.operacao import Operacao
from app.models.staging_operacao import StagingOperacao
from app.extensions import db

class ImportacaoService:
    STATUS_VALIDOS = ['Novo', 'Em análise', 'Pendente documentação', 'Aprovado', 'Reprovado', 'Conta aberta', 'Cancelado']
    PRODUTOS_VALIDOS = ['Abertura de Conta PJ', 'Abertura de Conta PF', 'Cartão', 'Getnet', 'Crédito', 'Maquininha', 'Produto Bancário']

    @staticmethod
    def processar_planilha(file_path):
        """
        Lê a planilha, valida os dados e salva na tabela de staging.
        """
        token = str(uuid.uuid4())
        
        try:
            df = pd.read_excel(file_path)
        except Exception as e:
            return None, f"Erro ao ler arquivo: {str(e)}"

        # Mapeamento de colunas (case-insensitive e flexível)
        mapping = {
            'data_atendimento': ['Data', 'Data Atendimento', 'DATA'],
            'cliente_nome': ['Cliente', 'Nome do Cliente', 'NOME'],
            'cpf_cnpj': ['CPF/CNPJ', 'CPF', 'CNPJ', 'DOCUMENTO'],
            'produto': ['Produto', 'PRODUTO'],
            'status': ['Status', 'STATUS'],
            'responsavel': ['Responsável', 'Responsavel', 'CONSULTOR'],
            'equipe': ['Equipe', 'EQUIPE'],
            'cidade': ['Cidade', 'CIDADE'],
            'uf': ['UF', 'ESTADO'],
            'valor_estimado': ['Valor', 'Valor Estimado', 'VALOR'],
            'observacao': ['Observação', 'Observacao', 'OBS']
        }

        # Normalizar colunas
        for target, aliases in mapping.items():
            for alias in aliases:
                if alias in df.columns:
                    df.rename(columns={alias: target}, inplace=True)
                    break

        for _, row in df.iterrows():
            motivos_erro = []
            status_importacao = 'novo'
            
            # Validação de Campos Obrigatórios
            if pd.isna(row.get('cliente_nome')): motivos_erro.append("Nome do cliente ausente")
            if pd.isna(row.get('produto')): motivos_erro.append("Produto ausente")
            if pd.isna(row.get('status')): motivos_erro.append("Status ausente")
            
            # Validação de Valores (Status e Produto)
            if not pd.isna(row.get('status')) and row.get('status') not in ImportacaoService.STATUS_VALIDOS:
                motivos_erro.append(f"Status inválido: {row.get('status')}")
            
            # Verificação de Duplicidade (Comparação de campos chave)
            if not motivos_erro:
                is_duplicado = Operacao.query.filter_by(
                    cliente_nome=str(row.get('cliente_nome')),
                    cpf_cnpj=str(row.get('cpf_cnpj')),
                    produto=str(row.get('produto')),
                    status=str(row.get('status')),
                    responsavel=str(row.get('responsavel')) if not pd.isna(row.get('responsavel')) else None
                ).first()
                if is_duplicado:
                    status_importacao = 'duplicado'

            if motivos_erro:
                status_importacao = 'erro'

            # Criar registro de Staging
            staging = StagingOperacao(
                importacao_token=token,
                cliente_nome=str(row.get('cliente_nome')) if not pd.isna(row.get('cliente_nome')) else None,
                cpf_cnpj=str(row.get('cpf_cnpj')) if not pd.isna(row.get('cpf_cnpj')) else None,
                produto=str(row.get('produto')) if not pd.isna(row.get('produto')) else None,
                status=str(row.get('status')) if not pd.isna(row.get('status')) else None,
                canal_origem=str(row.get('canal_origem')) if 'canal_origem' in row and not pd.isna(row.get('canal_origem')) else None,
                responsavel=str(row.get('responsavel')) if not pd.isna(row.get('responsavel')) else None,
                equipe=str(row.get('equipe')) if not pd.isna(row.get('equipe')) else None,
                cidade=str(row.get('cidade')) if not pd.isna(row.get('cidade')) else None,
                uf=str(row.get('uf')) if not pd.isna(row.get('uf')) else None,
                valor_estimado=float(row.get('valor_estimado', 0)) if not pd.isna(row.get('valor_estimado')) else 0.0,
                observacao=str(row.get('observacao')) if not pd.isna(row.get('observacao')) else None,
                status_importacao=status_importacao,
                motivo_erro=", ".join(motivos_erro) if motivos_erro else None,
                data_atendimento=pd.to_datetime(row.get('data_atendimento')).date() if not pd.isna(row.get('data_atendimento')) else datetime.utcnow().date()
            )
            db.session.add(staging)
        
        db.session.commit()
        return token, None

    @staticmethod
    def obter_resumo_staging(token):
        staging_items = StagingOperacao.query.filter_by(importacao_token=token).all()
        return {
            "novos": [i for i in staging_items if i.status_importacao == 'novo'],
            "duplicados": [i for i in staging_items if i.status_importacao == 'duplicado'],
            "erros": [i for i in staging_items if i.status_importacao == 'erro'],
            "token": token
        }

    @staticmethod
    def confirmar_importacao(token):
        novos = StagingOperacao.query.filter_by(importacao_token=token, status_importacao='novo').all()
        
        for item in novos:
            op = Operacao(
                data_atendimento=item.data_atendimento,
                cliente_nome=item.cliente_nome,
                cpf_cnpj=item.cpf_cnpj,
                produto=item.produto,
                status=item.status,
                canal_origem=item.canal_origem,
                responsavel=item.responsavel,
                equipe=item.equipe,
                cidade=item.cidade,
                uf=item.uf,
                valor_estimado=item.valor_estimado,
                observacao=item.observacao
            )
            db.session.add(op)
        
        # Limpar staging após confirmação
        StagingOperacao.query.filter_by(importacao_token=token).delete()
        db.session.commit()
        return len(novos)

    @staticmethod
    def cancelar_importacao(token):
        StagingOperacao.query.filter_by(importacao_token=token).delete()
        db.session.commit()
        return True

    @staticmethod
    def gerar_planilha_exemplo():
        import io
        import random
        from datetime import date, timedelta

        # Dados para geração randômica
        nomes = ['João Silva', 'Maria Oliveira', 'Empresa Tech', 'Bazar Central', 'Ana Costa', 'Carlos Souza', 'Padaria Pão Quente', 'Lucas Lima', 'Roberto Santos', 'Fernanda Dias']
        equipes = ['Comercial SP', 'Comercial RJ', 'Crédito', 'Vendas Internas', 'Equipe Sul']
        responsaveis = ['Consultor A', 'Consultor B', 'Consultor C', 'Consultor D']
        cidades = ['São Paulo', 'Rio de Janeiro', 'Curitiba', 'Belo Horizonte', 'Porto Alegre', 'Salvador']
        ufs = ['SP', 'RJ', 'PR', 'MG', 'RS', 'BA']

        data_rows = []
        for i in range(15): # Gerar 15 linhas
            cidade_idx = random.randint(0, len(cidades)-1)
            data_rows.append({
                'Data': (date.today() - timedelta(days=random.randint(0, 30))).strftime('%d/%m/%Y'),
                'Cliente': random.choice(nomes),
                'CPF/CNPJ': f'{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}',
                'Produto': random.choice(ImportacaoService.PRODUTOS_VALIDOS),
                'Status': random.choice(ImportacaoService.STATUS_VALIDOS),
                'Responsável': random.choice(responsaveis),
                'Equipe': random.choice(equipes),
                'Cidade': cidades[cidade_idx],
                'UF': ufs[cidade_idx],
                'Valor': round(random.uniform(500, 10000), 2),
                'Observação': 'Gerado automaticamente para teste'
            })

        df = pd.DataFrame(data_rows)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Sheet1')
        
        output.seek(0)
        return output

    @staticmethod
    def gerar_planilha_erros():
        import io
        import random
        from datetime import date

        # Dados com erros intencionais
        data_rows = [
            # Erro: Nome ausente
            {'Data': '12/05/2026', 'Cliente': None, 'CPF/CNPJ': '111.111.111-11', 'Produto': 'Cartão', 'Status': 'Novo', 'Responsável': 'Erro 1', 'Valor': 100},
            # Erro: Produto ausente
            {'Data': '12/05/2026', 'Cliente': 'Empresa Erro', 'CPF/CNPJ': '22.222.222/0001-22', 'Produto': None, 'Status': 'Novo', 'Responsável': 'Erro 2', 'Valor': 200},
            # Erro: Status Inválido
            {'Data': '12/05/2026', 'Cliente': 'João Erro', 'CPF/CNPJ': '333.333.333-33', 'Produto': 'Crédito', 'Status': 'Em Andamento', 'Responsável': 'Erro 3', 'Valor': 300},
            # Erro: Status ausente
            {'Data': '12/05/2026', 'Cliente': 'Maria Erro', 'CPF/CNPJ': '444.444.444-44', 'Produto': 'Getnet', 'Status': None, 'Responsável': 'Erro 4', 'Valor': 400},
            # Sucesso: Registro OK para comparar
            {'Data': '12/05/2026', 'Cliente': 'Registro Correto', 'CPF/CNPJ': '555.555.555-55', 'Produto': 'Maquininha', 'Status': 'Aprovado', 'Responsável': 'Sucesso', 'Valor': 500},
        ]

        df = pd.DataFrame(data_rows)
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            df.to_excel(writer, index=False, sheet_name='Erros')
        
        output.seek(0)
        return output
