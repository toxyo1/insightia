# Insightia — Qualidade de Dados e Observabilidade em Sistemas Distribuídos

## 1. Sobre o projeto

O **Insightia** é uma plataforma de análise, qualidade e padronização de dados desenvolvida em Python, FastAPI e Pandas, com integração à API Google Gemini para geração de relatórios descritivos.

A aplicação permite analisar arquivos CSV, identificar problemas de qualidade de dados, calcular indicadores e realizar operações de limpeza e padronização.

Para a disciplina de **Sistemas Distribuídos**, o Insightia foi adaptado para demonstrar conceitos de **observabilidade por meio de métricas, dashboards e alertas**, utilizando Prometheus, Grafana e Alertmanager.

A implementação busca responder a uma questão operacional:

**Como identificar automaticamente falhas em sistemas distribuídos antes que os usuários precisem comunicar o problema?**

Para isso, foi construída uma arquitetura com duas APIs independentes, comunicação HTTP, coleta automática de métricas, visualização gráfica e alertas baseados na taxa de erros.

---

## 2. Objetivos

### Objetivo geral

Demonstrar a aplicação de técnicas de observabilidade em sistemas distribuídos, permitindo monitorar o comportamento de serviços, detectar falhas e acompanhar sua recuperação.

### Objetivos específicos

- Instrumentar APIs para coleta de métricas HTTP.
- Implementar a comunicação entre dois serviços independentes.
- Coletar métricas automaticamente utilizando Prometheus.
- Construir dashboards baseados no método RED.
- Configurar alertas para taxas elevadas de erros.
- Simular falhas HTTP 500 de forma controlada.
- Demonstrar a propagação de falhas entre serviços.
- Identificar problemas por meio de dados de monitoramento.
- Acompanhar a recuperação dos serviços.

---

## 3. Funcionalidades originais do Insightia

A plataforma mantém suas funcionalidades de análise e tratamento de dados.

### 3.1. Perfilamento de dados

A aplicação recebe arquivos CSV e utiliza Pandas para calcular indicadores, como:

- Quantidade de linhas e colunas.
- Valores ausentes.
- Registros duplicados.
- Score de qualidade dos dados.

### 3.2. Diagnóstico com Inteligência Artificial

O Insightia utiliza a API Google Gemini para produzir relatórios descritivos a partir das métricas calculadas.

O processamento numérico é realizado por Pandas, enquanto a IA é utilizada para interpretar e descrever os resultados.

### 3.3. Limpeza e padronização

A aplicação oferece operações de tratamento dos arquivos:

- Remoção de registros duplicados.
- Preenchimento de valores nulos.
- Padronização dos nomes das colunas.
- Exportação do CSV processado.

---

## 4. Arquitetura da solução de observabilidade

A aplicação de demonstração utiliza serviços independentes executados em contêineres Docker.

### Componentes

**Gateway API:** serviço intermediário que recebe requisições e consulta o Insightia pela rede. Em caso de falha HTTP 500 no Insightia, responde com HTTP 502.

**Insightia API:** serviço principal da aplicação, desenvolvido com FastAPI. Disponibiliza as funcionalidades de análise de dados e endpoints de monitoramento.

**Gerador de carga:** contêiner que realiza requisições HTTP continuamente, simulando usuários acessando o sistema.

**Prometheus:** coleta periodicamente as métricas das duas APIs e avalia as regras de alerta.

**Grafana:** apresenta dashboards para acompanhamento das requisições, erros e latência.

**Alertmanager:** recebe e gerencia os alertas encaminhados pelo Prometheus.

### Fluxo da arquitetura

```text
              GERADOR DE CARGA
                      |
                      | HTTP
                      v
                GATEWAY API
                      |
                      | HTTP
                      v
                INSIGHTIA API


          COLETA DE MÉTRICAS (PULL)
                      |
           +----------+----------+
           |                     |
           v                     v
     GATEWAY /metrics      INSIGHTIA /metrics
           |                     |
           +----------+----------+
                      |
                      v
                  PROMETHEUS
                      |
              +-------+-------+
              |               |
              v               v
           GRAFANA        ALERTMANAGER
         Dashboards         Alertas
```

