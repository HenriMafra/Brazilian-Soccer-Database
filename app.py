import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# ── 1. CONFIGURAÇÕES DE AMBIENTE E TEMA ───────────────────────────────────────
if "KAGGLE_USERNAME" in st.secrets:
    os.environ["KAGGLE_USERNAME"] = st.secrets["KAGGLE_USERNAME"]
    os.environ["KAGGLE_KEY"]      = st.secrets["KAGGLE_KEY"]

st.set_page_config(
    page_title="Futebol Brasileiro · EDA Profissional",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilo Global
sns.set_theme(style="whitegrid")
VERDE_CBF   = "#1DB954"
AMARELO_CBF = "#F5C518"
AZUL_CBF    = "#1565C0"
CORES_PALETA = "Spectral"

# ── 2. FUNÇÃO DE CARREGAMENTO (EXPANDIDA E ULTRA-ROBUSTA) ──────────────────────
@st.cache_data(show_spinner="⬇️ Acessando base de dados do Kaggle...")
def carregar_dados_completo():
    import kagglehub
    import glob

    path = kagglehub.dataset_download("ricardomattos05/jogos-do-campeonato-brasileiro")
    caminhos_csv = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
    
    dfs = []
    for caminho in caminhos_csv:
        try:
            temp_df = pd.read_csv(caminho)
            
            # Identificação da competição pelo nome do arquivo
            nome_arq = os.path.basename(caminho).replace(".csv", "").replace("_matches", "").replace("_", " ")
            temp_df["competicao"] = nome_arq.strip().title()
            
            # --- NORMALIZAÇÃO DE COLUNAS (O SEGREDO PARA NÃO ZERAR) ---
            # Mapeamos todas as variações possíveis encontradas no Kaggle
            mapeamento = {
                'Home': 'mandante', 'home_team': 'mandante', 'Mandante': 'mandante',
                'Away': 'visitante', 'away_team': 'visitante', 'Visitante': 'visitante',
                'HomeGoals': 'gols_mandante', 'home_score': 'gols_mandante', 'Gols Mandante': 'gols_mandante',
                'AwayGoals': 'gols_visitante', 'away_score': 'gols_visitante', 'Gols Visitante': 'gols_visitante',
                'Date': 'data_jogo', 'data': 'data_jogo', 'Data': 'data_jogo', 'date': 'data_jogo'
            }
            temp_df.rename(columns=mapeamento, inplace=True)
            dfs.append(temp_df)
        except Exception as e:
            continue

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)

    # --- LIMPEZA E TIPAGEM ---
    # Garantir que colunas de gols sejam numéricas
    for col in ['gols_mandante', 'gols_visitante']:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)
        else:
            df[col] = 0

    # Tratamento de Datas
    if 'data_jogo' in df.columns:
        df['data_jogo'] = pd.to_datetime(df['data_jogo'], errors='coerce')
        # Se falhar, tenta extrair ano de colunas alternativas
        df['_ano'] = df['data_jogo'].dt.year
    
    if '_ano' not in df.columns or df['_ano'].isnull().all():
        # Busca colunas que contenham "ano" ou "season"
        col_ano = next((c for c in df.columns if 'ano' in c.lower() or 'season' in c.lower()), None)
        if col_ano:
            df['_ano'] = pd.to_numeric(df[col_ano], errors='coerce')
        else:
            df['_ano'] = 0

    # --- ENGENHARIA DE ATRIBUTOS (Calculando métricas novas) ---
    df['total_gols'] = df['gols_mandante'] + df['gols_visitante']
    df['saldo'] = df['gols_mandante'] - df['gols_visitante']
    
    # Lógica de Resultado
    condicoes = [
        (df['gols_mandante'] > df['gols_visitante']),
        (df['gols_mandante'] < df['gols_visitante']),
        (df['gols_mandante'] == df['gols_visitante'])
    ]
    resultados = ['Mandante', 'Visitante', 'Empate']
    df['resultado_texto'] = np.select(condicoes, resultados, default='Indefinido')
    
    # Nome do Vencedor
    df['vencedor'] = np.where(df['resultado_texto'] == 'Mandante', df['mandante'],
                     np.where(df['resultado_texto'] == 'Visitante', df['visitante'], 'Empate'))

    # Pontuação (Vitória=3, Empate=1)
    df['pts_mandante'] = np.select([df['resultado_texto'] == 'Mandante', df['resultado_texto'] == 'Empate'], [3, 1], 0)
    df['pts_visitante'] = np.select([df['resultado_texto'] == 'Visitante', df['resultado_texto'] == 'Empate'], [3, 1], 0)

    return df

