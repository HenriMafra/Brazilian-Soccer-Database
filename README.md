# Futebol Brasileiro — Dashboard de Análise Exploratória

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/Streamlit-1.35+-FF4B4B?style=for-the-badge&logo=streamlit&logoColor=white"/>
  <img src="https://img.shields.io/badge/Pandas-2.0+-150458?style=for-the-badge&logo=pandas&logoColor=white"/>
  <img src="https://img.shields.io/badge/Seaborn-0.13+-4C72B0?style=for-the-badge"/>
  <img src="https://img.shields.io/badge/Kaggle-Dataset-20BEFF?style=for-the-badge&logo=kaggle&logoColor=white"/>
</p>

<p align="center">
  Dashboard interativo de visualização de dados construído com Streamlit, aplicando as principais bibliotecas de visualização do ecossistema Python — Pandas Plot, Matplotlib e Seaborn — sobre dados reais do futebol brasileiro.
</p>

---

## Sobre o Projeto

Este projeto foi desenvolvido como parte da **Aula 9 — Visualização de Dados em Python** do curso de **Ciência de Dados** da **UniCEUB**, com o objetivo de praticar análise exploratória de dados (EDA) com um dataset real e publicar o resultado como uma aplicação web interativa.

O dataset utilizado é o **Jogos do Campeonato Brasileiro**, disponível no Kaggle, e cobre as principais competições de futebol que times brasileiros disputam:

- **Brasileirao** — Campeonato Brasileiro Serie A
- **Libertadores** — Principal competicao sul-americana
- **Sudamericana** — Competicao sul-americana secundaria
- **Copa do Brasil** — Copa nacional

---

## Demonstracao

> Apos o deploy, substitua o link abaixo pela URL gerada pelo Streamlit Cloud.

