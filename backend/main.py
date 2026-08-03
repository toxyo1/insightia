"""
Insightia API — análise e padronização de qualidade de dados em arquivos CSV.

Arquitetura:
- Pandas calcula todas as métricas exatas (linhas, nulos, duplicatas, score).
  A IA nunca faz contas: ela só recebe os números já prontos e redige o texto.
- Tudo em memória: nenhum arquivo é salvo em disco. O front-end reenvia o CSV
  original a cada chamada (/analyze e /clean são independentes), então não
  há necessidade de persistir estado entre requisições.
- Chave de API somente via variável de ambiente (.env), nunca hardcoded.
"""

from fastapi import FastAPI, UploadFile, File, HTTPException, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
import pandas as pd
import io
import os
from google import genai
from dotenv import load_dotenv

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
)

MAX_UPLOAD_BYTES = 20 * 1024 * 1024


def ler_csv_com_limite(contents: bytes) -> pd.DataFrame:
    """Valida o tamanho e faz o parse do CSV, com mensagens de erro amigáveis."""
    if len(contents) > MAX_UPLOAD_BYTES:
        raise HTTPException(
            status_code=413,
            detail=f"Arquivo muito grande. O limite atual é {MAX_UPLOAD_BYTES // (1024 * 1024)}MB.",
        )
    try:
        return pd.read_csv(io.BytesIO(contents))
    except Exception as e:
        raise HTTPException(
            status_code=400,
            detail=f"Não foi possível ler o CSV. Verifique o formato (delimitador, encoding). Detalhe: {str(e)}",
        )


# --- Endpoints ---

@app.get("/")
def home():
    """Health check simples — confirma que o servidor subiu e qual modelo está ativo."""
    return {"status": "Servidor rodando!", "modelo_configurado": MODEL_NAME}


@app.post("/analyze")
async def analyze_data(file: UploadFile = File(...)):
    """Recebe o CSV, extrai métricas exatas com Pandas e gera o insight com IA."""

    contents = await file.read()
    df = ler_csv_com_limite(contents)

    # --- Cálculos ---
    total_linhas = len(df)
    total_colunas = len(df.columns)
    duplicatas = int(df.duplicated().sum())
    nulos = int(df.isnull().sum().sum())

    total_celulas = total_linhas * total_colunas
    taxa_erros = (duplicatas + nulos) / total_celulas if total_celulas > 0 else 0
    score = max(0, min(100, int(100 - (taxa_erros * 100))))

    # --- Prompt de contexto para a IA ---
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

    try:
        response = client.models.generate_content(model=MODEL_NAME, contents=prompt)
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
        df.columns = df.columns.str.strip().str.lower()

    stream = io.StringIO()
    df.to_csv(stream, index=False)

    response = StreamingResponse(iter([stream.getvalue()]), media_type="text/csv")
    response.headers["Content-Disposition"] = f"attachment; filename=Insightia_Padronizado_{file.filename}"
    return response