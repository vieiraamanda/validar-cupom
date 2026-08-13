import azure.functions as func
import json
import logging

app = func.FunctionApp()

CUPONS = {
    "DESCONTO10": 10,
    "DESCONTO20": 20,
    "SEMESTRE": 15
}

@app.route(
    route="validar_cupom",
    methods=["POST"],
    auth_level=func.AuthLevel.ANONYMOUS
)
def validar_cupom(req: func.HttpRequest) -> func.HttpResponse:
    logging.info("Validando cupom de desconto.")

    try:
        dados = req.get_json()
        cupom = dados.get("cupom")
        valor_compra = dados.get("valor_compra")
    except ValueError:
        return func.HttpResponse(
            json.dumps({"erro": "O corpo da requisição deve ser um JSON válido."}),
            status_code=400,
            mimetype="application/json"
        )

    if not cupom or valor_compra is None:
        return func.HttpResponse(
            json.dumps({"erro": "Informe 'cupom' e 'valor_compra'."}),
            status_code=400,
            mimetype="application/json"
        )

    try:
        valor_compra = float(valor_compra)
    except (ValueError, TypeError):
        return func.HttpResponse(
            json.dumps({"erro": "'valor_compra' deve ser um número."}),
            status_code=400,
            mimetype="application/json"
        )

    if valor_compra < 0:
        return func.HttpResponse(
            json.dumps({"erro": "'valor_compra' não pode ser negativo."}),
            status_code=400,
            mimetype="application/json"
        )

    if cupom not in CUPONS:
        return func.HttpResponse(
            json.dumps({
                "cupom": cupom,
                "valido": False,
                "mensagem": "Cupom inválido."
            }),
            status_code=200,
            mimetype="application/json"
        )

    desconto_percentual = CUPONS[cupom]
    valor_desconto = valor_compra * desconto_percentual / 100
    valor_final = valor_compra - valor_desconto

    resposta = {
        "cupom": cupom,
        "valido": True,
        "desconto_percentual": desconto_percentual,
        "valor_desconto": round(valor_desconto, 2),
        "valor_final": round(valor_final, 2)
    }

    return func.HttpResponse(
        json.dumps(resposta),
        status_code=200,
        mimetype="application/json"
    )
