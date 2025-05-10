import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import yfinance as yf
from datetime import datetime, timedelta
import requests
from bs4 import BeautifulSoup
import matplotlib.pyplot as plt
from plotly.subplots import make_subplots
import plotly.graph_objects as go

# Configuração da página
st.set_page_config(
    page_title="Análise de Ações BR | Dividendos & Lucratividade",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Estilos CSS personalizados
st.markdown("""
    <style>
    .main {
        background-color: #f8f9fa;
    }
    .stSelectbox div[data-baseweb="select"] > div {
        border-color: #6c757d;
    }
    .stTextInput div[data-baseweb="input"] > div {
        border-color: #6c757d;
    }
    .css-1aumxhk {
        background-color: #e9ecef;
        background-image: none;
    }
    .stock-header {
        font-size: 2rem;
        font-weight: 700;
        color: #2c3e50;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #6c757d;
        margin-bottom: 1rem;
    }
    .metric-box {
        background-color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }
    .positive {
        color: #28a745;
        font-weight: bold;
    }
    .negative {
        color: #dc3545;
        font-weight: bold;
    }
    .ticker-info {
        background-color: white;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 2rem;
    }
    </style>
""", unsafe_allow_html=True)

# Dados de exemplo (na prática, você usaria uma API ou banco de dados)
@st.cache_data
def load_stock_data():
    # Lista de ações brasileiras com dados fictícios para exemplo
    stocks = {
        'PETR4.SA': {'Nome': 'Petrobras', 'Setor': 'Energia', 'Subsetor': 'Petróleo e Gás'},
        'VALE3.SA': {'Nome': 'Vale', 'Setor': 'Materiais Básicos', 'Subsetor': 'Mineração'},
        'ITUB4.SA': {'Nome': 'Itaú Unibanco', 'Setor': 'Financeiro', 'Subsetor': 'Bancos'},
        'BBDC4.SA': {'Nome': 'Bradesco', 'Setor': 'Financeiro', 'Subsetor': 'Bancos'},
        'BBAS3.SA': {'Nome': 'Banco do Brasil', 'Setor': 'Financeiro', 'Subsetor': 'Bancos'},
        'WEGE3.SA': {'Nome': 'WEG', 'Setor': 'Bens Industriais', 'Subsetor': 'Máquinas e Equipamentos'},
        'RENT3.SA': {'Nome': 'Localiza', 'Setor': 'Consumo Cíclico', 'Subsetor': 'Aluguel de Carros'},
        'TAEE11.SA': {'Nome': 'Taesa', 'Setor': 'Utilidade Pública', 'Subsetor': 'Energia Elétrica'},
        'CPLE6.SA': {'Nome': 'Copel', 'Setor': 'Utilidade Pública', 'Subsetor': 'Energia Elétrica'},
        'ABEV3.SA': {'Nome': 'Ambev', 'Setor': 'Consumo não Cíclico', 'Subsetor': 'Bebidas'},
    }
    return pd.DataFrame.from_dict(stocks, orient='index').reset_index().rename(columns={'index': 'Ticker'})

# Dados de dividendos e lucratividade (fictícios para exemplo)
@st.cache_data
def load_financial_data():
    data = []
    tickers = ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'BBDC4.SA', 'BBAS3.SA', 
               'WEGE3.SA', 'RENT3.SA', 'TAEE11.SA', 'CPLE6.SA', 'ABEV3.SA']
    
    for ticker in tickers:
        for year in range(2019, 2024):
            # Dados fictícios - na prática você buscaria em uma API
            div_yield = np.random.uniform(2, 12)
            payout = np.random.uniform(30, 100)
            lucro = np.random.uniform(1, 20) * 1e9
            crescimento_lucro = np.random.uniform(-5, 15)
            data.append({
                'Ticker': ticker,
                'Ano': year,
                'Dividend Yield (%)': div_yield,
                'Payout (%)': payout,
                'Lucro Líquido (R$ bi)': lucro / 1e9,
                'Crescimento Lucro (%)': crescimento_lucro,
                'Dividendos Crescimento (%)': np.random.uniform(0, 10)
            })
    
    return pd.DataFrame(data)

# Carregar dados
df_stocks = load_stock_data()
df_financial = load_financial_data()

# Sidebar - Filtros e busca
with st.sidebar:
    st.image(r"C:\Users\JOSEANA E FERNANDO\Desktop\projeto_python\investment.png", width=200)
    #st.image("C:\Users\JOSEANA E FERNANDO\Desktop\projeto_python\investment.png", width=200)
    st.title("Filtros de Ações")
    st.markdown("### Encontre as melhores ações para investir")
    st.markdown("Utilize os filtros abaixo para refinar sua busca por ações com bom potencial de dividendos e lucratividade.")
    st.markdown("---")
    
    
    # Busca por ticker ou nome
    search_term = st.text_input("Buscar ativo (ticker ou nome)", "")
    
    # Filtro por setor
    setores = df_stocks['Setor'].unique()
    setor_selecionado = st.selectbox("Filtrar por Setor", ["Todos"] + list(setores))
    
    # Filtro por dividend yield mínimo
    min_div = st.slider("Dividend Yield mínimo (%)", 0.0, 15.0, 5.0, 0.5)
    
    # Filtro por anos consecutivos de dividendos
    min_anos_div = st.slider("Mínimo de anos pagando dividendos", 0, 5, 3)
    
    # Filtro por lucratividade
    lucratividade = st.selectbox("Lucratividade nos últimos 5 anos", 
                                ["Qualquer", "Sempre lucrativa", "Crescimento consistente"])

