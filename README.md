# Insightia

O Insightia é uma plataforma de qualidade e padronização de dados projetada para analisar arquivos CSV. A aplicação combina processamento de dados determinístico para calcular métricas exatas com Inteligência Artificial para gerar relatórios diagnósticos descritivos.

## Arquitetura e Abordagem

A filosofia principal deste projeto é a separação de responsabilidades entre o cálculo de dados e a interpretação de dados para evitar alucinações da IA:
* **Processamento Determinístico:** Python e Pandas lidam com o cálculo exato de métricas estruturais (contagem de linhas, valores nulos, duplicatas) e executam as operações de limpeza de dados.
* **Interpretação da IA:** A API do Google Gemini é estritamente utilizada para ler as métricas consolidadas e redigir um relatório descritivo, garantindo que a IA não realize cálculos matemáticos diretos.

## Tecnologias Utilizadas

### Back-end
* **Python**
* **FastAPI:** Desenvolvimento da API e roteamento de requisições.
* **Pandas:** Manipulação de dados, cálculo de métricas e padronização do dataset.
* **Google Gemini API:** Geração de texto baseada em IA para insights de dados.

### Front-end
* **HTML5, CSS3, JavaScript (Vanilla):** Interface responsiva com arquitetura modular.
* **Fetch API:** Comunicação assíncrona com o back-end.

### Deploy
* **Render:** Hospedagem da API back-end.
* **Vercel:** Hospedagem da interface front-end.

## Funcionalidades

* **Perfilamento de Dados:** Calcula o total de linhas, valores ausentes, registros duplicados e atribui um Score de Qualidade de Dados.
* **Diagnóstico com IA:** Gera um relatório automatizado em texto corrido explicando a estrutura e a saúde do dataset enviado.
* **Limpeza Automatizada de Dados:** 
  * Remoção de linhas exatamente duplicadas.
  * Preenchimento de valores nulos (substituídos por "Não Informado").
  * Padronização de cabeçalhos de colunas (letras minúsculas, sem espaços extras).
* **Exportação:** Download do arquivo CSV processado e limpo diretamente pela interface.

## Como Executar Localmente

### Pré-requisitos
* Python 3.9+
* Git

### Configuração do Back-end
1. Clone o repositório:
   ```bash
   git clone (https://github.com/toxyo1/data-analyst-assistant)