O Prometheus consulta diretamente o endpoint `/metrics` das duas APIs. Não depende do Gateway para coletar as métricas do Insightia.

---

## 5. Tecnologias utilizadas

| Tecnologia | Utilização |
|---|---|
| Python | Desenvolvimento dos serviços |
| FastAPI | APIs REST |
| Pandas | Processamento de arquivos CSV |
| Google Gemini | Relatórios descritivos com IA |
| HTTPX | Comunicação HTTP entre APIs |
| Prometheus Client | Instrumentação e exposição de métricas |
| Prometheus | Coleta, armazenamento e consultas de métricas |
| PromQL | Consultas às séries temporais |
| Grafana | Dashboards de observabilidade |
| Alertmanager | Gerenciamento de alertas |
| Docker | Conteinerização |
| Docker Compose | Orquestração local dos serviços |
| HTML, CSS e JavaScript | Interface web original do Insightia |

A interface web original possui uma estrutura independente. O ambiente Docker Compose do seminário concentra-se nas APIs e nas ferramentas de monitoramento.

---

## 6. Estrutura do projeto

```text
insightia/
|
|-- backend/
|   |-- main.py
|   |-- requirements.txt
|   |-- Dockerfile
|   |-- .env
|
|-- gateway/
|   |-- main.py
|   |-- requirements.txt
|   |-- Dockerfile
|
|-- frontend/
|
|-- monitoring/
|   |-- prometheus.yml
|   |-- rules.yml
|   |-- alertmanager.yml
|   |-- grafana-datasource.yml
|   |-- grafana-dashboards.yml
|   |-- red-dashboard.json
|
|-- data/
|-- docker-compose.yml
|-- README.md
```

O arquivo `backend/.env` é utilizado localmente e não deve ser publicado no repositório.

---

## 7. Pré-requisitos

Para executar a demonstração são necessários:

- Git.
- Docker Desktop com Docker Compose.
- Terminal PowerShell, Bash ou equivalente.
- Navegador web.
- Portas 8001, 8002, 3000, 9090 e 9093 disponíveis.

A demonstração foi preparada e testada localmente em Windows com Docker Desktop.

Não é necessário instalar as dependências Python diretamente no sistema operacional, pois elas são instaladas dentro dos contêineres.

---

## 8. Como executar o projeto

### 8.1. Clonar o repositório

No terminal, execute:

```powershell
git clone -b feat/monitoramento-prometheus-grafana --single-branch https://github.com/toxyo1/insightia.git
```

Entre na pasta:

```powershell
cd insightia
```

**Importante:** esta documentação descreve a versão ampliada do projeto, que inclui o Gateway e as configurações de observabilidade. Esses arquivos precisam estar publicados no repositório para que a execução a partir de um clone novo reproduza o ambiente descrito.

### 8.2. Configurar as variáveis de ambiente

Crie o arquivo:

`backend/.env`

Adicione:

```dotenv
GEMINI_API_KEY=SUA_CHAVE_AQUI
```

O backend atualmente exige que a variável `GEMINI_API_KEY` esteja definida na inicialização.

Para testar apenas a observabilidade, pode-se utilizar uma chave fictícia de desenvolvimento. Nesse caso, as funcionalidades que dependem da API Gemini não funcionarão corretamente.

Para utilizar os relatórios gerados por IA, configure uma chave válida.

**Nunca publique chaves reais ou arquivos `.env` no GitHub.**

### 8.3. Validar o Docker Compose

Na raiz do projeto, execute:

```powershell
docker compose config --quiet
```

A ausência de mensagens de erro indica que a configuração foi validada.

### 8.4. Iniciar os serviços

Execute:

```powershell
docker compose up -d --build
```

Esse comando constrói as imagens necessárias e inicia os serviços em segundo plano.

### 8.5. Verificar os contêineres