# ── 3. CARGA INICIAL ──────────────────────────────────────────────────────────
df_raw = carregar_dados_completo()

# ── 4. BARRA LATERAL (SIDEBAR) ────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/pt/4/42/CBF_logo.svg", width=100)
    st.title("⚽ Brasil FutStat")
    st.caption("Análise Exploratória Avançada")
    st.divider()

    secao = st.radio(
        "Navegação",
        [
            "📋 Visão Geral",
            "🏟️ Times e Competições",
            "⚽ Análise de Gols",
            "📅 Evolução Temporal",
            "⚔️ Confronto Direto (H2H)",
            "🔍 Relações e Data Lab"
        ]
    )

    st.divider()
    st.subheader("Filtros Globais")
    
    # Filtro de Competição
    lista_comp = sorted(df_raw['competicao'].unique())
    filtro_comp = st.multiselect("Competições", lista_comp, default=lista_comp[:5])
    
    # Filtro de Anos (Seguro)
    anos_limpos = df_raw[df_raw['_ano'] > 1900]['_ano'].dropna().unique()
    if len(anos_limpos) > 0:
        min_a, max_a = int(min(anos_limpos)), int(max(anos_limpos))
        filtro_anos = st.slider("Período", min_a, max_a, (min_a, max_a))
    else:
        filtro_anos = (0, 2026)

    st.divider()
    st.caption("Dataset via Ricardo Mattos @ Kaggle")

# ── 5. APLICAÇÃO DOS FILTROS ──────────────────────────────────────────────────
df_f = df_raw[df_raw['competicao'].isin(filtro_comp)].copy()
if '_ano' in df_f.columns:
    df_f = df_f[df_f['_ano'].between(filtro_anos[0], filtro_anos[1])]

