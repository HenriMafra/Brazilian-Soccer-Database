import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# ── Streamlit Cloud: injeta credenciais do Kaggle via st.secrets ──────────────
if "KAGGLE_USERNAME" in st.secrets:
    os.environ["KAGGLE_USERNAME"] = st.secrets["KAGGLE_USERNAME"]
    os.environ["KAGGLE_KEY"]      = st.secrets["KAGGLE_KEY"]

# ── Configuração da página ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Futebol Brasileiro · EDA",
    page_icon="⚽",
    layout="wide",
)

# ── Paleta / estilo global ────────────────────────────────────────────────────
sns.set_theme(style="whitegrid")
VERDE   = "#1DB954"
AMARELO = "#F5C518"
AZUL    = "#1565C0"
CORES_COMP = "Set2"

# ─────────────────────────────────────────────────────────────────────────────
# CARREGAMENTO DOS DADOS (cacheado — só baixa uma vez por sessão)
# ─────────────────────────────────────────────────────────────────────────────
@st.cache_data(show_spinner="⬇️ Baixando dataset do Kaggle…")
def carregar_dados():
    import kagglehub

    path = kagglehub.dataset_download(
        "ricardomattos05/jogos-do-campeonato-brasileiro"
    )

    dfs = []
    for arquivo in os.listdir(path):
        if arquivo.endswith(".csv"):
            df_temp = pd.read_csv(os.path.join(path, arquivo))
            df_temp["competicao"] = arquivo.replace(".csv", "")
            dfs.append(df_temp)

    df = pd.concat(dfs, ignore_index=True)

    # ── Tipos ─────────────────────────────────────────────────────────────────
    # Detecta automaticamente a coluna de data
    col_data = next(
        (c for c in df.columns if "data" in c.lower()), None
    )
    if col_data:
        df[col_data] = pd.to_datetime(df[col_data], errors="coerce")
        df["_data"]  = df[col_data]
        df["_ano"]   = df[col_data].dt.year

    for col in ["gols_mandante", "gols_visitante"]:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce")

    if "gols_mandante" in df.columns and "gols_visitante" in df.columns:
        df["total_gols"] = df["gols_mandante"] + df["gols_visitante"]

    return df


df = carregar_dados()

# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.image(
        "https://upload.wikimedia.org/wikipedia/pt/4/42/CBF_logo.svg",
        width=80,
    )
    st.title("⚽ Futebol Brasileiro")
    st.caption("Análise Exploratória de Dados · Aula 9")
    st.divider()

    secao = st.radio(
        "Navegação",
        [
            "📋 Visão Geral",
            "🏟️ Times e Competições",
            "⚽ Análise de Gols",
            "📅 Evolução Temporal",
            "🔍 Relações entre Variáveis",
        ],
    )

    st.divider()

    # Filtros globais
    competicoes_disponiveis = sorted(df["competicao"].dropna().unique())
    filtro_comp = st.multiselect(
        "Filtrar competições",
        competicoes_disponiveis,
        default=competicoes_disponiveis,
    )

    if "_ano" in df.columns:
        ano_min = int(df["_ano"].min())
        ano_max = int(df["_ano"].max())
        filtro_anos = st.slider(
            "Período",
            ano_min, ano_max,
            (ano_min, ano_max),
        )
    else:
        filtro_anos = None

    st.caption("Dataset: [Kaggle ↗](https://www.kaggle.com/datasets/ricardomattos05/jogos-do-campeonato-brasileiro)")

# ── Aplica filtros ─────────────────────────────────────────────────────────
df_f = df[df["competicao"].isin(filtro_comp)].copy()
if filtro_anos and "_ano" in df_f.columns:
    df_f = df_f[df_f["_ano"].between(filtro_anos[0], filtro_anos[1])]


# ─────────────────────────────────────────────────────────────────────────────
# helper para exibir gráficos matplotlib no Streamlit
# ─────────────────────────────────────────────────────────────────────────────
def show(fig):
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)


# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 1 — VISÃO GERAL
# ═════════════════════════════════════════════════════════════════════════════
if secao == "📋 Visão Geral":
    st.header("📋 Visão Geral do Dataset")

    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total de Jogos",       f"{len(df_f):,}")
    col2.metric("Competições",          df_f["competicao"].nunique())
    if "mandante" in df_f.columns:
        col3.metric("Times Únicos",
                    df_f["mandante"].nunique())
    if "_ano" in df_f.columns:
        col4.metric("Anos cobertos",
                    f"{int(df_f['_ano'].min())} – {int(df_f['_ano'].max())}")

    st.divider()
    st.subheader("Amostra dos dados")
    st.dataframe(df_f.head(20), use_container_width=True)

    st.subheader("Estatísticas descritivas")
    st.dataframe(df_f.describe(), use_container_width=True)


# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 2 — TIMES E COMPETIÇÕES
# ═════════════════════════════════════════════════════════════════════════════
elif secao == "🏟️ Times e Competições":
    st.header("🏟️ Times e Competições")

    # ── Gráfico 1: Jogos por competição (Pandas Plot → Matplotlib) ────────────
    st.subheader("Gráfico 1 — Jogos por Competição")
    st.caption("Pandas Plot · `value_counts().plot(kind='bar')`")

    jogos_comp = df_f["competicao"].value_counts()

    fig, ax = plt.subplots(figsize=(10, 4))
    jogos_comp.plot(kind="bar", ax=ax, color=VERDE)
    ax.set_title("Número de Jogos por Competição", fontsize=13)
    ax.set_xlabel("Competição")
    ax.set_ylabel("Número de Jogos")
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    show(fig)

    # ── Gráfico 2: Top 10 mandantes (Matplotlib) ──────────────────────────────
    if "mandante" in df_f.columns:
        st.subheader("Gráfico 2 — Top 10 Times como Mandante")
        st.caption("Matplotlib · personalização completa")

        top10 = df_f["mandante"].value_counts().head(10)

        fig, ax = plt.subplots(figsize=(10, 4))
        top10.plot(kind="bar", ax=ax, color=AZUL)
        ax.set_title("Top 10 Times com Mais Jogos em Casa", fontsize=13)
        ax.set_xlabel("Time")
        ax.set_ylabel("Jogos")
        ax.tick_params(axis="x", rotation=40)
        fig.tight_layout()
        show(fig)

    # ── Gráfico 3: Seaborn barplot ────────────────────────────────────────────
    if "total_gols" in df_f.columns:
        st.subheader("Gráfico 3 — Média de Gols por Competição (Seaborn)")
        st.caption("Seaborn · `sns.barplot` com `as_index=False`")

        media_gols = (
            df_f.groupby("competicao", as_index=False)["total_gols"].mean()
        )

        fig, ax = plt.subplots(figsize=(10, 4))
        sns.barplot(
            data=media_gols,
            x="competicao",
            y="total_gols",
            palette=CORES_COMP,
            ax=ax,
        )
        ax.set_title("Média de Gols por Partida — por Competição", fontsize=13)
        ax.set_xlabel("Competição")
        ax.set_ylabel("Média de Gols")
        ax.tick_params(axis="x", rotation=35)
        fig.tight_layout()
        show(fig)


# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 3 — ANÁLISE DE GOLS
# ═════════════════════════════════════════════════════════════════════════════
elif secao == "⚽ Análise de Gols":
    st.header("⚽ Análise de Gols")

    if "total_gols" not in df_f.columns:
        st.warning("Colunas `gols_mandante` / `gols_visitante` não encontradas.")
        st.stop()

    # ── Gráfico 4: Histograma ─────────────────────────────────────────────────
    st.subheader("Gráfico 4 — Distribuição de Gols por Partida")
    st.caption("Seaborn · `sns.histplot` com `kde=True`")

    bins = st.slider("Número de bins", 5, 30, 15)

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.histplot(
        df_f["total_gols"].dropna(),
        bins=bins,
        kde=True,
        color="salmon",
        ax=ax,
    )
    ax.set_title("Distribuição do Total de Gols por Partida", fontsize=13)
    ax.set_xlabel("Total de Gols")
    ax.set_ylabel("Frequência")
    fig.tight_layout()
    show(fig)

    # ── Gráfico 5: Boxplot ────────────────────────────────────────────────────
    st.subheader("Gráfico 5 — Boxplot de Gols por Competição")
    st.caption("Seaborn · `sns.boxplot` — identifica outliers (placar alto)")

    fig, ax = plt.subplots(figsize=(10, 4))
    sns.boxplot(
        data=df_f,
        x="competicao",
        y="total_gols",
        palette=CORES_COMP,
        ax=ax,
    )
    ax.set_title("Boxplot do Total de Gols por Competição", fontsize=13)
    ax.set_xlabel("Competição")
    ax.set_ylabel("Total de Gols")
    ax.tick_params(axis="x", rotation=35)
    fig.tight_layout()
    show(fig)


# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 4 — EVOLUÇÃO TEMPORAL
# ═════════════════════════════════════════════════════════════════════════════
elif secao == "📅 Evolução Temporal":
    st.header("📅 Evolução Temporal")

    if "_ano" not in df_f.columns:
        st.warning("Coluna de data não encontrada no dataset.")
        st.stop()

    # ── Gráfico 6: Jogos por ano ──────────────────────────────────────────────
    st.subheader("Gráfico 6 — Jogos Registrados por Ano")
    st.caption("Pandas Plot · `kind='line'` com `marker='o'`")

    jogos_ano = df_f.groupby("_ano")["competicao"].count()

    fig, ax = plt.subplots(figsize=(12, 4))
    jogos_ano.plot(kind="line", marker="o", color="teal", ax=ax)
    ax.set_title("Número de Jogos Registrados por Ano", fontsize=13)
    ax.set_xlabel("Ano")
    ax.set_ylabel("Número de Jogos")
    ax.grid(axis="y", linestyle="--", alpha=0.5)
    fig.tight_layout()
    show(fig)

    # ── Gráfico 7: Mandante vs Visitante ──────────────────────────────────────
    if "gols_mandante" in df_f.columns and "gols_visitante" in df_f.columns:
        st.subheader("Gráfico 7 — Média de Gols por Ano: Mandante vs Visitante")
        st.caption("Pandas Plot · `groupby + unstack` para duas linhas")

        gols_ano = (
            df_f.groupby("_ano")[["gols_mandante", "gols_visitante"]]
            .mean()
        )

        fig, ax = plt.subplots(figsize=(12, 4))
        gols_ano.plot(kind="line", marker="o", ax=ax,
                      color=[AZUL, AMARELO])
        ax.set_title(
            "Média de Gols por Ano — Mandante vs Visitante", fontsize=13
        )
        ax.set_xlabel("Ano")
        ax.set_ylabel("Média de Gols")
        ax.legend(["Mandante", "Visitante"])
        ax.grid(axis="y", linestyle="--", alpha=0.5)
        fig.tight_layout()
        show(fig)


# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 5 — RELAÇÕES ENTRE VARIÁVEIS
# ═════════════════════════════════════════════════════════════════════════════
elif secao == "🔍 Relações entre Variáveis":
    st.header("🔍 Relações entre Variáveis")

    if "gols_mandante" not in df_f.columns or "gols_visitante" not in df_f.columns:
        st.warning("Colunas de gols não encontradas.")
        st.stop()

    # ── Gráfico 8: Scatter ────────────────────────────────────────────────────
    st.subheader("Gráfico 8 — Gols Mandante × Gols Visitante")
    st.caption("Seaborn · `sns.scatterplot` com `hue` por competição")

    n_amostra = st.slider("Tamanho da amostra", 500, 5000, 2000, step=500)
    df_clean = df_f.dropna(subset=["gols_mandante", "gols_visitante"])
    n_amostra = min(n_amostra, len(df_clean))
    amostra = df_clean.sample(n_amostra, random_state=42)

    fig, ax = plt.subplots(figsize=(9, 5))
    sns.scatterplot(
        data=amostra,
        x="gols_mandante",
        y="gols_visitante",
        hue="competicao",
        palette=CORES_COMP,
        alpha=0.5,
        ax=ax,
    )
    ax.set_title("Gols Mandante × Gols Visitante", fontsize=13)
    ax.set_xlabel("Gols Mandante")
    ax.set_ylabel("Gols Visitante")
    fig.tight_layout()
    show(fig)

    st.info(
        "💡 Cada ponto é uma partida. A diagonal imaginável (x=y) representa empate. "
        "Pontos acima dela = mais gols do visitante."
    )
