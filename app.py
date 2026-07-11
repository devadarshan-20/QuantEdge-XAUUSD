
import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from twelvedata import TDClient
from datetime import datetime
from zoneinfo import ZoneInfo


st.set_page_config(
    page_title="QuantEdge XAU/USD",
    page_icon="📊",
    layout="wide"
)


# =========================
# SECURE API KEY
# =========================

API_KEY = st.secrets["TWELVE_DATA_API_KEY"]

td = TDClient(apikey=API_KEY)

IST = ZoneInfo("Asia/Kolkata")


# =========================
# MARKET DATA STATUS
# =========================

def get_data_status(data):

    now_ist = datetime.now(IST)

    last_candle = data.index[-1]

    if last_candle.tzinfo is None:
        last_candle = last_candle.replace(
            tzinfo=IST
        )

    age = now_ist - last_candle

    age_minutes = (
        age.total_seconds() / 60
    )

    weekday = now_ist.weekday()

    if weekday in [5, 6]:

        active = False
        status = "WEEKEND CLOSED"

    elif age_minutes > 45:

        active = False
        status = "NO FRESH XAU/USD DATA"

    else:

        active = True
        status = "MARKET ACTIVE"

    return {
        "active": active,
        "status": status,
        "ist_time": now_ist,
        "last_candle": last_candle,
        "age_minutes": age_minutes
    }


# =========================
# XAUUSD QUANT ENGINE
# =========================

def analyze_xauusd():

    ts = td.time_series(
        symbol="XAU/USD",
        interval="15min",
        outputsize=5000,
        timezone="Asia/Kolkata"
    )

    data = ts.as_pandas()

    data = data.sort_index()

    data.columns = [
        column.capitalize()
        for column in data.columns
    ]

    data = data[
        [
            "Open",
            "High",
            "Low",
            "Close"
        ]
    ]

    data = data.astype(float)

    data = data.dropna()


    # EMA

    data["EMA20"] = (
        data["Close"]
        .ewm(
            span=20,
            adjust=False
        )
        .mean()
    )

    data["EMA50"] = (
        data["Close"]
        .ewm(
            span=50,
            adjust=False
        )
        .mean()
    )


    # RSI

    delta = data["Close"].diff()

    gain = delta.clip(lower=0)

    loss = -delta.clip(upper=0)

    avg_gain = gain.rolling(14).mean()

    avg_loss = loss.rolling(14).mean()

    rs = avg_gain / avg_loss

    data["RSI"] = (
        100 - (100 / (1 + rs))
    )


    # ATR

    high_low = (
        data["High"] - data["Low"]
    )

    high_close = abs(
        data["High"]
        - data["Close"].shift()
    )

    low_close = abs(
        data["Low"]
        - data["Close"].shift()
    )

    true_range = pd.concat(
        [
            high_low,
            high_close,
            low_close
        ],
        axis=1
    ).max(axis=1)

    data["ATR"] = (
        true_range
        .rolling(14)
        .mean()
    )


    # MACD

    ema12 = (
        data["Close"]
        .ewm(
            span=12,
            adjust=False
        )
        .mean()
    )

    ema26 = (
        data["Close"]
        .ewm(
            span=26,
            adjust=False
        )
        .mean()
    )

    data["MACD"] = (
        ema12 - ema26
    )

    data["MACD_SIGNAL"] = (
        data["MACD"]
        .ewm(
            span=9,
            adjust=False
        )
        .mean()
    )


    # 2 HOUR MOMENTUM

    data["Momentum"] = (
        data["Close"]
        .pct_change(8)
        * 100
    )


    data = data.dropna()

    latest = data.iloc[-1]


    # =========================
    # QUANT SCORE
    # =========================

    score = 0

    reasons = []


    if latest["EMA20"] > latest["EMA50"]:

        score += 25

        reasons.append(
            "EMA 20 is above EMA 50. Trend is bullish."
        )

    else:

        score -= 25

        reasons.append(
            "EMA 20 is below EMA 50. Trend is bearish."
        )


    if latest["RSI"] >= 60:

        score += 20

        reasons.append(
            "RSI shows strong bullish momentum."
        )

    elif latest["RSI"] >= 50:

        score += 10

        reasons.append(
            "RSI shows moderate bullish momentum."
        )

    elif latest["RSI"] <= 40:

        score -= 20

        reasons.append(
            "RSI shows strong bearish momentum."
        )

    else:

        score -= 10

        reasons.append(
            "RSI shows moderate bearish momentum."
        )


    if latest["MACD"] > latest["MACD_SIGNAL"]:

        score += 25

        reasons.append(
            "MACD confirms bullish momentum."
        )

    else:

        score -= 25

        reasons.append(
            "MACD confirms bearish momentum."
        )


    if latest["Momentum"] > 0:

        score += 20

        reasons.append(
            "2-hour price momentum is positive."
        )

    else:

        score -= 20

        reasons.append(
            "2-hour price momentum is negative."
        )


    score = max(
        -100,
        min(100, score)
    )


    # =========================
    # STRATEGY SIGNAL
    # =========================

    if score >= 60:

        decision = "STRONG BUY"

    elif score >= 25:

        decision = "BUY"

    elif score <= -60:

        decision = "STRONG SELL"

    elif score <= -25:

        decision = "SELL"

    else:

        decision = "WAIT"


    # =========================
    # ATR STRATEGY LEVELS
    # =========================

    entry = float(
        latest["Close"]
    )

    atr = float(
        latest["ATR"]
    )


    if decision in [
        "BUY",
        "STRONG BUY"
    ]:

        stop_loss = (
            entry - (1.5 * atr)
        )

        target_1 = (
            entry + (1.5 * atr)
        )

        target_2 = (
            entry + (3 * atr)
        )


    elif decision in [
        "SELL",
        "STRONG SELL"
    ]:

        stop_loss = (
            entry + (1.5 * atr)
        )

        target_1 = (
            entry - (1.5 * atr)
        )

        target_2 = (
            entry - (3 * atr)
        )


    else:

        stop_loss = None

        target_1 = None

        target_2 = None


    market = get_data_status(data)


    return {
        "data": data,
        "latest": latest,
        "decision": decision,
        "score": score,
        "reasons": reasons,
        "entry": entry,
        "stop_loss": stop_loss,
        "target_1": target_1,
        "target_2": target_2,
        "market": market
    }


