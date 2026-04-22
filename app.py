import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# ── 1. CONFIGURAÇÕES INICIAIS E SEGURANÇA ─────────────────────────────────────
# Injeta credenciais do Kaggle via st.secrets (necessário para Streamlit Cloud)
if "KAGGLE_USERNAME" in st.secrets:
    os.environ["KAGGLE_USERNAME"] = st.secrets["KAGGLE_USERNAME"]
    os.environ["KAGGLE_KEY"]      = st.secrets["KAGGLE_KEY"]

st.set_page_config(
    page_title="Brasil FutStat Pro · Advanced EDA",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilização Global
sns.set_theme(style="whitegrid")
VERDE_BRASIL = "#009739"
AMARELO_BRASIL = "#FEDD00"
AZUL_BRASIL = "#002776"
PALETA_QUENTE = "YlOrRd"

# ── 2. MOTOR DE PROCESSAMENTO DE DADOS ────────────────────────────────────────
@st.cache_data(show_spinner="⏳ Minerando e tratando dados do Kaggle...")
def carregar_e_limpar_dados():
    import kagglehub
    import glob

    # Download do Dataset
    path = kagglehub.dataset_download("ricardomattos05/jogos-do-campeonato-brasileiro")
    caminhos_csv = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
    
    dfs = []
    for arq in caminhos_csv:
        try:
            df_temp = pd.read_csv(arq)
            
            # --- CORREÇÃO DOS NOMES (Sua dúvida anterior) ---
            # Transformamos em minúsculo, removemos lixo e aplicamos Title Case
            nome_base = os.path.basename(arq).lower().replace(".csv", "")
            nome_limpo = nome_base.replace("_matches", "").replace("_", " ").strip().title()
            df_temp["competicao"] = nome_limpo
            
            dfs.append(df_temp)
        except Exception as e:
            continue

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)

    # --- MAPEAMENTO INTELIGENTE DE COLUNAS ---
    # Isso evita o erro de "KeyError" se o CSV mudar os nomes das colunas
    mapa_colunas = {
        'Data': 'data', 'Date': 'data', 'date': 'data', 'ano': 'data', 'Season': 'data',
        'Mandante': 'mandante', 'Home': 'mandante', 'home_team': 'mandante',
        'Visitante': 'visitante', 'Away': 'visitante', 'away_team': 'visitante',
        'Gols Mandante': 'gols_mandante', 'HomeGoals': 'gols_mandante', 'home_score': 'gols_mandante',
        'Gols Visitante': 'gols_visitante', 'AwayGoals': 'gols_visitante', 'away_score': 'gols_visitante'
    }
    df = df.rename(columns=mapa_colunas)

    # --- TRATAMENTO DE DATAS E CRIAÇÃO DO _ANO ---
    if 'data' in df.columns:
        # Converte para datetime e remove datas nulas
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        df = df.dropna(subset=['data'])
        df['_ano'] = df['data'].dt.year
        df['_mes'] = df['data'].dt.month
        df['_dia_semana'] = df['data'].dt.day_name()
    
    # Segurança caso não exista data mas exista uma coluna "Ano" perdida
    if '_ano' not in df.columns:
        col_reserva = next((c for c in df.columns if 'ano' in c.lower()), None)
        if col_reserva:
            df['_ano'] = pd.to_numeric(df[col_reserva], errors='coerce')

    # --- CONVERSÃO DE GOLS ---
    cols_gols = ['gols_mandante', 'gols_visitante']
    for col in cols_gols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # --- FEATURE ENGINEERING (Novas Métricas) ---
    if all(c in df.columns for c in cols_gols):
        df['total_gols'] = df['gols_mandante'] + df['gols_visitante']
        df['saldo_gols'] = df['gols_mandante'] - df['gols_visitante']
        
        # Definindo resultado
        def calcular_resultado(row):
            if row['gols_mandante'] > row['gols_visitante']: return 'Mandante'
            if row['gols_mandante'] < row['gols_visitante']: return 'Visitante'
            return 'Empate'
        
        df['resultado'] = df.apply(calcular_resultado, axis=1)
        
        # Definindo Vencedor (Nome do Time)
        df['vencedor'] = np.where(df['resultado'] == 'Mandante', df['mandante'], 
                         np.where(df['resultado'] == 'Visitante', df['visitante'], 'Empate'))

        # Pontuação simulada
        df['pts_mandante'] = np.select([df['resultado'] == 'Mandante', df['resultado'] == 'Empate'], [3, 1], 0)
        df['pts_visitante'] = np.select([df['resultado'] == 'Visitante', df['resultado'] == 'Empate'], [3, 1], 0)

    return df

# Inicialização dos dados
df_raw = carregar_e_limpar_dados()

