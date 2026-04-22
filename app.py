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

st.set_page_config(page_title="FutStat Pro · Estável", page_icon="⚽", layout="wide")

# ── 2. MOTOR DE DADOS COM COLUNAS GARANTIDAS ─────────────────────────────────
@st.cache_data(show_spinner="⏳ Minerando dados...")
def carregar_dados_blindados():
    import kagglehub
    import glob

    path = kagglehub.dataset_download("ricardomattos05/jogos-do-campeonato-brasileiro")
    caminhos_csv = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
    
    dfs = []
    for arq in caminhos_csv:
        try:
            df_temp = pd.read_csv(arq)
            nome = os.path.basename(arq).lower().replace(".csv", "").replace("_matches", "").replace("_", " ")
            df_temp["competicao"] = nome.strip().title()
            dfs.append(df_temp)
        except:
            continue

    if not dfs: return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)

    # 1. Padronização de nomes
    mapa = {
        'Data': 'data', 'Date': 'data', 'date': 'data', 'ano': 'data', 'Season': 'data',
        'Mandante': 'mandante', 'Home': 'mandante',
        'Visitante': 'visitante', 'Away': 'visitante',
        'Gols Mandante': 'gols_mandante', 'HomeGoals': 'gols_mandante', 'home_score': 'gols_mandante',
        'Gols Visitante': 'gols_visitante', 'AwayGoals': 'gols_visitante', 'away_score': 'gols_visitante'
    }
    df = df.rename(columns=mapa)

    # 2. INICIALIZAÇÃO DE COLUNAS CRÍTICAS (Garante que nunca dê KeyError)
    colunas_obrigatorias = ['mandante', 'visitante', 'gols_mandante', 'gols_visitante', 'competicao']
    for col in colunas_obrigatorias:
        if col not in df.columns:
            df[col] = "Indefinido" if col in ['mandante', 'visitante', 'competicao'] else 0

    # 3. CRIAÇÃO DE MÉTRICAS (Seguro)
    df['gols_mandante'] = pd.to_numeric(df['gols_mandante'], errors='coerce').fillna(0).astype(int)
    df['gols_visitante'] = pd.to_numeric(df['gols_visitante'], errors='coerce').fillna(0).astype(int)
    df['total_gols'] = df['gols_mandante'] + df['gols_visitante']

    # Lógica de Vencedor
    df['vencedor'] = np.select(
        [df['gols_mandante'] > df['gols_visitante'], df['gols_mandante'] < df['gols_visitante']],
        [df['mandante'], df['visitante']], 
        default='Empate'
    )

    # Lógica de Ano
    if 'data' in df.columns:
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        df['_ano'] = df['data'].dt.year.fillna(0).astype(int)
    else:
        df['_ano'] = 0

    return df

df_raw = carregar_dados_blindados()

# ── 3. SIDEBAR ───────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚽ Controles")
    menu = st.radio("Seções", ["🏠 Dashboard", "⚔️ H2H", "🥅 Gols"])
    
    st.divider()
    
    # Filtro de Competição
    todas_comp = sorted(df_raw['competicao'].unique()) if not df_raw.empty else []
    filtro_comp = st.multiselect("Compas", todas_comp, default=todas_comp)
    
    # Filtro de Ano
    anos_disponiveis = sorted(df_raw[df_raw['_ano'] > 0]['_ano'].unique())
    if anos_disponiveis:
        filtro_anos = st.select_slider("Anos", options=anos_disponiveis, value=(min(anos_disponiveis), max(anos_disponiveis)))
    else:
        filtro_anos = (0, 3000)

# ── 4. FILTRAGEM SEGURA ──────────────────────────────────────────────────────
# Criamos uma cópia filtrada garantindo que não estamos tentando acessar nada nulo
mask = df_raw['competicao'].isin(filtro_comp)
if filtro_anos != (0, 3000):
    mask &= df_raw['_ano'].between(filtro_anos[0], filtro_anos[1])

df = df_raw[mask].copy()

# ── 5. INTERFACE DO USUÁRIO ──────────────────────────────────────────────────
if menu == "🏠 Dashboard":
    st.header("📋 Panorama Geral")
    
    if df.empty:
        st.info("Ajuste os filtros para visualizar os dados.")
    else:
        # Métricas em colunas
        m1, m2, m3 = st.columns(3)
        m1.metric("Total de Jogos", len(df))
        m2.metric("Gols Marcados", df['total_gols'].sum())
        m3.metric("Média de Gols", f"{df['total_gols'].mean():.2f}")

        st.divider()
        
        # Gráfico de vitórias (AQUI OCORRIA O ERRO)
        st.subheader("🏆 Top 10 Clubes com Mais Vitórias")
        # Filtramos 'Empate' e contamos os valores na coluna 'vencedor'
        vencedores_contagem = df[df['vencedor'] != 'Empate']['vencedor'].value_counts().head(10)
        
        if not vencedores_contagem.empty:
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(x=vencedores_contagem.values, y=vencedores_contagem.index, palette="viridis", ax=ax)
            ax.set_xlabel("Número de Vitórias")
            st.pyplot(fig)
        else:
            st.write("Sem dados de vitórias para exibir.")

elif menu == "⚔️ H2H":
    st.header("⚔️ Confronto Direto")
    if not df.empty:
        times = sorted(df['mandante'].unique())
        t1 = st.selectbox("Selecione Time 1", times, index=0)
        t2 = st.selectbox("Selecione Time 2", times, index=1)
        
        confrontos = df[
            ((df['mandante'] == t1) & (df['visitante'] == t2)) | 
            ((df['mandante'] == t2) & (df['visitante'] == t1))
        ].sort_values(by='_ano', ascending=False)
        
        st.dataframe(confrontos[['_ano', 'competicao', 'mandante', 'gols_mandante', 'gols_visitante', 'visitante', 'vencedor']])
    else:
        st.error("Dados insuficientes para H2H.")

elif menu == "🥅 Gols":
    st.header("🥅 Distribuição de Gols")
    if not df.empty:
        fig, ax = plt.subplots()
        sns.histplot(df['total_gols'], bins=10, kde=True, color="orange", ax=ax)
        st.pyplot(fig)

st.sidebar.caption(f"Status: {len(df_raw)} linhas processadas.")