# Helper para plotar
def exibir(fig):
    st.pyplot(fig, use_container_width=True)
    plt.close(fig)

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 1 — VISÃO GERAL
# ═════════════════════════════════════════════════════════════════════════════
if secao == "📋 Visão Geral":
    st.header("📋 Visão Geral do Dataset")

    # KPIs Principais
    c1, c2, c3, c4 = st.columns(4)
    c1.metric("Total de Jogos", f"{len(df_f):,}")
    c2.metric("Gols Marcados", f"{int(df_f['total_gols'].sum()):,}")
    c3.metric("Média Gols/Jogo", f"{df_f['total_gols'].mean():.2f}")
    c4.metric("Times Únicos", f"{df_f['mandante'].nunique()}")

    st.divider()
    
    col_inf1, col_inf2 = st.columns([2, 1])
    
    with col_inf1:
        st.subheader("🏆 Top 10 Clubes com Mais Vitórias (Histórico)")
        vitorias = df_f[df_f['vencedor'] != 'Empate']['vencedor'].value_counts().head(10)
        if not vitorias.empty:
            fig, ax = plt.subplots(figsize=(10, 5))
            sns.barplot(x=vitorias.values, y=vitorias.index, palette="viridis", ax=ax)
            ax.set_xlabel("Número de Vitórias")
            ax.set_ylabel("Equipe")
            exibir(fig)
        else:
            st.warning("Dados de vitória não encontrados para os filtros selecionados.")

    with col_inf2:
        st.subheader("⚖️ Equilíbrio de Resultados")
        fig, ax = plt.subplots()
        df_f['resultado_texto'].value_counts().plot.pie(
            autopct='%1.1f%%', colors=[VERDE_CBF, AZUL_CBF, 'lightgray'], ax=ax, startangle=140
        )
        ax.set_ylabel("")
        exibir(fig)

    st.subheader("📄 Amostra dos Dados Processados")
    st.dataframe(df_f.head(15), use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 2 — TIMES E COMPETIÇÕES
# ═════════════════════════════════════════════════════════════════════════════
elif secao == "🏟️ Times e Competições":
    st.header("🏟️ Times e Competições")

    tab1, tab2 = st.tabs(["Análise por Competição", "Ranking de Mandantes"])

    with tab1:
        st.subheader("Número de Jogos por Competição")
        contagem_comp = df_f['competicao'].value_counts()
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=contagem_comp.index, y=contagem_comp.values, palette="magma", ax=ax)
        plt.xticks(rotation=45)
        exibir(fig)

    with tab2:
        st.subheader("Top 15 Mandantes mais Ativos")
        mandantes = df_f['mandante'].value_counts().head(15)
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=mandantes.values, y=mandantes.index, color=AZUL_CBF, ax=ax)
        exibir(fig)

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 3 — ANÁLISE DE GOLS
# ═════════════════════════════════════════════════════════════════════════════
elif secao == "⚽ Análise de Gols":
    st.header("⚽ Análise de Gols")

    c1, c2 = st.columns(2)
    
    with c1:
        st.subheader("Distribuição do Total de Gols")
        fig, ax = plt.subplots()
        sns.histplot(df_f['total_gols'], bins=15, kde=True, color="orange", ax=ax)
        exibir(fig)

    with c2:
        st.subheader("Gols Mandante vs Visitante")
        gols_m = df_f['gols_mandante'].sum()
        gols_v = df_f['gols_visitante'].sum()
        fig, ax = plt.subplots()
        ax.pie([gols_m, gols_v], labels=['Mandante', 'Visitante'], autopct='%1.1f%%', colors=['navy', 'crimson'])
        exibir(fig)

    st.divider()
    st.subheader("Maiores Goleadas Encontradas")
    goleadas = df_f.sort_values(by='total_gols', ascending=False).head(10)
    st.table(goleadas[['data_jogo', 'competicao', 'mandante', 'gols_mandante', 'gols_visitante', 'visitante']])

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 4 — EVOLUÇÃO TEMPORAL
# ═════════════════════════════════════════════════════════════════════════════
elif secao == "📅 Evolução Temporal":
    st.header("📅 Evolução Temporal")

    if '_ano' in df_f.columns:
        st.subheader("Média de Gols por Ano")
        media_ano = df_f.groupby('_ano')['total_gols'].mean()
        fig, ax = plt.subplots(figsize=(12, 5))
        media_ano.plot(kind='line', marker='o', color=VERDE_CBF, linewidth=2, ax=ax)
        ax.set_ylabel("Gols por Jogo")
        exibir(fig)

        st.subheader("Quantidade de Jogos Registrados por Ano")
        jogos_ano = df_f.groupby('_ano').size()
        fig, ax = plt.subplots(figsize=(12, 4))
        sns.lineplot(x=jogos_ano.index, y=jogos_ano.values, ax=ax, color="red")
        exibir(fig)
    else:
        st.error("Dados temporais insuficientes para gerar gráficos.")

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 5 — CONFRONTO DIRETO (H2H)
# ═════════════════════════════════════════════════════════════════════════════
elif secao == "⚔️ Confronto Direto (H2H)":
    st.header("⚔️ Confronto Direto (Head-to-Head)")
    
    col1, col2 = st.columns(2)
    time_lista = sorted(df_f['mandante'].unique())
    t1 = col1.selectbox("Time A", time_lista, index=0)
    t2 = col2.selectbox("Time B", time_lista, index=1)

    confrontos = df_f[
        ((df_f['mandante'] == t1) & (df_f['visitante'] == t2)) |
        ((df_f['mandante'] == t2) & (df_f['visitante'] == t1))
    ].sort_values(by='_ano', ascending=False)

    if not confrontos.empty:
        st.write(f"Histórico de **{len(confrontos)}** partidas entre as equipes.")
        
        # Mini Estatística H2H
        v_a = (confrontos['vencedor'] == t1).sum()
        v_b = (confrontos['vencedor'] == t2).sum()
        emp = (confrontos['vencedor'] == 'Empate').sum()
        
        m1, m2, m3 = st.columns(3)
        m1.metric(f"Vitórias {t1}", v_a)
        m2.metric(f"Vitórias {t2}", v_b)
        m3.metric("Empates", emp)

        st.dataframe(confrontos[['_ano', 'competicao', 'mandante', 'gols_mandante', 'gols_visitante', 'visitante', 'vencedor']], use_container_width=True)
    else:
        st.warning("Nenhum confronto direto encontrado entre esses dois times nos filtros atuais.")

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 6 — RELAÇÕES E DATA LAB
# ═════════════════════════════════════════════════════════════════════════════
elif secao == "🔍 Relações e Data Lab":
    st.header("🔍 Laboratório de Dados")

    st.subheader("Correlação entre Variáveis Numéricas")
    cols_num = df_f[['gols_mandante', 'gols_visitante', 'total_gols', '_ano', 'saldo']].corr()
    fig, ax = plt.subplots()
    sns.heatmap(cols_num, annot=True, cmap="coolwarm", fmt=".2f", ax=ax)
    exibir(fig)

    st.divider()
    st.subheader("Exportar Dados Filtrados")
    st.write("Clique no botão abaixo para baixar a planilha com os dados que você filtrou.")
    
    csv = df_f.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Baixar CSV Filtrado",
        data=csv,
        file_name='futebol_brasileiro_filtrado.csv',
        mime='text/csv',
    )

# ── RODAPÉ ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: gray;'>Brasil FutStat Pro · 2026 · Criado com Streamlit & Pandas</div>", 
    unsafe_allow_html=True
)