Execute:

```powershell
docker compose ps -a
```

Os seis serviços esperados são:

- `insightia_api`
- `gateway`
- `carga`
- `prometheus`
- `alertmanager`
- `grafana`

Os contêineres devem apresentar estado `Up`.

Para consultar os logs:

```powershell
docker compose logs --tail=50
```

---

## 9. Endereços dos serviços

| Serviço | Endereço local |
|---|---|
| Insightia API | `http://127.0.0.1:8001` |
| Métricas do Insightia | `http://127.0.0.1:8001/metrics` |
| Documentação da API | `http://127.0.0.1:8001/docs` |
| Gateway API | `http://127.0.0.1:8002` |
| Métricas do Gateway | `http://127.0.0.1:8002/metrics` |
| Prometheus | `http://127.0.0.1:9090` |
| Targets do Prometheus | `http://127.0.0.1:9090/targets` |
| Alertas do Prometheus | `http://127.0.0.1:9090/alerts` |
| Grafana | `http://127.0.0.1:3000` |
| Alertmanager | `http://127.0.0.1:9093` |

As portas externas estão configuradas para acesso pelo computador local.

Dentro da rede Docker, as duas APIs continuam utilizando a porta 8000.

---

## 10. Métricas implementadas

A solução utiliza métricas do Prometheus para medir o comportamento das aplicações.

### 10.1. Counter

O Counter é uma métrica cumulativa utilizada para contabilizar eventos.

Exemplos:

`http_requests_total`

Contabiliza as requisições recebidas pelo Insightia.

`gateway_http_requests_total`

Contabiliza as requisições recebidas pelo Gateway.

Essas métricas possuem rótulos que permitem distinguir métodos, rotas e códigos de resposta HTTP.

### 10.2. Histogram

O Histogram registra observações em faixas de valores, permitindo analisar distribuições e estimar percentis.

Exemplos:

`http_request_duration_seconds`

`gateway_http_request_duration_seconds`

Essas métricas permitem calcular o tempo de resposta p50 e p95.

### 10.3. Gauge

Gauge representa valores que podem aumentar ou diminuir, como consumo de memória ou número de conexões ativas.

Embora a instrumentação personalizada do projeto utilize principalmente Counter e Histogram, o cliente Prometheus também expõe métricas de processo, como:

`process_resident_memory_bytes`

Essa métrica informa o consumo de memória residente do processo.

---

## 11. Método RED e dashboards

O método RED acompanha três indicadores fundamentais de serviços:

**Rate:** taxa de requisições processadas.

**Errors:** quantidade ou proporção de requisições que resultaram em erro.

**Duration:** distribuição dos tempos de resposta.

O dashboard do projeto apresenta sete painéis:

| Painel | Indicador |
|---|---|
| Insightia — Rate | Requisições por segundo |
| Insightia — Errors | Percentual de erros HTTP 5xx |
| Insightia — Duration | Latência p95 |
| Gateway — Rate | Requisições por segundo |
| Gateway — Errors | Percentual de erros HTTP 5xx |
| Gateway — Duration | Latência p95 |
| Propagação de falhas | Comparação entre erros HTTP 500 e HTTP 502 |

O último painel permite visualizar a propagação das falhas entre serviços.

### Consultas PromQL de exemplo

Taxa de requisições do Insightia:

```promql
sum(rate(http_requests_total{job="insightia"}[1m]))
```

Taxa de erros HTTP 500 no Insightia:

```promql
sum(rate(http_requests_total{job="insightia",status="500"}[1m]))
```

Taxa de erros HTTP 502 no Gateway:

```promql
sum(rate(gateway_http_requests_total{job="gateway",status="502"}[1m]))
```

Latência p95 do Insightia:

```promql
histogram_quantile(
  0.95,
  sum by (le) (
    rate(http_request_duration_seconds_bucket{job="insightia"}[1m])
  )
)
```

---

## 12. Cenário de demonstração de falhas

### Problema simulado