# =========================
# USER INTERFACE
# =========================

st.title("QuantEdge")

st.caption(
    "Explainable XAU/USD Quantitative Strategy Engine"
)


st.info(
    "Instrument: XAU/USD Spot Gold | "
    "Timeframe: 15 Minutes | "
    "Timezone: Indian Standard Time"
)


if st.button(
    "Analyze XAU/USD",
    use_container_width=True,
    type="primary"
):

    try:

        with st.spinner(
            "Downloading fresh XAU/USD data and analyzing market..."
        ):

            st.session_state.result = (
                analyze_xauusd()
            )

    except Exception as error:

        st.error(
            f"Market data error: {error}"
        )


if "result" in st.session_state:

    result = st.session_state.result

    latest = result["latest"]

    market = result["market"]


    st.divider()


    col1, col2, col3 = st.columns(3)


    col1.metric(
        "Market Status",
        market["status"]
    )


    col2.metric(
        "Strategy Signal",
        result["decision"]
    )


    col3.metric(
        "Quant Score",
        f'{result["score"]} / 100'
    )


    st.caption(
        "Last XAU/USD candle: "
        f'{market["last_candle"]}'
    )


    st.subheader(
        "Market Metrics"
    )


    col1, col2, col3, col4 = (
        st.columns(4)
    )


    col1.metric(
        "XAU/USD",
        f'{result["entry"]:.2f}'
    )


    col2.metric(
        "RSI",
        f'{latest["RSI"]:.2f}'
    )


    col3.metric(
        "ATR",
        f'{latest["ATR"]:.2f}'
    )


    col4.metric(
        "2H Momentum",
        f'{latest["Momentum"]:.2f}%'
    )


    if (
        market["active"]
        and
        result["decision"] != "WAIT"
    ):

        st.subheader(
            "Model Strategy Levels"
        )


        col1, col2, col3, col4 = (
            st.columns(4)
        )


        col1.metric(
            "Entry Reference",
            f'{result["entry"]:.2f}'
        )


        col2.metric(
            "Stop Loss",
            f'{result["stop_loss"]:.2f}'
        )


        col3.metric(
            "Target 1",
            f'{result["target_1"]:.2f}'
        )


        col4.metric(
            "Target 2",
            f'{result["target_2"]:.2f}'
        )


    elif not market["active"]:

        st.warning(
            f'XAU/USD data status: {market["status"]}. '
            "No active strategy levels are shown."
        )


    else:

        st.warning(
            "Strategy signal is WAIT. "
            "The model does not currently generate "
            "a valid setup."
        )


    st.subheader(
        "XAU/USD Price Analysis"
    )


    chart_data = (
        result["data"]
        .tail(200)
    )


    fig = go.Figure()


    fig.add_trace(
        go.Scatter(
            x=chart_data.index,
            y=chart_data["Close"],
            name="XAU/USD"
        )
    )


    fig.add_trace(
        go.Scatter(
            x=chart_data.index,
            y=chart_data["EMA20"],
            name="EMA 20"
        )
    )


    fig.add_trace(
        go.Scatter(
            x=chart_data.index,
            y=chart_data["EMA50"],
            name="EMA 50"
        )
    )


    fig.update_layout(
        height=500,
        xaxis_title="Indian Standard Time",
        yaxis_title="XAU/USD Price",
        hovermode="x unified"
    )


    st.plotly_chart(
        fig,
        use_container_width=True
    )


    st.subheader(
        "Model Reasoning"
    )


    for reason in result["reasons"]:

        st.write(
            "•",
            reason
        )


    st.divider()


    st.subheader(
        "Ask QuantEdge"
    )


    question = st.text_input(
        "Ask about the current XAU/USD strategy",
        placeholder="Should the model signal BUY, SELL, or WAIT?"
    )


    if st.button(
        "Ask QuantEdge"
    ):

        if not question:

            st.warning(
                "Enter a question."
            )


        elif not market["active"]:

            st.info(
                f"""
XAU/USD data is currently not active.

Market status: {market["status"]}

Last model signal: {result["decision"]}

Quant Score: {result["score"]}/100

No active strategy levels are displayed while
fresh market data is unavailable.
"""
            )


        elif result["decision"] == "WAIT":

            st.info(
                f"""
Current model signal: WAIT

Quant Score: {result["score"]}/100

The indicators have mixed confirmation.

The model does not currently generate
a valid BUY or SELL setup.
"""
            )


        else:

            st.success(
                f"""
Current model signal: {result["decision"]}

Quant Score: {result["score"]}/100

Model Entry Reference: {result["entry"]:.2f}

Model Stop Loss: {result["stop_loss"]:.2f}

Model Target 1: {result["target_1"]:.2f}

Model Target 2: {result["target_2"]:.2f}

The signal is generated using EMA trend,
RSI momentum, MACD confirmation,
ATR volatility and 2-hour price momentum.
"""
            )


st.divider()

st.caption(
    "QuantEdge is an educational quantitative "
    "strategy research project. Model-generated "
    "signals and levels are not guaranteed outcomes."
)