# Aplicar filtros
if search_term:
    df_stocks_filtered = df_stocks[
        df_stocks['Ticker'].str.contains(search_term.upper()) | 
        df_stocks['Nome'].str.contains(search_term, case=False)
    ]
else:
    df_stocks_filtered = df_stocks.copy()

if setor_selecionado != "Todos":
    df_stocks_filtered = df_stocks_filtered[df_stocks_filtered['Setor'] == setor_selecionado]

# Filtrar por dividend yield
tickers_com_div_yield = df_financial.groupby('Ticker')['Dividend Yield (%)'].mean().reset_index()
tickers_com_div_yield = tickers_com_div_yield[tickers_com_div_yield['Dividend Yield (%)'] >= min_div]['Ticker']
df_stocks_filtered = df_stocks_filtered[df_stocks_filtered['Ticker'].isin(tickers_com_div_yield)]

# Filtrar por anos pagando dividendos
tickers_anos_div = df_financial.groupby('Ticker').size().reset_index(name='Anos')
tickers_anos_div = tickers_anos_div[tickers_anos_div['Anos'] >= min_anos_div]['Ticker']
df_stocks_filtered = df_stocks_filtered[df_stocks_filtered['Ticker'].isin(tickers_anos_div)]

# Filtrar por lucratividade
if lucratividade == "Sempre lucrativa":
    tickers_lucrativos = df_financial.groupby('Ticker')['Lucro Líquido (R$ bi)'].min().reset_index()
    tickers_lucrativos = tickers_lucrativos[tickers_lucrativos['Lucro Líquido (R$ bi)'] > 0]['Ticker']
    df_stocks_filtered = df_stocks_filtered[df_stocks_filtered['Ticker'].isin(tickers_lucrativos)]
elif lucratividade == "Crescimento consistente":
    # Verifica se houve crescimento ano a ano
    def is_growing(ticker_df):
        lucros = ticker_df.sort_values('Ano')['Lucro Líquido (R$ bi)'].values
        return all(x <= y for x, y in zip(lucros, lucros[1:]))
    
    tickers_crescentes = []
    for ticker in df_stocks_filtered['Ticker']:
        ticker_df = df_financial[df_financial['Ticker'] == ticker]
        if is_growing(ticker_df):
            tickers_crescentes.append(ticker)
    df_stocks_filtered = df_stocks_filtered[df_stocks_filtered['Ticker'].isin(tickers_crescentes)]

# Página principal
st.title("📈 Análise de Ações Brasileiras")
st.markdown("""
    *Foco em Dividendos e Empresas Lucrativas nos Últimos 5 Anos*  
    Utilize os Filtros na Sidebar para Encontrar as Melhores Oportunidades.
""")

