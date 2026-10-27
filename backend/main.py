from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request, Response, Depends  # [OBS]
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import os
import time    # [OBS]
import random  # [OBS]
from google import genai
from dotenv import load_dotenv
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST  # [OBS]

load_dotenv()

# --- Configuração da IA ---

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError(
        "ERRO FATAL: GEMINI_API_KEY não foi encontrada nas variáveis de ambiente. "
        "Defina-a em um arquivo .env (GEMINI_API_KEY=sua_chave) ou na configuração do container."
    )

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3.6-flash"

# --- [OBS] Observabilidade (Prometheus) ---------------------------------------
REQUISICOES = Counter(
    "http_requests_total", "Total de requisições HTTP", ["route", "method", "status"]
)
LATENCIA = Histogram(
    "http_request_duration_seconds", "Tempo de resposta das requisições HTTP", ["route"]
)

# --- [OBS] Falha controlada (somente para a demonstração) ---------------------
TAXA_FALHA = {"valor": 0.0}


def injetar_falha(request: Request):
    """Devolve HTTP 500 em uma fração das requisições, sem mexer nas rotas."""
    if request.url.path.startswith(("/metrics", "/demo")):
        return
    if random.random() < TAXA_FALHA["valor"]:
        raise HTTPException(status_code=500, detail="Falha simulada para a demonstração")


# --- Configuração da aplicação -----------------------------------------------

app = FastAPI(
    title="Insightia API",
    description="API de qualidade de dados: métricas via Pandas + relatório via Gemini",
    dependencies=[Depends(injetar_falha)],  # [OBS]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# [OBS] mede toda requisição: Rate, Errors e Duration
@app.middleware("http")
async def medir_requisicoes(request: Request, call_next):
    inicio = time.perf_counter()
    status = 500
    try:
        resposta = await call_next(request)
        status = resposta.status_code
        return resposta
    finally:
        rota = getattr(request.scope.get("route"), "path", "desconhecida")
        if rota != "/metrics":
            LATENCIA.labels(rota).observe(time.perf_counter() - inicio)
            REQUISICOES.labels(rota, request.method, str(status)).inc()


MAX_UPLOAD_BYTES = 20 * 1024 * 1024


def ler_csv_com_limite(contents: bytes) -> pd.DataFrame:
    """Valida o tamanho e lê o CSV com detecção automática de delimitador."""
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo muito grande. O limite atual é {MAX_UPLOAD_BYTES // (1024 * 1024)}MB.",
        )
    try:
        return pd.read_csv(io.BytesIO(contents), sep=None, engine="python")
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Não foi possível ler o CSV. Verifique o formato (delimitador, encoding). Detalhe: {str(e)}",
        )

# --- Endpoints ---

@app.get("/")
def home():
    return {"status": "Servidor rodando!", "modelo_configurado": MODEL_NAME}


# [OBS] endpoint que o Prometheus consulta (pull)
@app.get("/metrics", include_in_schema=False)
def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


# [OBS] liga/desliga a falha da demonstração: /demo/falha/0.3 e /demo/falha/0
@app.get("/demo/falha/{taxa}", include_in_schema=False)
def definir_falha(taxa: float):
    TAXA_FALHA["valor"] = max(0.0, min(1.0, taxa))
    return {"taxa_de_erro": TAXA_FALHA["valor"]}


@app.post("/analyze")
async def analyze_data(file: UploadFile = File(...)):
    contents = await file.read()
    df = ler_csv_com_limite(contents)

    # 1. Cálculos
    total_linhas = len(df)
    total_colunas = len(df.columns)
    total_celulas = total_linhas * total_colunas

    if total_celulas > 0:
        duplicatas = int(df.duplicated().sum())
        nulos = int(df.isnull().sum().sum())

        celulas_afetadas = (duplicatas * total_colunas) + nulos
        taxa_erros = min(1.0, celulas_afetadas / total_celulas)
        score = round((1 - taxa_erros) * 100)
    else:
        duplicatas, nulos, score = 0, 0, 100

    # 2. Prompt da IA
    prompt = f"""
    Aja como um Engenheiro de Dados sênior avaliando a qualidade de uma base de dados.
    Acabei de processar um arquivo CSV chamado '{file.filename}' com os seguintes dados:
    - Total de registros: {total_linhas}
    - Total de colunas: {total_colunas}
    - Colunas identificadas: {', '.join(df.columns.tolist())}
    - Linhas totalmente duplicadas: {duplicatas}
    - Células vazias (valores nulos): {nulos}
    - Score de Qualidade Geral: {score}/100

    Escreva um breve relatório descritivo (máximo de 2 parágrafos curtos) em tom profissional e direto.
    Explique brevemente o estado da base com foco nos dados ausentes e duplicados, justificando o Score de Qualidade.
    Não invente nenhuma métrica nova, baseie-se apenas nos números acima. Não cumprimente o usuário.
    """

    # 3. Chamada da IA
    try:
        response = await client.aio.models.generate_content(
            model=MODEL_NAME, contents=prompt
        )
        relatorio = response.text.strip()
    except Exception as e:
        relatorio = (
            "Não foi possível gerar o relatório descritivo no momento "
            f"(erro ao consultar a IA: {str(e)}). As métricas acima permanecem válidas."
        )

    return {
        "estatisticas": {
            "linhas": total_linhas,
            "colunas": total_colunas,
            "duplicatas": duplicatas,
            "nulos": nulos,
            "score": score,
        },
        "relatorio_ia": relatorio,
    }

@app.post("/clean")
async def clean_data(
    file: UploadFile = File(...),
    remover_duplicatas: bool = Form(True),
    preencher_nulos: bool = Form(True),
    normalizar_colunas: bool = Form(True),
):
    """Aplica a padronização escolhida pelo usuário e devolve o arquivo limpo para download."""

    contents = await file.read()
    df = ler_csv_com_limite(contents)

    # --- Regras de limpeza ---
    if remover_duplicatas:
        df = df.drop_duplicates()

    if preencher_nulos:
        df = df.fillna("Não Informado")

    if normalizar_colunas:
        df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    stream = io.StringIO()
    df.to_csv(stream, index=False)

    response = StreamingResponse(
        iter([stream.getvalue()]), 
        media_type="text/csv"
    )
    response.headers["Content-Disposition"] = f"attachment; filename=Insightia_Padronizado_{file.filename}"
    return response