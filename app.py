import os
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from datetime import datetime

# ── CONFIGURAÇÕES KAGGLE ──────────────────────────────────────────────────────
if "KAGGLE_USERNAME" in st.secrets:
    os.environ["KAGGLE_USERNAME"] = st.secrets["KAGGLE_USERNAME"]
    os.environ["KAGGLE_KEY"]      = st.secrets["KAGGLE_KEY"]

# ── CONFIGURAÇÃO DA PÁGINA ────────────────────────────────────────────────────
st.set_page_config(
    page_title="Brasil FutStat Pro · Advanced EDA",
    page_icon="⚽",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ── ESTILIZAÇÃO E CONSTANTES ──────────────────────────────────────────────────
sns.set_theme(style="whitegrid")
VERDE_BRASIL = "#009739"
AMARELO_BRASIL = "#FEDD00"
AZUL_BRASIL = "#002776"
PALETA_QUENTE = "YlOrRd"

# ── LÓGICA DE TRATAMENTO DE DADOS ─────────────────────────────────────────────
@st.cache_data(show_spinner="⏳ Minerando dados do Kaggle...")
def carregar_e_limpar_dados():
    import kagglehub
    import glob

    path = kagglehub.dataset_download("ricardomattos05/jogos-do-campeonato-brasileiro")
    caminhos_csv = glob.glob(os.path.join(path, "**", "*.csv"), recursive=True)
    
    dfs = []
    for arq in caminhos_csv:
        try:
            df_temp = pd.read_csv(arq)
            # Limpeza do nome da competição
            nome = os.path.basename(arq).lower().replace(".csv", "")
            nome = nome.replace("_matches", "").replace("_", " ")
            df_temp["competicao"] = nome.strip().title()
            dfs.append(df_temp)
        except Exception as e:
            st.warning(f"Erro ao ler {arq}: {e}")

    if not dfs:
        return pd.DataFrame()

    df = pd.concat(dfs, ignore_index=True)

    # Padronização de Colunas (Trata variações de nomes no CSV)
    mapa_colunas = {
        'Data': 'data', 'Date': 'data',
        'Mandante': 'mandante', 'Home': 'mandante',
        'Visitante': 'visitante', 'Away': 'visitante',
        'Gols Mandante': 'gols_mandante', 'HomeGoals': 'gols_mandante',
        'Gols Visitante': 'gols_visitante', 'AwayGoals': 'gols_visitante'
    }
    df = df.rename(columns=mapa_colunas)

    # Conversão de tipos
    if 'data' in df.columns:
        df['data'] = pd.to_datetime(df['data'], errors='coerce')
        df = df.dropna(subset=['data'])
        df['_ano'] = df['data'].dt.year
        df['_mes'] = df['data'].dt.month
        df['_dia_semana'] = df['data'].dt.day_name()

    cols_gols = ['gols_mandante', 'gols_visitante']
    for col in cols_gols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # --- FEATURE ENGINEERING (Criação de métricas) ---
    if all(c in df.columns for c in cols_gols):
        df['total_gols'] = df['gols_mandante'] + df['gols_visitante']
        df['saldo_gols'] = df['gols_mandante'] - df['gols_visitante']
        
        # Resultado do jogo
        condicoes = [
            (df['gols_mandante'] > df['gols_visitante']),
            (df['gols_mandante'] < df['gols_visitante']),
            (df['gols_mandante'] == df['gols_visitante'])
        ]
        escolhas = ['Mandante', 'Visitante', 'Empate']
        df['resultado'] = np.select(condicoes, escolhas, default='Indefinido')
        
        # Pontuação (Simulada para análise)
        df['pts_mandante'] = np.select([df['resultado'] == 'Mandante', df['resultado'] == 'Empate'], [3, 1], 0)
        df['pts_visitante'] = np.select([df['resultado'] == 'Visitante', df['resultado'] == 'Empate'], [3, 1], 0)

    return df

df_raw = carregar_e_limpar_dados()

# ── SIDEBAR E FILTROS ─────────────────────────────────────────────────────────
with st.sidebar:
    st.image("https://upload.wikimedia.org/wikipedia/pt/4/42/CBF_logo.svg", width=100)
    st.title("⚽ Brasil FutStat Pro")
    st.markdown("---")
    
    menu = st.selectbox(
        "Navegação Principal",
        ["🏠 Dashboard Inicial", "📈 Análise de Desempenho", "⚔️ Head-to-Head", 
         "🥅 Raio-X dos Gols", "📅 Tendências Temporais", "🧪 Laboratório de Dados"]
    )

    st.subheader("🛠️ Filtros Globais")
    todas_comp = sorted(df_raw['competicao'].unique())
    filtro_comp = st.multiselect("Competições", todas_comp, default=todas_comp[:3])
    
    anos = sorted(df_raw['_ano'].unique().astype(int))
    filtro_anos = st.select_slider("Recorte Temporal", options=anos, value=(min(anos), max(anos)))

    st.markdown("---")
    st.caption(f"Última atualização: {datetime.now().strftime('%d/%m/%Y')}")

# Aplicação dos filtros no DataFrame principal
df = df_raw[
    (df_raw['competicao'].isin(filtro_comp)) & 
    (df_raw['_ano'].between(filtro_anos[0], filtro_anos[1]))
].copy()

# ── FUNÇÕES DE APOIO PARA GRÁFICOS ────────────────────────────────────────────
def plot_style(title, xlabel, ylabel):
    plt.title(title, fontsize=16, fontweight='bold', pad=20)
    plt.xlabel(xlabel, fontsize=12)
    plt.ylabel(ylabel, fontsize=12)
    plt.tight_layout()

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 1: DASHBOARD INICIAL
# ═════════════════════════════════════════════════════════════════════════════
if menu == "🏠 Dashboard Inicial":
    st.header("📋 Visão Geral do Ecossistema")
    
    # KPIs Superiores
    kpi1, kpi2, kpi3, kpi4 = st.columns(4)
    with kpi1:
        st.metric("Total de Partidas", f"{len(df):,}")
    with kpi2:
        media_g = df['total_gols'].mean()
        st.metric("Média de Gols/Jogo", f"{media_g:.2f}")
    with kpi3:
        v_casa = (df['resultado'] == 'Mandante').sum() / len(df) * 100
        st.metric("% Vitórias Casa", f"{v_casa:.1f}%")
    with kpi4:
        st.metric("Times Analisados", df['mandante'].nunique())

    st.markdown("---")
    
    col_left, col_right = st.columns([2, 1])
    
    with col_left:
        st.subheader("🔥 Top 10 Times com Mais Pontos Acumulados (Recorte)")
        # Cálculo de pontos totais
        m_pts = df.groupby('mandante')['pts_mandante'].sum()
        v_pts = df.groupby('visitante')['pts_visitante'].sum()
        total_pts = m_pts.add(v_pts, fill_value=0).sort_values(ascending=False).head(10)
        
        fig, ax = plt.subplots(figsize=(10, 5))
        sns.barplot(x=total_pts.values, y=total_pts.index, palette="viridis", ax=ax)
        plot_style("Ranking de Pontuação Acumulada", "Pontos", "Clubes")
        st.pyplot(fig)

    with col_right:
        st.subheader("⚖️ Distribuição de Resultados")
        fig, ax = plt.subplots()
        df['resultado'].value_counts().plot.pie(
            autopct='%1.1f%%', colors=[AZUL_BRASIL, VERDE_BRASIL, 'gray'], 
            startangle=90, ax=ax, explode=(0.05, 0, 0)
        )
        ax.set_ylabel("")
        st.pyplot(fig)

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 2: ANÁLISE DE DESEMPENHO
# ═════════════════════════════════════════════════════════════════════════════
elif menu == "📈 Análise de Desempenho":
    st.header("📈 Rankings e Performance por Competição")
    
    comp_alvo = st.selectbox("Selecione a Competição para Detalhar", filtro_comp)
    df_comp = df[df['competicao'] == comp_alvo]

    tab1, tab2 = st.tabs(["🛡️ Melhores Defesas", "⚔️ Melhores Ataques"])
    
    with tab1:
        # Gols sofridos em casa + fora
        gs_casa = df_comp.groupby('mandante')['gols_visitante'].sum()
        gs_fora = df_comp.groupby('visitante')['gols_mandante'].sum()
        defesa = gs_casa.add(gs_fora, fill_value=0).sort_values().head(10)
        
        st.subheader(f"Muralhas: Menos gols sofridos em {comp_alvo}")
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.barplot(x=defesa.index, y=defesa.values, color="darkred")
        plt.xticks(rotation=45)
        st.pyplot(fig)

    with tab2:
        # Gols marcados em casa + fora
        gm_casa = df_comp.groupby('mandante')['gols_mandante'].sum()
        gm_fora = df_comp.groupby('visitante')['gols_visitante'].sum()
        ataque = gm_casa.add(gm_fora, fill_value=0).sort_values(ascending=False).head(10)
        
        st.subheader(f"Artilharia Coletiva: Mais gols marcados em {comp_alvo}")
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.barplot(x=ataque.index, y=ataque.values, color="darkgreen")
        plt.xticks(rotation=45)
        st.pyplot(fig)

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 3: HEAD-TO-HEAD (CONFRONTO DIRETO)
# ═════════════════════════════════════════════════════════════════════════════
elif menu == "⚔️ Head-to-Head":
    st.header("⚔️ Confronto Direto (Head-to-Head)")
    
    c1, c2 = st.columns(2)
    time_a = c1.selectbox("Time A", sorted(df['mandante'].unique()), index=0)
    time_b = c2.selectbox("Time B", sorted(df['visitante'].unique()), index=1)

    confrontos = df[
        ((df['mandante'] == time_a) & (df['visitante'] == time_b)) |
        ((df['mandante'] == time_b) & (df['visitante'] == time_a))
    ]

    if confrontos.empty:
        st.warning("Não foram encontrados jogos entre essas duas equipes no período selecionado.")
    else:
        st.subheader(f"Histórico: {time_a} vs {time_b}")
        
        # Estatísticas do Confronto
        v_a = len(confrontos[confrontos['vencedor' if 'vencedor' in confrontos else 'resultado'] == (time_a if 'vencedor' in confrontos else 'Mandante')]) # Lógica simplificada
        # Re-calculando vencedor real para o H2H
        def get_winner(row):
            if row['gols_mandante'] > row['gols_visitante']: return row['mandante']
            if row['gols_visitante'] > row['gols_mandante']: return row['visitante']
            return "Empate"
        
        confrontos['vencedor_real'] = confrontos.apply(get_winner, axis=1)
        res_h2h = confrontos['vencedor_real'].value_counts()
        
        h_col1, h_col2, h_col3 = st.columns(3)
        h_col1.metric(f"Vitórias {time_a}", res_h2h.get(time_a, 0))
        h_col2.metric(f"Vitórias {time_b}", res_h2h.get(time_b, 0))
        h_col3.metric("Empates", res_h2h.get("Empate", 0))

        st.dataframe(confrontos[['data', 'competicao', 'mandante', 'gols_mandante', 'gols_visitante', 'visitante']], use_container_width=True)

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 4: RAIO-X DOS GOLS
# ═════════════════════════════════════════════════════════════════════════════
elif menu == "🥅 Raio-X dos Gols":
    st.header("🥅 Análise Estatística de Placares")
    
    col_l, col_r = st.columns(2)
    
    with col_l:
        st.subheader("Distribuição de Gols Totais")
        fig, ax = plt.subplots()
        sns.histplot(df['total_gols'], kde=True, bins=15, color="purple", ax=ax)
        st.pyplot(fig)
        st.info("💡 A maioria dos jogos brasileiros termina com 2 ou 3 gols.")

    with col_r:
        st.subheader("Heatmap de Placares (Frequência)")
        matrix_placar = df.pivot_table(index='gols_mandante', columns='gols_visitante', aggfunc='size', fill_value=0)
        fig, ax = plt.subplots()
        sns.heatmap(matrix_placar, annot=True, fmt='d', cmap=PALETA_QUENTE, ax=ax)
        ax.invert_yaxis()
        st.pyplot(fig)

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 5: TENDÊNCIAS TEMPORAIS
# ═════════════════════════════════════════════════════════════════════════════
elif menu == "📅 Tendências Temporais":
    st.header("📅 Evolução do Futebol ao Longo dos Anos")
    
    tab_ano, tab_mes = st.tabs(["🗓️ Por Ano", "🕒 Por Mês"])
    
    with tab_ano:
        evo_gols = df.groupby('_ano')['total_gols'].mean()
        fig, ax = plt.subplots(figsize=(12, 5))
        evo_gols.plot(kind="line", marker="s", color=AZUL_BRASIL, linewidth=3, ax=ax)
        plot_style("Média de Gols por Ano", "Ano", "Gols/Jogo")
        st.pyplot(fig)

    with tab_mes:
        st.subheader("Volume de Jogos por Mês (Sazonalidade)")
        ordem_meses = [1,2,3,4,5,6,7,8,9,10,11,12]
        jogos_mes = df.groupby('_mes').size().reindex(ordem_meses)
        fig, ax = plt.subplots(figsize=(10, 4))
        sns.barplot(x=jogos_mes.index, y=jogos_mes.values, palette="coolwarm", ax=ax)
        st.pyplot(fig)

# ═════════════════════════════════════════════════════════════════════════════
# SEÇÃO 6: LABORATÓRIO DE DADOS (AVANÇADO)
# ═════════════════════════════════════════════════════════════════════════════
elif menu == "🧪 Laboratório de Dados":
    st.header("🧪 Laboratório de Análise Avançada")
    
    st.markdown("""
    Nesta seção, exploramos correlações e detecção de anomalias (Outliers).
    """)
    
    exp1 = st.expander("🔍 Correlação de Variáveis")
    with exp1:
        corr = df[['gols_mandante', 'gols_visitante', 'total_gols', 'saldo_gols', '_ano', 'pts_mandante']].corr()
        fig, ax = plt.subplots()
        sns.heatmap(corr, annot=True, cmap="RdBu", center=0, ax=ax)
        st.pyplot(fig)

    exp2 = st.expander("🚨 Jogos Atípicos (Goleadas Históricas)")
    with exp2:
        goleadas = df[df['total_gols'] >= 7].sort_values(by='total_gols', ascending=False)
        st.write("Partidas com 7 ou mais gols encontrados:")
        st.table(goleadas[['data', 'mandante', 'gols_mandante', 'gols_visitante', 'visitante', 'competicao']])

    st.markdown("---")
    st.subheader("💾 Exportar Dados Filtrados")
    @st.cache_data
    def convert_df(df_to_save):
        return df_to_save.to_csv(index=False).encode('utf-8')

    csv_data = convert_df(df)
    st.download_button(
        label="Download CSV dos Filtros Atuais",
        data=csv_data,
        file_name='futebol_brasileiro_filtrado.csv',
        mime='text/csv',
    )

# ── RODAPÉ ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown(
    f"<div style='text-align: center'>Desenvolvido para análise de Dados Esportivos · 2026 · {len(df_raw)} linhas processadas</div>", 
    unsafe_allow_html=True
)
