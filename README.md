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

---

# Balanceamento de Carga com NGINX

## Objetivo

Como extensão do Insightia, foi implementada uma arquitetura de balanceamento de carga para distribuir as requisições HTTP entre múltiplas instâncias da API. A solução utiliza NGINX como ponto único de entrada e Docker Compose para executar e gerenciar os serviços.

## Arquitetura

O NGINX recebe as requisições na porta `8080` e as distribui entre instâncias independentes do back-end FastAPI, utilizando a estratégia **Round Robin**.

```text
                 Cliente / Navegador
                          |
                          v
                  NGINX (porta 8080)
                          |
              +-----------+-----------+
              |           |           |
              v           v           v
           app-01      app-02      app-03
              |
        Instância adicional
              |
              v
           app-04
```

A arquitetura utiliza:

- **FastAPI:** disponibilização dos endpoints e processamento das requisições.
- **Docker Compose:** gerenciamento das instâncias independentes da aplicação.
- **NGINX:** distribuição do tráfego entre os serviços configurados.
- **Health check:** verificação periódica da disponibilidade das instâncias.
- **Round Robin:** distribuição sequencial das requisições entre os servidores disponíveis.

Cada instância recebe um identificador próprio por meio da variável de ambiente `INSTANCE_ID`, permitindo reconhecer qual delas atendeu à requisição.

O cabeçalho HTTP `X-Served-By` informa a instância responsável pela resposta. A página `/painel` também exibe o identificador e uma cor específica para facilitar a demonstração visual.

## Como executar

### Pré-requisitos

- Docker
- Docker Compose
- Git

### 1. Configurar o ambiente

Clone o repositório e acesse a pasta do projeto:

```bash
git clone https://github.com/toxyo1/insightia.git
cd insightia
```

Configure a variável `GEMINI_API_KEY` no arquivo `.env`, conforme a configuração exigida pelo back-end.

### 2. Iniciar os serviços

Para iniciar o ambiente configurado:

```bash
docker compose up --build -d
```

Verifique o estado dos contêineres:

```bash
docker compose ps
```

### 3. Acessar a aplicação

- Painel visual: `http://localhost:8080/painel`
- Health check: `http://localhost:8080/health`

O endereço `http://localhost:8080` é o ponto de entrada do balanceador.

## Testes de verificação

### 1. Alternância visual

Acesse `http://localhost:8080/painel` e atualize a página com `Ctrl + F5`. O identificador e a cor devem variar conforme a instância que atende à requisição.

### 2. Verificação por linha de comando

Execute:

```bash
curl -i http://localhost:8080/health
```

A resposta apresenta a instância responsável e o cabeçalho `X-Served-By`.

### 3. Distribuição de 100 requisições

```bash
for i in $(seq 1 100); do
  curl -s http://localhost:8080/health
  echo
done | grep -o '"instance":"[^"]*"' | sort | uniq -c
```

Com três instâncias e distribuição Round Robin, espera-se uma contagem aproximadamente equilibrada entre elas.

### 4. Teste de tolerância a falhas

Pare temporariamente uma instância:

```bash
docker compose stop app-02
```

Acesse o painel e atualize a página. O serviço deverá continuar respondendo pelas instâncias restantes.

Depois, reative a instância:

```bash
docker compose start app-02
```

### 5. Teste de escala

A instância adicional `app-04` pode ser iniciada utilizando o perfil `escala` definido no Docker Compose:

```bash
docker compose --profile escala up -d app-04
```

Com a instância adicional disponível e incluída na configuração do NGINX, reinicie o balanceador para aplicar a configuração:

```bash
docker compose restart nginx
```

Verifique a distribuição entre as quatro instâncias:

```bash
for i in $(seq 1 20); do
  curl -s http://localhost:8080/health
  echo
done | grep -o '"instance":"[^"]*"' | sort | uniq -c
```

### 6. Verificação dos logs

Para visualizar as requisições recebidas pelo balanceador:

```bash
docker compose logs --tail=30 nginx
```

Os registros permitem observar o endereço do servidor de destino, o identificador da instância e o tempo de resposta.

### Acesso direto a uma instância

Para demonstrar que o balanceamento ocorre no NGINX, e não dentro da aplicação, consulte diretamente uma instância pela rede Docker:

```bash
docker compose exec nginx wget -qO- http://app-01:8000/health
```

A resposta deverá identificar exclusivamente `app-01`, sem passar pelo balanceador.

## Possíveis evoluções

- **Escalabilidade horizontal:** adicionar novas instâncias para ampliar a capacidade de atendimento.
- **Sticky sessions:** manter um cliente associado à mesma instância quando a aplicação exigir sessões persistentes.
- **Auto scaling:** automatizar a criação e remoção de instâncias conforme a demanda.
- **Monitoramento:** integrar métricas e ferramentas de observabilidade para acompanhar disponibilidade, tráfego e desempenho.