# Mostrar ações filtradas
if not df_stocks_filtered.empty:
    st.subheader("Ações que Atendem aos Critérios")
    
    # Métricas resumidas
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Número de Ações", len(df_stocks_filtered))
    with col2:
        avg_div = df_financial[df_financial['Ticker'].isin(df_stocks_filtered['Ticker'])]['Dividend Yield (%)'].mean()
        st.metric("Dividend Yield Médio", f"{avg_div:.2f}%")
    with col3:
        avg_payout = df_financial[df_financial['Ticker'].isin(df_stocks_filtered['Ticker'])]['Payout (%)'].mean()
        st.metric("Payout Médio", f"{avg_payout:.2f}%")
    
    # Tabela de ações
    st.dataframe(
        df_stocks_filtered.style.format({
            'Dividend Yield (%)': '{:.2f}%',
            'Payout (%)': '{:.2f}%'
        }),
        use_container_width=True,
        hide_index=True
    )
    
    # Selecionar uma ação para análise detalhada
    selected_ticker = st.selectbox(
        "Selecione uma ação para análise detalhada",
        df_stocks_filtered['Ticker'].tolist(),
        format_func=lambda x: f"{x} - {df_stocks_filtered[df_stocks_filtered['Ticker'] == x]['Nome'].values[0]}"
        
    )
    
    if selected_ticker:
        # Obter dados da ação selecionada
        stock_info = df_stocks[df_stocks['Ticker'] == selected_ticker].iloc[0]
        
        st.markdown(f"### Informações sobre {stock_info['Nome']}")
        st.markdown(f"**Setor:** {stock_info['Setor']}")
        st.markdown(f"**Subsetor:** {stock_info['Subsetor']}")
        st.markdown(f"**Ticker:** {stock_info['Ticker']}")
        st.markdown(f"**Dividend Yield:** {df_financial[df_financial['Ticker'] == selected_ticker]['Dividend Yield (%)'].mean():.2f}%")
        st.markdown(f"**Payout:** {df_financial[df_financial['Ticker'] == selected_ticker]['Payout (%)'].mean():.2f}%")
        st.markdown(f"**Lucro Líquido Médio (últimos 5 anos):** R$ {df_financial[df_financial['Ticker'] == selected_ticker]['Lucro Líquido (R$ bi)'].mean():.2f} bilhões")
        st.markdown(f"**Crescimento do Lucro (últimos 5 anos):** {df_financial[df_financial['Ticker'] == selected_ticker]['Crescimento Lucro (%)'].mean():.2f}%")
        st.markdown(f"**Crescimento dos Dividendos (últimos 5 anos):** {df_financial[df_financial['Ticker'] == selected_ticker]['Dividendos Crescimento (%)'].mean():.2f}%")
        st.markdown("---")
        # Gráfico de lucros e dividendos
        fig = make_subplots(rows=2, cols=1, subplot_titles=("Lucro Líquido (R$ bi)", "Dividendos (R$ bi)"))
        lucro_data = df_financial[df_financial['Ticker'] == selected_ticker]
        lucro_data = lucro_data.sort_values('Ano')
        fig.add_trace(
            go.Bar(x=lucro_data['Ano'], y=lucro_data['Lucro Líquido (R$ bi)'], name='Lucro Líquido', marker_color='blue'),
            row=1, col=1
        )
        fig.add_trace(
            go.Bar(x=lucro_data['Ano'], y=lucro_data['Dividendos Crescimento (%)'], name='Dividendos', marker_color='green'),
            row=2, col=1
        )
        fig.update_layout(title_text=f"Lucro e Dividendos de {stock_info['Nome']}", height=600)
        st.plotly_chart(fig, use_container_width=True)
        # Gráfico de dividend yield
        fig2 = px.line(
            df_financial[df_financial['Ticker'] == selected_ticker],
            x='Ano',
            y='Dividend Yield (%)',
            title=f"Dividend Yield de {stock_info['Nome']}",
            labels={'Dividend Yield (%)': 'Dividend Yield (%)', 'Ano': 'Ano'},
            markers=True
        )
        fig2.update_traces(marker=dict(size=10))
        fig2.update_layout(yaxis_tickformat='%')
        st.plotly_chart(fig2, use_container_width=True)
        # Gráfico de payout
        fig3 = px.line(
            df_financial[df_financial['Ticker'] == selected_ticker],
            x='Ano',
            y='Payout (%)',
            title=f"Payout de {stock_info['Nome']}",
            labels={'Payout (%)': 'Payout (%)', 'Ano': 'Ano'},
            markers=True
        )
        fig3.update_traces(marker=dict(size=10))
        fig3.update_layout(yaxis_tickformat='%')
        st.plotly_chart(fig3, use_container_width=True)
        # Gráfico de crescimento do lucro
        fig4 = px.line(
            df_financial[df_financial['Ticker'] == selected_ticker],
            x='Ano',
            y='Crescimento Lucro (%)',
            title=f"Crescimento do Lucro de {stock_info['Nome']}",
            labels={'Crescimento Lucro (%)': 'Crescimento do Lucro (%)', 'Ano': 'Ano'},
            markers=True
        )
        fig4.update_traces(marker=dict(size=10))
        fig4.update_layout(yaxis_tickformat='%')
        st.plotly_chart(fig4, use_container_width=True)
        # Gráfico de crescimento dos dividendos
        fig5 = px.line(
            df_financial[df_financial['Ticker'] == selected_ticker],
            x='Ano',
            y='Dividendos Crescimento (%)',
            title=f"Crescimento dos Dividendos de {stock_info['Nome']}",
            labels={'Dividendos Crescimento (%)': 'Crescimento dos Dividendos (%)', 'Ano': 'Ano'},
            markers=True
        )
        fig5.update_traces(marker=dict(size=10))
        fig5.update_layout(yaxis_tickformat='%')
        st.plotly_chart(fig5, use_container_width=True) 
       
# Rodapé
st.markdown("---")
st.markdown("### Sobre o Aplicativo")
st.markdown("""
    Este aplicativo foi desenvolvido para ajudar investidores a encontrar ações brasileiras com bom potencial de dividendos e lucratividade.
    A análise é baseada em dados históricos e métricas financeiras.
    As informações apresentadas são meramente informativas e não devem ser consideradas como recomendações de investimento.
    Sempre faça sua própria pesquisa antes de tomar decisões financeiras.
""")
st.markdown("### Contato")
st.markdown("""
    Para sugestões, dúvidas ou feedback, entre em contato pelo e-mail:
    [fernanfds@yahoo.com.br](mailto:fernanfds@yahoo.com.br)
    """)




        