**[Acesse o app ao vivo](https://share.streamlit.io)**

---

## Funcionalidades

O dashboard esta organizado em **5 secoes**, acessiveis pela barra lateral:

| Secao | O que voce encontra |
|---|---|
| **Visao Geral** | Metricas gerais, amostra dos dados e estatisticas descritivas |
| **Times e Competicoes** | Jogos por competicao, top 10 mandantes, media de gols por competicao |
| **Analise de Gols** | Histograma de distribuicao de gols, boxplot por competicao |
| **Evolucao Temporal** | Jogos registrados por ano, medias de gols mandante vs visitante ao longo do tempo |
| **Relacoes entre Variaveis** | Scatter plot interativo entre gols mandante e gols visitante |

### Filtros interativos
- **Filtro de competicoes** — selecione uma ou mais competicoes para comparar
- **Filtro de periodo** — ajuste o intervalo de anos analisado
- **Slider de bins** — controle a granularidade do histograma
- **Slider de amostra** — ajuste o tamanho da amostra no scatter plot

---

## Tecnologias Utilizadas

| Biblioteca | Versao | Uso |
|---|---|---|
| `streamlit` | >= 1.35 | Interface web e deploy |
| `pandas` | >= 2.0 | Leitura, limpeza e manipulacao dos dados |
| `matplotlib` | >= 3.7 | Criacao e personalizacao de graficos |
| `seaborn` | >= 0.13 | Graficos estatisticos com visual aprimorado |
| `kagglehub` | >= 0.2 | Download automatico do dataset via API Kaggle |

---

## Estrutura do Repositorio

```
futebol-brasileiro-eda/
├── app.py              <- Codigo principal do Streamlit
├── requirements.txt    <- Dependencias do projeto
└── README.md           <- Este arquivo
```

---

## Como Executar Localmente

### Pre-requisitos

- Python 3.10 ou superior
- Conta no [Kaggle](https://www.kaggle.com) (gratuita)

### 1. Clone o repositorio

```bash
git clone https://github.com/seu-usuario/futebol-brasileiro-eda.git
cd futebol-brasileiro-eda
```

### 2. Instale as dependencias

```bash
pip install -r requirements.txt
```

### 3. Configure as credenciais do Kaggle

Acesse [kaggle.com/settings](https://www.kaggle.com/settings) → **API** → **Create New Token**.
Um arquivo `kaggle.json` sera baixado. Em seguida, configure as variaveis de ambiente:

**Windows (PowerShell):**
```powershell
$env:KAGGLE_USERNAME="seu_usuario"
$env:KAGGLE_KEY="sua_chave_api"
```

**Linux / macOS:**
```bash
export KAGGLE_USERNAME="seu_usuario"
export KAGGLE_KEY="sua_chave_api"
```

### 4. Inicie o app

```bash
streamlit run app.py
```

O app abrira automaticamente em `http://localhost:8501`.

---

## Deploy no Streamlit Cloud

### 1. Crie um repositorio publico no GitHub

Suba os tres arquivos (`app.py`, `requirements.txt`, `README.md`) em um repositorio **publico** no GitHub.

### 2. Acesse o Streamlit Cloud

1. Va para [share.streamlit.io](https://share.streamlit.io)
2. Faca login com sua conta do GitHub
3. Clique em **New app**
4. Selecione o repositorio, a branch (`main`) e o arquivo principal (`app.py`)

### 3. Configure os Secrets

Antes de confirmar o deploy, clique em **Advanced settings → Secrets** e adicione suas credenciais do Kaggle no formato TOML:

```toml
KAGGLE_USERNAME = "seu_usuario_kaggle"
KAGGLE_KEY = "sua_chave_api_kaggle"
```

> **Nunca** commite suas credenciais diretamente no codigo ou em arquivos do repositorio. Use sempre os Secrets do Streamlit Cloud.

### 4. Clique em Deploy

O Streamlit Cloud ira instalar as dependencias automaticamente a partir do `requirements.txt` e publicar o app em uma URL publica.

---

## Como o App Funciona

```
Streamlit Cloud
      |
      v
Le KAGGLE_USERNAME e KAGGLE_KEY dos Secrets
      |
      v
kagglehub.dataset_download()  -->  baixa os CSVs do Kaggle
      |
      v
pd.concat()  -->  unifica todos os arquivos em um unico DataFrame
      |
      v
@st.cache_data  -->  dados ficam em cache (nao baixa de novo a cada clique)
      |
      v
Sidebar com filtros  -->  aplica filtros no DataFrame
      |
      v
Graficos renderizados com Matplotlib/Seaborn  -->  exibidos com st.pyplot()
```

---

## Contexto Academico

Este projeto foi desenvolvido seguindo o conteudo da **Aula 9 — Visualizacao de Dados em Python** do curso de Ciencia de Dados da UniCEUB, que aborda:

- A importancia da visualizacao na Analise Exploratoria de Dados (EDA)
- As quatro principais bibliotecas Python para visualizacao: Pandas Plot, Matplotlib, Seaborn e Plotly
- Quando e como usar cada biblioteca
- Boas praticas na criacao de graficos (titulo, rotulos de eixos, `tight_layout`, rotacao de labels)

---

## Dataset

**Nome:** Jogos do Campeonato Brasileiro  
**Autor:** [ricardomattos05](https://www.kaggle.com/ricardomattos05)  
**Fonte:** [kaggle.com/datasets/ricardomattos05/jogos-do-campeonato-brasileiro](https://www.kaggle.com/datasets/ricardomattos05/jogos-do-campeonato-brasileiro)  
**Licenca:** Consultar pagina do dataset no Kaggle

---

## Autor

**Henri Felipe Marques Mafra**  
Estudante de Ciencia de Dados — UniCEUB  
[GitHub](https://github.com/seu-usuario) · [LinkedIn](https://linkedin.com/in/seu-perfil)

---

## Licenca

Este projeto esta sob a licenca MIT. Consulte o arquivo `LICENSE` para mais detalhes.
