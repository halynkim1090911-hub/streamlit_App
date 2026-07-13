import streamlit as st
import pandas as pd
import plotly.express as px
import yfinance as yf

st.set_page_config(
    page_title="Global Top10 Stocks Dashboard",
    layout="wide"
)

st.title("🌍 Global Market Cap Top10 Stock Dashboard")
st.markdown("최근 1년간 글로벌 시가총액 Top10 기업의 주가 비교")

# Top10 (2025 기준)
companies = {
    "Apple":"AAPL",
    "Microsoft":"MSFT",
    "NVIDIA":"NVDA",
    "Amazon":"AMZN",
    "Alphabet":"GOOGL",
    "Meta":"META",
    "Saudi Aramco":"2222.SR",
    "Broadcom":"AVGO",
    "Tesla":"TSLA",
    "Berkshire Hathaway":"BRK-B"
}

selected = st.multiselect(
    "기업 선택",
    list(companies.keys()),
    default=list(companies.keys())
)

normalize = st.checkbox("100 기준으로 정규화", value=True)

@st.cache_data
def load_data(selected):

    data = pd.DataFrame()

    for company in selected:
        ticker = companies[company]

        try:
            df = yf.download(
                ticker,
                period="1y",
                progress=False,
                auto_adjust=True
            )

            df = df[["Close"]]
            df.columns=[company]

            if data.empty:
                data=df
            else:
                data=data.join(df, how="outer")

        except:
            pass

    return data

price = load_data(selected)

if price.empty:
    st.warning("데이터를 불러오지 못했습니다.")
    st.stop()

price = price.dropna(how="all")

if normalize:
    price = price / price.iloc[0] * 100

plot_df = (
    price.reset_index()
    .melt(id_vars="Date",
          var_name="Company",
          value_name="Price")
)

fig = px.line(
    plot_df,
    x="Date",
    y="Price",
    color="Company",
    template="plotly_white"
)

fig.update_layout(
    height=700,
    legend_title="Company",
    hovermode="x unified",
    title="Stock Performance (Last 1 Year)"
)

st.plotly_chart(fig, use_container_width=True)

st.subheader("Latest Price")

latest = (
    price.iloc[-1]
    .sort_values(ascending=False)
    .to_frame("Value")
)

st.dataframe(latest, use_container_width=True)
