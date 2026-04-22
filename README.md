# ⚽ Futebol Brasileiro — Dashboard de Análise Exploratória

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

## 📌 Sobre o Projeto

Este projeto foi desenvolvido como parte da **Aula 9 — Visualização de Dados em Python** do curso de **Ciência de Dados** da **UniCEUB**, com o objetivo de praticar análise exploratória de dados (EDA) com um dataset real e publicar o resultado como uma aplicação web interativa.

O dataset utilizado é o **Jogos do Campeonato Brasileiro**, disponível no Kaggle, e cobre as principais competições de futebol que times brasileiros disputam:

- 🏆 **Brasileirão** — Campeonato Brasileiro Série A
- 🌎 **Libertadores** — Principal competição sul-americana
- 🥈 **Sudamericana** — Competição sul-americana secundária
- 🇧🇷 **Copa do Brasil** — Copa nacional

---

## 🖥️ Demonstração

> Após o deploy, substitua o link abaixo pela URL gerada pelo Streamlit Cloud.

🔗 **[Acesse o app ao vivo →](https://share.streamlit.io)**

---

## 📊 Funcionalidades

O dashboard está organizado em **5 seções**, acessíveis pela barra lateral:

| Seção | O que você encontra |
|---|---|
| 📋 **Visão Geral** | Métricas gerais, amostra dos dados e estatísticas descritivas |
| 🏟️ **Times e Competições** | Jogos por competição, top 10 mandantes, média de gols por competição |
| ⚽ **Análise de Gols** | Histograma de distribuição de gols, boxplot por competição |
| 📅 **Evolução Temporal** | Jogos registrados por ano, médias de gols mandante vs visitante ao longo do tempo |
| 🔍 **Relações entre Variáveis** | Scatter plot interativo entre gols mandante e gols visitante |

### Filtros interativos
- **Filtro de competições** — selecione uma ou mais competições para comparar
- **Filtro de período** — ajuste o intervalo de anos analisado
- **Slider de bins** — controle a granularidade do histograma
- **Slider de amostra** — ajuste o tamanho da amostra no scatter plot

---

## 🛠️ Tecnologias Utilizadas

| Biblioteca | Versão | Uso |
|---|---|---|
| `streamlit` | ≥ 1.35 | Interface web e deploy |
| `pandas` | ≥ 2.0 | Leitura, limpeza e manipulação dos dados |
| `matplotlib` | ≥ 3.7 | Criação e personalização de gráficos |
| `seaborn` | ≥ 0.13 | Gráficos estatísticos com visual aprimorado |
| `kagglehub` | ≥ 0.2 | Download automático do dataset via API Kaggle |

---

## 📁 Estrutura do Repositório

```
📦 futebol-brasileiro-eda/
├── app.py              ← Código principal do Streamlit
├── requirements.txt    ← Dependências do projeto
└── README.md           ← Este arquivo
```

---

## 🚀 Como Executar Localmente

### Pré-requisitos

- Python 3.10 ou superior
- Conta no [Kaggle](https://www.kaggle.com) (gratuita)

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/futebol-brasileiro-eda.git
cd futebol-brasileiro-eda
```

### 2. Instale as dependências

```bash
pip install -r requirements.txt
```

### 3. Configure as credenciais do Kaggle

Acesse [kaggle.com/settings](https://www.kaggle.com/settings) → **API** → **Create New Token**.
Um arquivo `kaggle.json` será baixado. Em seguida, configure as variáveis de ambiente:

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

O app abrirá automaticamente em `http://localhost:8501`.

---

## ☁️ Deploy no Streamlit Cloud

### 1. Crie um repositório público no GitHub

Suba os três arquivos (`app.py`, `requirements.txt`, `README.md`) em um repositório **público** no GitHub.

### 2. Acesse o Streamlit Cloud

1. Vá para [share.streamlit.io](https://share.streamlit.io)
2. Faça login com sua conta do GitHub
3. Clique em **New app**
4. Selecione o repositório, a branch (`main`) e o arquivo principal (`app.py`)

### 3. Configure os Secrets

Antes de confirmar o deploy, clique em **Advanced settings → Secrets** e adicione suas credenciais do Kaggle no formato TOML:

```toml
KAGGLE_USERNAME = "seu_usuario_kaggle"
KAGGLE_KEY = "sua_chave_api_kaggle"
```

> ⚠️ **Nunca** commite suas credenciais diretamente no código ou em arquivos do repositório. Use sempre os Secrets do Streamlit Cloud.

### 4. Clique em Deploy

O Streamlit Cloud irá instalar as dependências automaticamente a partir do `requirements.txt` e publicar o app em uma URL pública.

---

## ⚙️ Como o App Funciona

```
Streamlit Cloud
      │
      ▼
Lê KAGGLE_USERNAME e KAGGLE_KEY dos Secrets
      │
      ▼
kagglehub.dataset_download()  ──►  baixa os CSVs do Kaggle
      │
      ▼
pd.concat()  ──►  unifica todos os arquivos em um único DataFrame
      │
      ▼
@st.cache_data  ──►  dados ficam em cache (não baixa de novo a cada clique)
      │
      ▼
Sidebar com filtros  ──►  aplica filtros no DataFrame
      │
      ▼
Gráficos renderizados com Matplotlib/Seaborn  ──►  exibidos com st.pyplot()
```

---

## 📚 Contexto Acadêmico

Este projeto foi desenvolvido seguindo o conteúdo da **Aula 9 — Visualização de Dados em Python** do curso de Ciência de Dados da UniCEUB, que aborda:

- A importância da visualização na Análise Exploratória de Dados (EDA)
- As quatro principais bibliotecas Python para visualização: Pandas Plot, Matplotlib, Seaborn e Plotly
- Quando e como usar cada biblioteca
- Boas práticas na criação de gráficos (título, rótulos de eixos, `tight_layout`, rotação de labels)

---

## 🗂️ Dataset

**Nome:** Jogos do Campeonato Brasileiro  
**Autor:** [ricardomattos05](https://www.kaggle.com/ricardomattos05)  
**Fonte:** [kaggle.com/datasets/ricardomattos05/jogos-do-campeonato-brasileiro](https://www.kaggle.com/datasets/ricardomattos05/jogos-do-campeonato-brasileiro)  
**Licença:** Consultar página do dataset no Kaggle

---

## 👤 Autor

**Henri Felipe Marques Mafra (Charles)**  
Estudante de Ciência de Dados — UniCEUB  
[GitHub](https://github.com/seu-usuario) · [LinkedIn](https://linkedin.com/in/seu-perfil)

---

## 📝 Licença

Este projeto está sob a licença MIT. Consulte o arquivo `LICENSE` para mais detalhes.