O sistema funciona normalmente, mas uma falha na API Insightia passa a provocar respostas HTTP 500.

Como o Gateway depende do Insightia, parte das requisições recebidas pelo Gateway também começa a falhar.

O objetivo é detectar o problema por meio de métricas e visualizar seu impacto nos dois serviços.

### Etapa 1 — Estado normal

Primeiro, garanta que a simulação esteja desligada:

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/demo/falha/0"
```

Teste a comunicação com o Gateway:

```powershell
Invoke-RestMethod "http://127.0.0.1:8002/"
```

O resultado esperado é uma resposta HTTP 200 indicando comunicação bem-sucedida.

No Grafana, verifique que os indicadores de erros estão próximos de 0%.

### Etapa 2 — Provocar a falha

Execute:

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/demo/falha/0.3"
```

O parâmetro `0.3` configura uma probabilidade de 30% de falha nas requisições elegíveis do Insightia.

### Etapa 3 — Testar a propagação

Execute 30 requisições ao Gateway:

```powershell
1..30 | ForEach-Object {
    curl.exe -s -o NUL -w "%{http_code}" "http://127.0.0.1:8002/"
} | Group-Object | Select-Object Count, Name
```

O resultado esperado apresenta uma combinação de respostas HTTP 200 e HTTP 502.

A quantidade exata de falhas varia porque a simulação é probabilística.

### Etapa 4 — Observar o Grafana

Abra o dashboard:

**Insightia - Observabilidade de Sistemas Distribuidos**

Selecione o intervalo **Last 5 minutes** e configure atualização automática de 5 segundos.

Observe os gráficos:

- Insightia — Errors (%).
- Gateway — Errors (%).
- Propagação de falhas — Insightia 500 × Gateway 502.

O aumento dos erros nos dois serviços demonstra o impacto da falha na aplicação distribuída.

### Etapa 5 — Verificar o alerta

Acesse:

`http://127.0.0.1:9090/alerts`

Procure pelo alerta `TaxaDeErrosAlta`.

A regra monitora a proporção de respostas HTTP 5xx e dispara quando a taxa ultrapassa 5% durante 30 segundos contínuos.

O alerta pode passar pelos seguintes estados:

- `Inactive`: condição não atendida.
- `Pending`: condição detectada, aguardando o tempo configurado.
- `Firing`: condição persistiu e o alerta foi disparado.

Depois, acesse:

`http://127.0.0.1:9093`

Verifique se o Alertmanager recebeu o alerta ativo.

A configuração atual utiliza um receptor de demonstração e não realiza envio de notificações por e-mail.

### Etapa 6 — Recuperar o sistema

Execute:

```powershell
Invoke-RestMethod "http://127.0.0.1:8001/demo/falha/0"
```

A falha artificial será desativada.

Acompanhe a redução dos erros no Grafana e a resolução do alerta no Prometheus.

Como as consultas utilizam janelas de um minuto, a taxa não necessariamente retorna a zero imediatamente.

---

## 13. Regra de alerta

A regra principal do projeto é denominada:

`TaxaDeErrosAlta`

Sua condição é:

```promql
(
  sum(rate(http_requests_total{status=~"5.."}[1m]))
  or vector(0)
)
/
sum(rate(http_requests_total[1m]))
> 0.05
```

A expressão verifica se mais de 5% das requisições do Insightia retornaram erros HTTP 5xx.

O parâmetro `for: 30s` exige que a condição permaneça verdadeira durante 30 segundos.

O intervalo de coleta e avaliação configurado no Prometheus é de 5 segundos.

A utilização de uma janela temporal e de um período de persistência ajuda a reduzir alertas provocados por oscilações muito breves.

---

## 14. Diagnóstico observado

Nos testes locais realizados, a simulação de falha foi ativada e produziu erros HTTP 500 no Insightia.

Em um teste de 30 requisições diretas à API, foram observadas:

| Resultado | Quantidade |
|---|---:|
| HTTP 200 | 23 |
| HTTP 500 | 7 |
| Total | 30 |
| Taxa observada de erros | 23,3% |