# ── 3. SIDEBAR E NAVEGAÇÃO ────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/pt/4/42/CBF_logo.svg", width=90)
    st.title("⚽ FutStat Brasil")
    st.markdown("---")
    
    menu = st.selectbox(
        "Navegação Principal",
        ["🏠 Dashboard Geral", "📊 Desempenho de Clubes", "⚔️ Confronto Direto (H2H)", 
         "🥅 Análise de Gols", "📅 Linha do Tempo", "🧪 Data Lab"]
    )

    st.subheader("🔍 Filtros de Pesquisa")
    
    # Filtro de Competições
    todas_comp = sorted(df_raw['competicao'].unique())
    filtro_comp = st.multiselect("Competições", todas_comp, default=todas_comp)
    
    # Filtro de Anos (Com trava de segurança para o erro que você teve)
    if '_ano' in df_raw.columns:
        anos_disponiveis = sorted(df_raw['_ano'].unique().astype(int))
        filtro_anos = st.select_slider(
            "Período Analisado", 
            options=anos_disponiveis, 
            value=(min(anos_disponiveis), max(anos_disponiveis))
        )
    else:
        filtro_anos = (0, 9999)

    st.markdown("---")
    st.info(f"Dataset processado: {len(df_raw)} linhas.")

# Aplicação dos Filtros no DF de trabalho
df = df_raw[
    (df_raw['competicao'].isin(filtro_comp)) & 
    (df_raw['_ano'].between(filtro_anos[0], filtro_anos[1]))
].copy()

