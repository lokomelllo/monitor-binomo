import streamlit as st
import yfinance as yf
import ta
import google.generativeai as genai

st.set_page_config(page_title="Monitor de Trades", layout="wide")
st.title("📈 Monitor de Pares & Indicadores - Binomo")

# Seleção do Par
par = st.selectbox("Selecione o Par para Monitorar:", ["EURUSD=X", "GBPUSD=X", "BTC-USD", "ETH-USD"])

# Busca dados de mercado
dados = yf.download(par, period="1d", interval="5m")

if not dados.empty:
    # Cálculo do RSI
    close_series = dados['Close'].iloc[:, 0] if len(dados['Close'].shape) > 1 else dados['Close']
    dados['RSI'] = ta.momentum.RSIIndicator(close=close_series, window=14).rsi()
    
    rsi_atual = float(dados['RSI'].iloc[-1])
    preco_atual = float(close_series.iloc[-1])

    col1, col2 = st.columns(2)
    col1.metric("Preço Atual", f"{preco_atual:.4f}")
    col2.metric("RSI (14)", f"{rsi_atual:.2f}")

    # Gráfico de Preço
    st.line_chart(close_series)

    st.markdown("---")
    st.subheader("🤖 Análise com Inteligência Artificial")
    
    # Campo para inserir a chave da API do Gemini de forma segura
    api_key = st.text_input("Insira sua Gemini API Key (Aistudio):", type="password")

    if st.button("Analisa Mercado com IA"):
        if not api_key:
            st.error("Por favor, insira sua chave da API do Gemini.")
        else:
            try:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel('gemini-2.5-flash')

                
                ultimos_fechamentos = close_series.tail(5).values.tolist()
                
                prompt = f"""
                Atue como um analista técnico de trading em Opções Binárias / Forex.
                Analise os seguintes dados do par {par} em tempo real:
                - Preço Atual: {preco_atual}
                - RSI Atual: {rsi_atual}
                - Últimos 5 fechamentos: {ultimos_fechamentos}

                Responda em no máximo 2 frases objetivas: 
                1. O mercado está em tendência clara ou consolidação? 
                2. Qual o contexto atual do RSI (sobrecomprado, sobrevendido ou neutro)?
                """
                
                with st.spinner("IA analisando o mercado..."):
                    resposta = model.generate_content(prompt)
                    st.success(resposta.text)
            except Exception as e:
                st.error(f"Erro ao consultar a IA: {e}")
