# Validação de Cupons de Desconto

API serverless desenvolvida em Python utilizando Azure Functions para validação de cupons de desconto.

## Cupons disponíveis

- DESCONTO10: 10% de desconto
- DESCONTO20: 20% de desconto
- SEMESTRE: 15% de desconto

## Funcionamento

A API recebe uma requisição HTTP POST contendo o código do cupom e o valor da compra.

Quando o cupom é válido, a API retorna o percentual de desconto, o valor do desconto e o valor final da compra.

Quando o cupom não existe, a API informa que o cupom é inválido.

## Tecnologias utilizadas

- Python
- Azure Functions
- Azure Cloud Shell
- Azure Functions Core Tools
- Git
- GitHub

## Executando localmente

Na pasta do projeto, execute:

    func start

A função estará disponível em:

    http://localhost:7071/api/validar_cupom

## Teste local

    curl -X POST http://localhost:7071/api/validar_cupom -H "Content-Type: application/json" -d '{"cupom":"DESCONTO10","valor_compra":100}'

## Resposta esperada

    {
      "cupom": "DESCONTO10",
      "valido": true,
      "desconto_percentual": 10,
      "valor_desconto": 10.0,
      "valor_final": 90.0
    }


## Estrutura do projeto

    validar-cupom/
    ├── function_app.py
    ├── host.json
    ├── requirements.txt
    ├── README.md
    └── .gitignore

O arquivo local.settings.json é utilizado apenas para execução local e não deve ser versionado no GitHub.