# ── 4. FUNÇÕES DE PLOTAGEM CUSTOMIZADAS ───────────────────────────────────────
def format_spines(ax):
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 1: DASHBOARD GERAL
# ═════════════════════════════════════════════════════════════════════════════
if menu == "🏠 Dashboard Geral":
    st.header("📋 Panorama Geral do Futebol")
    
    # KPIs Flash
    k1, k2, k3, k4 = st.columns(4)
    k1.metric("Partidas", f"{len(df):,}")
    k2.metric("Média de Gols", f"{df['total_gols'].mean():.2f}")
    
    v_casa = (df['resultado'] == 'Mandante').sum() / len(df) * 100
    k3.metric("Fator Casa", f"{v_casa:.1f}%", help="Percentual de vitórias do mandante")
    k4.metric("Clubes Únicos", df['mandante'].nunique())

    st.markdown("---")
    
    c_left, c_right = st.columns([2, 1])
    
    with c_left:
        st.subheader("🏆 Ranking de Pontuação Acumulada")
        p_mandante = df.groupby('mandante')['pts_mandante'].sum()
        p_visitante = df.groupby('visitante')['pts_visitante'].sum()
        ranking = p_mandante.add(p_visitante, fill_value=0).sort_values(ascending=False).head(15)
        
        fig, ax = plt.subplots(figsize=(10, 6))
        sns.barplot(x=ranking.values, y=ranking.index, palette="summer", ax=ax)
        ax.set_title("Top 15 Clubes por Pontos (Filtros Atuais)")
        format_spines(ax)
        st.pyplot(fig)

    with c_right:
        st.subheader("⚖️ Resultados")
        fig, ax = plt.subplots()
        df['resultado'].value_counts().plot.pie(
            autopct='%1.1f%%', colors=[AZUL_BRASIL, VERDE_BRASIL, 'silver'], 
            explode=(0.05, 0, 0), ax=ax
        )
        ax.set_ylabel("")
        st.pyplot(fig)

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 2: DESEMPENHO DE CLUBES
# ═════════════════════════════════════════════════════════════════════════════
elif menu == "📊 Desempenho de Clubes":
    st.header("📊 Análise de Performance")
    
    escolha_comp = st.selectbox("Selecione a Competição", filtro_comp)
    df_c = df[df['competicao'] == escolha_comp]

    col_a, col_b = st.columns(2)
    
    with col_a:
        st.subheader("🎯 Melhores Ataques")
        gm_m = df_c.groupby('mandante')['gols_mandante'].sum()
        gm_v = df_c.groupby('visitante')['gols_visitante'].sum()
        ataque = gm_m.add(gm_v, fill_value=0).sort_values(ascending=False).head(10)
        
        fig, ax = plt.subplots()
        sns.barplot(x=ataque.values, y=ataque.index, color=VERDE_BRASIL)
        st.pyplot(fig)

    with col_b:
        st.subheader("🛡️ Melhores Defesas")
        gs_m = df_c.groupby('mandante')['gols_visitante'].sum()
        gs_v = df_c.groupby('visitante')['gols_mandante'].sum()
        defesa = gs_m.add(gs_v, fill_value=0).sort_values().head(10)
        
        fig, ax = plt.subplots()
        sns.barplot(x=defesa.values, y=defesa.index, color="darkred")
        st.pyplot(fig)

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 3: CONFRONTO DIRETO (H2H)
# ═════════════════════════════════════════════════════════════════════════════
elif menu == "⚔️ Confronto Direto (H2H)":
    st.header("⚔️ Histórico de Confrontos")
    
    t1, t2 = st.columns(2)
    time_a = t1.selectbox("Time A", sorted(df['mandante'].unique()), index=0)
    time_b = t2.selectbox("Time B", sorted(df['visitante'].unique()), index=1)

    h2h = df[
        ((df['mandante'] == time_a) & (df['visitante'] == time_b)) |
        ((df['mandante'] == time_b) & (df['visitante'] == time_a))
    ].sort_values(by='data', ascending=False)

    if h2h.empty:
        st.warning(f"Nenhum registro encontrado entre {time_a} e {time_b}.")
    else:
        st.write(f"Encontrados **{len(h2h)}** jogos históricos.")
        
        # Mini-KPIs do Confronto
        v_a = (h2h['vencedor'] == time_a).sum()
        v_b = (h2h['vencedor'] == time_b).sum()
        emp = (h2h['vencedor'] == 'Empate').sum()
        
        hc1, hc2, hc3 = st.columns(3)
        hc1.metric(f"Vitórias {time_a}", v_a)
        hc2.metric(f"Vitórias {time_b}", v_b)
        hc3.metric("Empates", emp)
        
        st.dataframe(h2h[['data', 'competicao', 'mandante', 'gols_mandante', 'gols_visitante', 'visitante', 'vencedor']], use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 4: ANÁLISE DE GOLS
# ═════════════════════════════════════════════════════════════════════════════
elif menu == "🥅 Análise de Gols":
    st.header("🥅 Raio-X dos Placares")
    
    col_x, col_y = st.columns(2)
    
    with col_x:
        st.subheader("Frequência de Gols Totais")
        fig, ax = plt.subplots()
        sns.countplot(data=df, x='total_gols', palette="viridis", ax=ax)
        st.pyplot(fig)

    with col_y:
        st.subheader("Mapa Calor de Placares")
        placar_freq = df.pivot_table(index='gols_mandante', columns='gols_visitante', aggfunc='size', fill_value=0)
        fig, ax = plt.subplots()
        sns.heatmap(placar_freq, annot=True, fmt='d', cmap=PALETA_QUENTE, ax=ax)
        ax.invert_yaxis()
        st.pyplot(fig)

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 5: LINHA DO TEMPO
# ═════════════════════════════════════════════════════════════════════════════
elif menu == "📅 Linha do Tempo":
    st.header("📅 Evolução Temporal")
    
    if '_ano' in df.columns:
        st.subheader("Média de Gols por Ano")
        evolucao = df.groupby('_ano')['total_gols'].mean()
        
        fig, ax = plt.subplots(figsize=(12, 5))
        evolucao.plot(kind="line", marker="o", color=AZUL_BRASIL, linewidth=2, ax=ax)
        ax.fill_between(evolucao.index, evolucao.values, alpha=0.1)
        st.pyplot(fig)
        
        st.subheader("Volume de Jogos por Mês (Sazonalidade)")
        # Mapeamento para nomes de meses
        jogos_mes = df.groupby('_mes').size()
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.barplot(x=jogos_mes.index, y=jogos_mes.values, color=AMARELO_BRASIL, ax=ax)
        ax.set_xticklabels(['Jan','Fev','Mar','Abr','Mai','Jun','Jul','Ago','Set','Out','Nov','Dez'])
        st.pyplot(fig)

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 6: DATA LAB (CIÊNCIA DE DADOS)
# ═════════════════════════════════════════════════════════════════════════════
elif menu == "🧪 Data Lab":
    st.header("🧪 Laboratório de Dados")
    
    st.markdown("Explore correlações e baixe os dados processados para seus próprios estudos.")
    
    tab1, tab2 = st.tabs(["🔍 Correlação", "💾 Exportação"])
    
    with tab1:
        cols_corr = ['gols_mandante', 'gols_visitante', 'total_gols', 'saldo_gols', '_ano', 'pts_mandante']
        df_corr = df[cols_corr].corr()
        fig, ax = plt.subplots()
        sns.heatmap(df_corr, annot=True, cmap="coolwarm", center=0, ax=ax)
        st.pyplot(fig)

    with tab2:
        st.subheader("Baixar Dados Filtrados")
        csv = df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="📥 Clique para baixar CSV",
            data=csv,
            file_name=f'soccer_data_{datetime.now().strftime("%Y%m%d")}.csv',
            mime='text/csv',
        )
        
        st.subheader("Amostra das Goleadas Históricas")
        goleadas = df[df['total_gols'] >= 7].sort_values(by='total_gols', ascending=False)
        st.dataframe(goleadas)

# ── RODAPÉ ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    "<div style='text-align: center; color: #888;'>Brasil FutStat Pro · 2026 · Criado para Análise de Big Data Esportivo</div>", 
    unsafe_allow_html=True
)
