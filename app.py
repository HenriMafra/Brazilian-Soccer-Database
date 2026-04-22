import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# ── 1. CONFIGURAÇÕES KAGGLE ──────────────────────────────────────────────────
if "KAGGLE_USERNAME" in st.secrets:
    os.environ["KAGGLE_USERNAME"] = st.secrets["KAGGLE_USERNAME"]
    os.environ["KAGGLE_KEY"]      = st.secrets["KAGGLE_KEY"]

st.set_page_config(
    page_title="Brasil FutStat Pro · Fix",
    page_icon="⚽",
    layout="wide"
)

# ── 2. TRATAMENTO DE DADOS (BLINDADO) ────────────────────────────────────────
@st.cache_data(show_spinner="⏳ Carregando dados...")
def carregar_dados():
    import kagglehub
    import glob

    path = kagglehub.dataset_download("ricardomattos05/jogos-do-campeonato-brasileiro")
    caminhos_csv = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
    
    dfs = []
    for arq in caminhos_csv:
        try:
            df_temp = pd.read_csv(arq)
            # Limpa o nome da competição
            nome = os.path.basename(arq).lower().replace(".csv", "").replace("_matches", "").replace("_", " ")
            df_temp["competicao"] = nome.strip().title()
            dfs.append(df_temp)
        except:
            continue

    if not dfs: return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)

    # Padronização de nomes de colunas
    mapa = {
        'Data': 'data', 'Date': 'data', 'date': 'data', 'ano': 'data',
        'Mandante': 'mandante', 'Home': 'mandante', 'home_team': 'mandante',
        'Visitante': 'visitante', 'Away': 'visitante', 'away_team': 'visitante',
        'Gols Mandante': 'gols_mandante', 'HomeGoals': 'gols_mandante',
        'Gols Visitante': 'gols_visitante', 'AwayGoals': 'gols_visitante'
    }
    df = df.rename(columns=mapa)

    # --- CRIAÇÃO SEGURA DA COLUNA _ANO ---
    if 'data' in df.columns:
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        df['_ano'] = df['data'].dt.year
    
    # Se não achou data, procura qualquer coluna numérica que pareça um ano (ex: 2024)
    if '_ano' not in df.columns or df['_ano'].isnull().all():
        for col in df.columns:
            if 'ano' in col.lower() or 'season' in col.lower():
                df['_ano'] = pd.to_numeric(df[col], errors='coerce')
                break

    # Garantir que _ano exista (mesmo que seja 0) para evitar o KeyError
    if '_ano' not in df.columns:
        df['_ano'] = 0

    # Conversão de Gols
    for c in ['gols_mandante', 'gols_visitante']:
        if c in df.columns:
            df[c] = pd.to_numeric(df[c], errors='coerce').fillna(0).astype(int)
    
    if 'gols_mandante' in df.columns and 'gols_visitante' in df.columns:
        df['total_gols'] = df['gols_mandante'] + df['gols_visitante']
        df['resultado'] = np.select(
            [df['gols_mandante'] > df['gols_visitante'], df['gols_mandante'] < df['gols_visitante']],
            ['Mandante', 'Visitante'], default='Empate'
        )
        df['vencedor'] = np.where(df['resultado'] == 'Mandante', df['mandante'], 
                         np.where(df['resultado'] == 'Visitante', df['visitante'], 'Empate'))

    return df

df_raw = carregar_dados()

# ── 3. SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("⚽ Dashboard Futebol")
    menu = st.selectbox("Menu", ["🏠 Início", "📊 Clubes", "⚔️ H2H", "🥅 Gols"])
    
    # Filtro de Competição
    todas_comp = sorted(df_raw['competicao'].unique())
    filtro_comp = st.multiselect("Competições", todas_comp, default=todas_comp)
    
    # Filtro de Ano (Seguro)
    anos_validos = df_raw[df_raw['_ano'] > 0]['_ano'].dropna().unique()
    if len(anos_validos) > 0:
        anos_list = sorted(anos_validos.astype(int))
        filtro_anos = st.select_slider("Anos", options=anos_list, value=(min(anos_list), max(anos_list)))
    else:
        filtro_anos = (0, 9999)

# ── 4. APLICAÇÃO DO FILTRO (Onde ocorria o erro) ──────────────────────────────
# Usamos uma lógica que verifica a existência da coluna antes de filtrar
mask = df_raw['competicao'].isin(filtro_comp)

if '_ano' in df_raw.columns and filtro_anos != (0, 9999):
    # Só aplica o filtro de ano se a coluna existir e tiver dados válidos
    mask &= df_raw['_ano'].between(filtro_anos[0], filtro_anos[1])

df = df_raw[mask].copy()

# ── 5. INTERFACE ─────────────────────────────────────────────────────────────
if menu == "🏠 Início":
    st.header("📋 Visão Geral")
    
    if df.empty:
        st.warning("Nenhum dado encontrado para os filtros selecionados.")
    else:
        c1, c2, c3 = st.columns(3)
        c1.metric("Jogos", len(df))
        c2.metric("Gols", df['total_gols'].sum() if 'total_gols' in df.columns else 0)
        c3.metric("Média Gols", f"{df['total_gols'].mean():.2f}" if 'total_gols' in df.columns else "0")

        st.divider()
        st.subheader("Top 10 Vencedores")
        vitorias = df[df['vencedor'] != 'Empate']['vencedor'].value_counts().head(10)
        fig, ax = plt.subplots()
        vitorias.plot(kind='bar', color='seagreen', ax=ax)
        st.pyplot(fig)

elif menu == "📊 Clubes":
    st.header("📊 Ranking por Competição")
    comp = st.selectbox("Selecione", filtro_comp)
    df_c = df[df['competicao'] == comp]
    st.dataframe(df_c.head(50))

elif menu == "⚔️ H2H":
    st.header("⚔️ Confronto Direto")
    times = sorted(df['mandante'].unique())
    t1 = st.selectbox("Time A", times, index=0)
    t2 = st.selectbox("Time B", times, index=1)
    confrontos = df[((df['mandante'] == t1) & (df['visitante'] == t2)) | ((df['mandante'] == t2) & (df['visitante'] == t1))]
    st.table(confrontos[['data', 'mandante', 'gols_mandante', 'gols_visitante', 'visitante']])

elif menu == "🥅 Gols":
    st.header("🥅 Análise de Gols")
    fig, ax = plt.subplots()
    sns.histplot(df['total_gols'], kde=True, ax=ax)
    st.pyplot(fig)

st.sidebar.markdown("---")
st.sidebar.caption(f"Linhas carregadas: {len(df_raw)}")
