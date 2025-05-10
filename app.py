import streamlit as st
import yfinance as yf
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import numpy as np

# Configuração da página
st.set_page_config(
    page_title="Stock Analysis Dashboard",
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
    .sidebar .sidebar-content {
        background-color: #343a40;
        color: white;
    }
    .st-bq {
        border-radius: 10px;
    }
    .stock-card {
        border-radius: 10px;
        padding: 15px;
        background-color: grayish;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        margin-bottom: 20px;
    }
    .metric-card {
        border-radius: 10px;
        padding: 15px;
        background-color: #ffffff;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)

# Título do dashboard
st.title("📊 Painel de Analise para Ações $")

# Sidebar com filtros
with st.sidebar:
    st.image(r"C:\Users\JOSEANA E FERNANDO\Desktop\projeto_python\investment.png", width=150)
    st.header("🔍 Filtros")
    
    # Seleção de tickers (exemplos de ações brasileiras e americanas)
    default_tickers = ["PETR4.SA", "VALE3.SA", "ITUB4.SA", "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NFLX", "FB", "BBAS3.SA", "ABEV3.SA", "MGLU3.SA", "WEGE3.SA", "LREN3.SA", "B3SA3.SA", "BRFS3.SA", "RENT3.SA", "CVCB3.SA", "GGBR4.SA", "JBSS3.SA", "MRFG3.SA", "SBSP3.SA", "SUZB3.SA", "TOTS3.SA", "VIVT3.SA", "YDUQ3.SA", "RANI3.SA", "IRBR3.SA", "PSSA3.SA", "CMIG4.SA", "CPFE3.SA", "ENGI11.SA", "EQTL3.SA", "LIGT3.SA", "NTCO3.SA", "PARD3.SA", "QUAL3.SA", "RADL3.SA", "RENT3.SA", "SULA11.SA", "TIMS3.SA", "TRPL4.SA"]
    selected_tickers = st.multiselect(
        "Selecione as ações:",
        options=default_tickers,
        default=default_tickers[:3]
    )
    
    # Período de análise
    end_date = datetime.today()
    start_date = end_date - timedelta(days=365)
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Data inicial:",
            value=start_date,
            max_value=end_date - timedelta(days=1)
        )   
    with col2:
        end_date = st.date_input(
            "Data final:",
            value=end_date,
            min_value=start_date + timedelta(days=1),
            max_value=datetime.today())
    
    # Intervalo de tempo
    interval = st.selectbox(
        "Intervalo:",
        options=["1d", "1wk", "1mo"],
        index=0
    )
    
    # Métricas adicionais
    show_advanced = st.checkbox("Mostrar métricas avançadas")
    if show_advanced:
        moving_average = st.slider("Média móvel (dias):", 7, 200, 50)
        show_rsi = st.checkbox("Mostrar RSI (14 dias)", value=True)
        show_macd = st.checkbox("Mostrar MACD", value=False)

# Função para carregar dados
@st.cache_data(ttl=3600)  # Cache de 1 hora
def load_data(tickers, start_date, end_date, interval):
    data = yf.download(
        tickers=tickers,
        start=start_date,
        end=end_date,
        interval=interval,
        group_by='ticker'
    )
    return data

# Carregar dados
if selected_tickers:
    with st.spinner("Carregando dados..."):
        stock_data = load_data(selected_tickers, start_date, end_date, interval)
    
    if stock_data.empty:
        st.error("Não foi possível carregar os dados para os tickers selecionados.")
    else:
        # Layout principal
        tab1, tab2, tab3 = st.tabs(["📊 Visão Geral", "📈 Análise Técnica", "📌 Comparativo"])
        
        with tab1:
            st.header("Visão Geral do Mercado")
            
            # Cards com métricas resumidas
            cols = st.columns(len(selected_tickers))
            for i, ticker in enumerate(selected_tickers):
                if ticker in stock_data:
                    last_close = stock_data[ticker]['Close'].iloc[-1]
                    first_close = stock_data[ticker]['Close'].iloc[0]
                    change_pct = ((last_close - first_close) / first_close) * 100
                    
                    with cols[i]:
                        st.markdown(f"""
                            <div class="metric-card">
                                <h3>{ticker}</h3>
                                <h2>{last_close:.2f}</h2>
                                <p style="color: {'green' if change_pct >= 0 else 'red'}">
                                    {change_pct:.2f}% {'↑' if change_pct >= 0 else '↓'}
                                </p>
                            </div>
                        """, unsafe_allow_html=True)
            
            # Gráfico de preços
            st.subheader("Evolução dos Preços")
            fig = go.Figure()
            
            for ticker in selected_tickers:
                if ticker in stock_data:
                    df = stock_data[ticker].reset_index()
                    fig.add_trace(go.Scatter(
                        x=df['Date'],
                        y=df['Close'],
                        name=ticker,
                        line=dict(width=2),
                        mode='lines'
                    ))
            
            fig.update_layout(
                hovermode="x unified",
                xaxis_title="Data",
                yaxis_title="Preço (R$)",
                height=500,
                margin=dict(l=20, r=20, t=30, b=20),
                legend=dict(
                    orientation="h",
                    yanchor="bottom",
                    y=1.02,
                    xanchor="right",
                    x=1
                )
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Dados em tabela
            st.subheader("Dados Históricos")
            selected_ticker = st.selectbox("Selecione uma ação para ver os dados:", default_tickers)
            if selected_ticker in stock_data:
                st.dataframe(stock_data[selected_ticker].sort_index(ascending=False), height=300)
        
        with tab2:
            st.header("Análise Técnica")
            
            selected_ticker_ta = st.selectbox("Selecione uma ação para análise:", default_tickers)
            
            if selected_ticker_ta in stock_data:
                df = stock_data[selected_ticker_ta].copy()
                df = df.reset_index()
                
                # Cálculo de indicadores técnicos
                if show_advanced:
                    # Média Móvel
                    df['MA'] = df['Close'].rolling(window=moving_average).mean()
                    
                    # RSI
                    if show_rsi:
                        delta = df['Close'].diff()
                        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
                        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
                        rs = gain / loss
                        df['RSI'] = 100 - (100 / (1 + rs))
                    
                    # MACD
                    if show_macd:
                        exp12 = df['Close'].ewm(span=12, adjust=False).mean()
                        exp26 = df['Close'].ewm(span=26, adjust=False).mean()
                        df['MACD'] = exp12 - exp26
                        df['Signal'] = df['MACD'].ewm(span=9, adjust=False).mean()
                
                # Gráfico de candlesticks
                st.subheader(f"Gráfico de Candles - {selected_ticker_ta}")
                fig_candles = go.Figure()
                
                fig_candles.add_trace(go.Candlestick(
                    x=df['Date'],
                    open=df['Open'],
                    high=df['High'],
                    low=df['Low'],
                    close=df['Close'],
                    name='Candles'
                ))
                
                if show_advanced:
                    fig_candles.add_trace(go.Scatter(
                        x=df['Date'],
                        y=df['MA'],
                        name=f'Média Móvel ({moving_average} dias)',
                        line=dict(color='orange', width=2)
                    ))
                
                fig_candles.update_layout(
                    height=500,
                    xaxis_rangeslider_visible=False,
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                st.plotly_chart(fig_candles, use_container_width=True)
                
                # Gráficos de indicadores
                if show_advanced:
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if show_rsi:
                            st.subheader("Índice de Força Relativa (RSI)")
                            fig_rsi = go.Figure()
                            fig_rsi.add_trace(go.Scatter(
                                x=df['Date'],
                                y=df['RSI'],
                                name='RSI',
                                line=dict(color='purple', width=2)
                            ))
                            fig_rsi.add_hline(y=70, line_dash="dash", line_color="red")
                            fig_rsi.add_hline(y=30, line_dash="dash", line_color="green")
                            fig_rsi.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                            st.plotly_chart(fig_rsi, use_container_width=True)
                    
                    with col2:
                        if show_macd:
                            st.subheader("MACD")
                            fig_macd = go.Figure()
                            fig_macd.add_trace(go.Scatter(
                                x=df['Date'],
                                y=df['MACD'],
                                name='MACD',
                                line=dict(color='blue', width=2)
                            ))
                            fig_macd.add_trace(go.Scatter(
                                x=df['Date'],
                                y=df['Signal'],
                                name='Signal',
                                line=dict(color='orange', width=2)
                            ))
                            fig_macd.update_layout(height=300, margin=dict(l=20, r=20, t=30, b=20))
                            st.plotly_chart(fig_macd, use_container_width=True)
        
        with tab3:
            st.header("Análise Comparativa")
            
            if len(selected_tickers) > 1:
                # Normalização dos preços para comparação
                norm_data = pd.DataFrame()
                for ticker in selected_tickers:
                    if ticker in stock_data:
                        norm_data[ticker] = stock_data[ticker]['Close'] / stock_data[ticker]['Close'].iloc[0] * 100
                
                # Gráfico comparativo
                st.subheader("Desempenho Relativo (Base 100)")
                fig_compare = px.line(
                    norm_data.reset_index(),
                    x='Date',
                    y=selected_tickers,
                    labels={'value': 'Desempenho (%)', 'variable': 'Ação'},
                    height=500
                )
                fig_compare.update_layout(
                    hovermode="x unified",
                    margin=dict(l=20, r=20, t=30, b=20)
                )
                st.plotly_chart(fig_compare, use_container_width=True)
                
                # Correlação entre ações
                st.subheader("Matriz de Correlação")
                corr_matrix = norm_data.corr()
                fig_corr = px.imshow(
                    corr_matrix,
                    text_auto=True,
                    color_continuous_scale='RdYlGn',
                    zmin=-1,
                    zmax=1,
                    labels=dict(color="Correlação")
                )
                fig_corr.update_layout(height=500)
                st.plotly_chart(fig_corr, use_container_width=True)
            else:
                st.warning("Selecione pelo menos 2 ações para comparação.")
else:
    st.warning("Por favor, selecione pelo menos uma ação para análise.")
# Carregar dados financeiros adicionais
@st.cache_data(ttl=3600)  # Cache de 1 hora
def load_financial_data():
    # Exemplo de dados financeiros fictícios
    data = {
        'Ticker': ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'AAPL', 'MSFT'],
        'Nome': ['Petrobras', 'Vale', 'Itaú Unibanco', 'Apple Inc.', 'Microsoft Corp.'],
        'Setor': ['Energia', 'Mineração', 'Financeiro', 'Tecnologia', 'Tecnologia'],
        'Subsetor': ['Petróleo e Gás', 'Mineração de Ferro', 'Bancos', 'Hardware', 'Software'],
        'Dividend Yield (%)': [5.0, 4.5, 3.0, 0.6, 0.8],
        'Payout (%)': [50, 40, 30, 20, 25],
        'Lucro Líquido (R$ bi)': [10, 15, 8, 50, 60],
        'Crescimento Lucro (%)': [5, 10, 7, 15, 12],
        'Dividendos Crescimento (%)': [3, 5, 2, 1, 2]
    }
    return pd.DataFrame(data)
df_financial = load_financial_data()
# Carregar dados de ações
@st.cache_data(ttl=3600)  # Cache de 1 hora
def load_stocks_data():
    # Exemplo de dados de ações fictícios
    data = {
        'Ticker': ['PETR4.SA', 'VALE3.SA', 'ITUB4.SA', 'AAPL', 'MSFT'],
        'Nome': ['Petrobras', 'Vale', 'Itaú Unibanco', 'Apple Inc.', 'Microsoft Corp.'],
        'Setor': ['Energia', 'Mineração', 'Financeiro', 'Tecnologia', 'Tecnologia'],
        'Subsetor': ['Petróleo e Gás', 'Mineração de Ferro', 'Bancos', 'Hardware', 'Software']
    }
    return pd.DataFrame(data)
df_stocks = load_stocks_data()
# Exibir dados financeiros
st.subheader("Dados Financeiros")
st.dataframe(df_financial, use_container_width=True)
# Exibir dados de ações
st.subheader("Dados de Ações")
st.dataframe(df_stocks, use_container_width=True)
# Exibir informações adicionais
st.subheader("Informações Adicionais", anchor="informacoes")
st.markdown("""
    <div style="text-align: center; color: #6c757d;">
        Este dashboard foi desenvolvido para análise de ações do mercado financeiro. Os dados são atualizados periodicamente e podem ser filtrados por ticker, data e intervalo.
    </div>
""", unsafe_allow_html=True)
# Exibir informações de contato
st.subheader("Contato", anchor="contato")
st.markdown("""
    <div style="text-align: center; color: #6c757d;">
        Para mais informações, entre em contato: <br>
        Email:fernanfds@yahoo.com.br <br>
        LinkedIn: [Fernando](https://www.linkedin.com/in/fernando-silva-465269238/)
    </div>
""", unsafe_allow_html=True)
# Exibir informações de copyright
st.subheader("Copyright")
st.markdown("""
    <div style="text-align: center; color: #6c757d;">
        © 2023 Fernando Silva. Todos os direitos reservados.
    </div>
""", unsafe_allow_html=True)
# Exibir informações de versão

    
# Rodapé
st.markdown("---")
st.markdown("""
    <div style="text-align: center; color: #6c757d; font-size: 0.9em;">
        Stock Analysis Dashboard • Dados do Yahoo Finance • Atualizado em {date}
    </div>
""".format(date=datetime.now().strftime("%d/%m/%Y %H:%M")), unsafe_allow_html=True)