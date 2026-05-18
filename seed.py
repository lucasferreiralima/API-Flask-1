import random
from datetime import date, timedelta
from app import create_app
from app.extensions import db
from app.models.operacao import Operacao

def seed_data():
    app = create_app()
    with app.app_context():
        # Verifica se já existem dados para evitar duplicidade no seed
        if Operacao.query.first():
            print("O banco de dados já possui dados. Pulando seeding.")
            return

        print("Iniciando seeding de 15 operações...")

        nomes = ['João', 'Maria', 'Ana', 'Carlos', 'Lucas', 'Fernanda', 'Roberto', 'Juliana', 'Ricardo', 'Beatriz']
        sobrenomes = ['Silva', 'Oliveira', 'Costa', 'Santos', 'Lima', 'Souza', 'Ferreira', 'Almeida', 'Pereira', 'Mendes']
        empresas = ['Tech', 'Soluções', 'Bazar', 'Logística', 'Serviços', 'Consultoria', 'Varejo', 'Global', 'Inova', 'Brasil']
        
        produtos = ['Abertura de Conta PJ', 'Abertura de Conta PF', 'Cartão', 'Getnet', 'Crédito', 'Maquininha', 'Produto Bancário']
        status_lista = ['Novo', 'Em análise', 'Pendente documentação', 'Aprovado', 'Reprovado', 'Conta aberta', 'Cancelado']
        equipes = ['Comercial SP', 'Comercial RJ', 'Crédito', 'Vendas Internas', 'Equipe Sul']
        responsaveis = ['Consultor A', 'Consultor B', 'Consultor C', 'Consultor D']
        cidades_uf = [('São Paulo', 'SP'), ('Rio de Janeiro', 'RJ'), ('Curitiba', 'PR'), ('Belo Horizonte', 'MG'), ('Porto Alegre', 'RS')]

        operacoes = []
        for i in range(15):
            is_pj = random.choice([True, False])
            if is_pj:
                cliente = f"{random.choice(nomes)} {random.choice(empresas)} Ltda"
                doc = f"{random.randint(10,99)}.{random.randint(100,999)}.{random.randint(100,999)}/0001-{random.randint(10,99)}"
            else:
                cliente = f"{random.choice(nomes)} {random.choice(sobrenomes)}"
                doc = f"{random.randint(100,999)}.{random.randint(100,999)}.{random.randint(100,999)}-{random.randint(10,99)}"

            cidade, uf = random.choice(cidades_uf)
            
            nova_op = Operacao(
                data_atendimento=date.today() - timedelta(days=random.randint(0, 30)),
                cliente_nome=cliente,
                cpf_cnpj=doc,
                produto=random.choice(produtos),
                status=random.choice(status_lista),
                responsavel=random.choice(responsaveis),
                equipe=random.choice(equipes),
                cidade=cidade,
                uf=uf,
                valor_estimado=round(random.uniform(500, 15000), 2),
                possui_inconsistencia=random.random() < 0.15, # 15% de chance de erro
                descricao_inconsistencia="Documento pendente de validação" if random.random() < 0.15 else None
            )
            operacoes.append(nova_op)

        db.session.bulk_save_objects(operacoes)
        db.session.commit()
        print(f"Sucesso! 15 operações aleatórias foram inseridas.")

if __name__ == '__main__':
    seed_data()
