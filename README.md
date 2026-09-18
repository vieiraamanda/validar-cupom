# Checkpoint 5 — CI/CD e Deploy Automatizado

Projeto desenvolvido para o Checkpoint 5, utilizando **GitHub Actions** para automatizar o processo de validação e deploy da Azure Function.

## Objetivo

Implementar um pipeline de **CI/CD** capaz de automatizar a integração e a implantação das funções serverless do projeto.

A partir de alterações realizadas na branch `checkpoint-5`, o GitHub Actions executa automaticamente as etapas de validação e deploy da aplicação.

## Pipeline

O workflow está localizado em:

```text
.github/workflows/deploy.yml
```

O pipeline executa as seguintes etapas:

1. Checkout do código-fonte;
2. Configuração do Python 3.11;
3. Instalação das dependências do projeto;
4. Validação da sintaxe do código;
5. Autenticação no Azure utilizando **OpenID Connect (OIDC)**;
6. Deploy automático da Azure Function.

## Segurança

A autenticação entre o GitHub Actions e o Azure utiliza **OpenID Connect (OIDC)**, evitando a necessidade de armazenar um client secret permanente no repositório.

Os identificadores utilizados pelo workflow são armazenados por meio dos **GitHub Actions Secrets**.

Nenhuma chave de API, token, credencial, connection string, arquivo `.env` ou `local.settings.json` é versionado no repositório.

## Evidências

As evidências da execução do pipeline estão disponíveis em:

```text
evidencias/checkpoint-5/
```

A pasta contém capturas de tela dos principais estágios da execução do GitHub Actions, incluindo a validação, autenticação no Azure e deploy realizado com sucesso.

## Resultado

O pipeline foi executado com sucesso, demonstrando o processo automatizado de CI/CD para implantação da Azure Function.

A cada novo push na branch `checkpoint-5`, o workflow é acionado automaticamente e realiza o processo de validação e deploy configurado.