O dashboard também mostrou elevação da taxa de erros dos serviços, alcançando valores próximos de 30%.

Após a introdução do Gateway, foi possível observar erros HTTP 500 no Insightia e HTTP 502 no Gateway em períodos correspondentes, evidenciando a propagação da falha.

O alerta `TaxaDeErrosAlta` alcançou o estado `Firing` durante os testes.

Após a desativação da falha artificial, os indicadores dos dois serviços retornaram a zero.

Esses resultados correspondem aos testes locais realizados durante o desenvolvimento. Os valores podem variar em novas execuções.

---

## 15. Análise crítica e limitações

A implementação proporciona visibilidade operacional, mas apresenta limitações.

### Limitações das métricas HTTP

Um serviço pode retornar HTTP 200 mesmo quando uma funcionalidade interna não é concluída corretamente.

No Insightia, uma falha na geração do relatório pelo Gemini pode resultar em uma resposta HTTP 200 contendo uma mensagem de aviso.

Nesse cenário, o dashboard RED baseado apenas em status HTTP não identifica diretamente a falha da integração com IA.

Uma melhoria futura seria adicionar métricas específicas para contabilizar erros nas chamadas ao Gemini.

### Limitações da demonstração distribuída

O Gateway implementado é uma API intermediária simples que consulta a rota inicial do Insightia.

Ele não substitui o processamento real dos arquivos CSV nem encaminha as operações de análise e limpeza.

A arquitetura foi construída para demonstrar comunicação entre serviços, falhas em dependências e observabilidade.

### Custos e overhead

A coleta de métricas gera consumo adicional de processamento, memória, armazenamento e tráfego de rede.

O impacto depende da quantidade de serviços, frequência de coleta, quantidade de séries temporais e número de rótulos utilizados.

Neste projeto, os intervalos curtos foram escolhidos para facilitar a visualização durante a demonstração.

### Alert fatigue

Alertas excessivos podem prejudicar a identificação de incidentes importantes.

Por isso, é necessário definir limites adequados, priorizar condições relevantes e evitar notificações para pequenas oscilações temporárias.

### Limitações do ambiente

O projeto foi preparado para demonstração local.

A configuração de acesso anônimo ao Grafana foi mantida com papel `Viewer`, e as portas publicadas pelo Docker foram restritas ao endereço local.

Para uso em produção, seriam necessários controles adicionais de autenticação, autorização, segurança, persistência e disponibilidade.

---

## 16. Como encerrar a aplicação

Para interromper e remover os contêineres do projeto:

```powershell
docker compose down
```

Para consultar o estado dos serviços:

```powershell
docker compose ps -a
```

O comando `docker compose down`, sem a opção `-v`, não solicita a remoção dos volumes nomeados.

---

## 17. Referências

- Documentação oficial do Prometheus: https://prometheus.io/docs/
- PromQL: https://prometheus.io/docs/prometheus/latest/querying/basics/
- Prometheus Alerting: https://prometheus.io/docs/alerting/latest/
- Grafana: https://grafana.com/docs/grafana/latest/
- FastAPI: https://fastapi.tiangolo.com/
- Docker Compose: https://docs.docker.com/compose/
- Google Site Reliability Engineering: https://sre.google/books/
- Brendan Gregg — USE Method: https://www.brendangregg.com/usemethod.html

---

## 18. Contexto acadêmico

Projeto adaptado para o seminário **Métricas, Dashboards e Alertas**, da disciplina de Sistemas Distribuídos.

A demonstração tem finalidade didática e busca evidenciar como métricas, visualizações e alertas podem apoiar a identificação e o diagnóstico de falhas em aplicações distribuídas.

O trabalho parte da aplicação Insightia existente e acrescenta instrumentação, monitoramento e um serviço intermediário para reprodução de falhas.

As contribuições individuais dos integrantes e o uso de ferramentas de IA como apoio ao desenvolvimento devem ser declarados no relatório acadêmico, conforme as orientações da disciplina.
