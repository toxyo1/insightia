from fastapi import FastAPI, UploadFile, File, HTTPException, Form, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, HTMLResponse
import pandas as pd
import io
import os
import socket
import zlib
from datetime import datetime
from google import genai
from dotenv import load_dotenv

load_dotenv()

# --- Identificação da instância (vem sempre de variável de ambiente) ---------

INSTANCE_ID = os.getenv("INSTANCE_ID", "app-00")
HOSTNAME = socket.gethostname()

PALETA = ["#2563eb", "#16a34a", "#ea580c", "#9333ea", "#dc2626", "#0891b2"]


def cor_da_instancia(instance_id: str) -> str:
    """Cor derivada do identificador: app-01 azul, app-02 verde, app-03 laranja..."""
    digitos = "".join(c for c in instance_id if c.isdigit())
    indice = int(digitos) - 1 if digitos else zlib.crc32(instance_id.encode())
    return PALETA[indice % len(PALETA)]


COR_INSTANCIA = cor_da_instancia(INSTANCE_ID)

# --- Configuração da IA ---

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    raise ValueError(
        "ERRO FATAL: GEMINI_API_KEY não foi encontrada nas variáveis de ambiente. "
        "Defina-a em um arquivo .env (GEMINI_API_KEY=sua_chave) ou na configuração do container."
    )

client = genai.Client(api_key=GEMINI_API_KEY)
MODEL_NAME = "gemini-3.6-flash"

# --- Configuração da aplicação -----------------------------------------------

app = FastAPI(
    title="Insightia API",
    description="API de qualidade de dados: métricas via Pandas + relatório via Gemini",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Served-By"],  # deixa o frontend ler o cabeçalho via fetch
)


@app.middleware("http")
async def identificar_instancia(request: Request, call_next):
    """Adiciona X-Served-By em TODAS as respostas."""
    resposta = await call_next(request)
    resposta.headers["X-Served-By"] = INSTANCE_ID
    return resposta


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

# --- Endpoints de infraestrutura (load balancer) ------------------------------

@app.get("/health")
def health():
    """Usado pelo balanceador e pelo Docker para detectar instâncias fora do ar."""
    return {"status": "ok", "instance": INSTANCE_ID}


@app.get("/painel", response_class=HTMLResponse)
def painel():
    """Página HTML que mostra, em destaque, qual instância respondeu."""
    agora = datetime.now().strftime("%H:%M:%S")
    html = f"""<!DOCTYPE html>
<html lang="pt-BR">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>Insightia - {INSTANCE_ID}</title>
  <style>
    body {{ margin: 0; min-height: 100vh; display: flex; flex-direction: column;
           align-items: center; justify-content: center; background: {COR_INSTANCIA};
           color: #fff; font-family: system-ui, sans-serif; text-align: center; }}
    h1 {{ font-size: 4rem; margin: .2em 0; }}
    p  {{ font-size: 1.3rem; margin: .3em 0; opacity: .95; }}
  </style>
</head>
<body>
  <p>Respondido por:</p>
  <h1>{INSTANCE_ID}</h1>
  <p>Hostname: {HOSTNAME}</p>
  <p>Horário da resposta: {agora}</p>
</body>
</html>"""
    return HTMLResponse(html, headers={"Cache-Control": "no-store"})

# --- Endpoints ---

@app.get("/")
def home():
    return {
        "status": "Servidor rodando!",
        "modelo_configurado": MODEL_NAME,
        "instancia": INSTANCE_ID,
    }


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
        "instancia": INSTANCE_ID,
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