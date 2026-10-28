
import os
import time

import httpx
from fastapi import FastAPI, HTTPException, Request, Response
from prometheus_client import (
    Counter,
    Histogram,
    generate_latest,
    CONTENT_TYPE_LATEST,
)

app = FastAPI(
    title="Insightia Gateway",
    description="API intermediária para demonstração de sistemas distribuídos",
    version="1.0.0",
)

INSIGHTIA_URL = os.getenv(
    "INSIGHTIA_URL",
    "http://insightia_api:8000",
)

# Métricas do Gateway
REQUISICOES = Counter(
    "gateway_http_requests_total",
    "Total de requisições recebidas pelo Gateway",
    ["method", "route", "status"],
)

DURACAO = Histogram(
    "gateway_http_request_duration_seconds",
    "Tempo de resposta do Gateway",
    ["route"],
)


@app.middleware("http")
async def monitorar_requisicoes(request: Request, call_next):
    if request.url.path == "/metrics":
        return await call_next(request)

    inicio = time.perf_counter()
    rota = request.url.path
    status = 500

    try:
        resposta = await call_next(request)
        status = resposta.status_code
        return resposta

    finally:
        duracao = time.perf_counter() - inicio

        REQUISICOES.labels(
            method=request.method,
            route=rota,
            status=str(status),
        ).inc()

        DURACAO.labels(
            route=rota,
        ).observe(duracao)


@app.get("/")
async def consultar_insightia():
    """
    Consulta o Insightia através da rede Docker.

    Se o Insightia apresentar erro HTTP 500,
    o Gateway retorna HTTP 502.
    """

    try:
        async with httpx.AsyncClient(timeout=5.0) as cliente:
            resposta = await cliente.get(
                f"{INSIGHTIA_URL}/"
            )

    except httpx.RequestError as erro:
        raise HTTPException(
            status_code=503,
            detail="O serviço Insightia está indisponível.",
        ) from erro

    if resposta.status_code >= 500:
        raise HTTPException(
            status_code=502,
            detail=(
                "Falha na comunicação com o Insightia. "
                f"Status recebido: {resposta.status_code}"
            ),
        )

    if resposta.status_code >= 400:
        raise HTTPException(
            status_code=502,
            detail=(
                "O Insightia retornou uma resposta inesperada. "
                f"Status: {resposta.status_code}"
            ),
        )

    return {
        "servico": "Insightia Gateway",
        "status": "sucesso",
        "mensagem": "Comunicação entre serviços realizada.",
        "servico_consultado": "insightia_api",
        "status_insightia": resposta.status_code,
    }


@app.get("/health")
def verificar_saude():
    return {
        "servico": "gateway",
        "status": "ativo",
    }


@app.get("/metrics")
def obter_metricas():
    return Response(
        content=generate_latest(),
        media_type=CONTENT_TYPE_LATEST,
    )
