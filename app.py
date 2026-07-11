import streamlit as st
import pandas as pd
import plotly.graph_objects as go

from twelvedata import TDClient
from datetime import datetime
from zoneinfo import ZoneInfo


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="QuantEdge",
    page_icon="Q",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM UI
# ============================================================

st.markdown(
    """
    <style>

    /* MAIN APP */

    .stApp {
        background: #0d0f12;
    }

    .main .block-container {
        max-width: 1000px;
        padding-top: 1.5rem;
        padding-bottom: 7rem;
    }


    /* SIDEBAR */

    [data-testid="stSidebar"] {
        background: #090b0d;
        border-right: 1px solid #202328;
    }

    [data-testid="stSidebar"] .block-container {
        padding-top: 1.5rem;
    }


    /* HIDE STREAMLIT UI */

    #MainMenu {
        visibility: hidden;
    }

    footer {
        visibility: hidden;
    }


    /* TITLE */

    .quant-logo {
        font-size: 25px;
        font-weight: 700;
        letter-spacing: -1px;
        color: #ffffff;
        margin-bottom: 3px;
    }

    .quant-logo span {
        color: #4da3ff;
    }

    .quant-subtitle {
        color: #8b949e;
        font-size: 13px;
        margin-bottom: 25px;
    }


    /* HEADER */

    .app-header {
        border-bottom: 1px solid #25282d;
        padding-bottom: 16px;
        margin-bottom: 30px;
    }

    .app-title {
        font-size: 21px;
        font-weight: 600;
        color: #ffffff;
    }

    .market-open {
        display: inline-block;
        background: rgba(34, 197, 94, 0.12);
        color: #4ade80;
        border: 1px solid rgba(34, 197, 94, 0.25);
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
        margin-top: 7px;
    }

    .market-closed {
        display: inline-block;
        background: rgba(239, 68, 68, 0.10);
        color: #f87171;
        border: 1px solid rgba(239, 68, 68, 0.25);
        padding: 5px 10px;
        border-radius: 20px;
        font-size: 12px;
        margin-top: 7px;
    }


    /* WELCOME */

    .welcome {
        text-align: center;
        padding-top: 60px;
        padding-bottom: 30px;
    }

    .welcome-title {
        font-size: 34px;
        font-weight: 600;
        color: #f5f5f5;
        letter-spacing: -1.5px;
    }

    .welcome-text {
        color: #8b949e;
        font-size: 16px;
        margin-top: 10px;
    }


    /* SIGNAL CARD */

    .signal-card {
        background: #15181c;
        border: 1px solid #292d33;
        border-radius: 16px;
        padding: 22px;
        margin-top: 18px;
        margin-bottom: 18px;
    }

    .signal-label {
        color: #8b949e;
        font-size: 12px;
        text-transform: uppercase;
        letter-spacing: 1px;
    }

    .signal-buy {
        color: #4ade80;
        font-size: 28px;
        font-weight: 700;
        margin-top: 4px;
    }

    .signal-sell {
        color: #f87171;
        font-size: 28px;
        font-weight: 700;
        margin-top: 4px;
    }

    .signal-wait {
        color: #facc15;
        font-size: 28px;
        font-weight: 700;
        margin-top: 4px;
    }


    /* LEVEL CARDS */

    .level-card {
        background: #13161a;
        border: 1px solid #272b31;
        border-radius: 12px;
        padding: 15px;
        text-align: center;
    }

    .level-title {
        color: #8b949e;
        font-size: 11px;
        text-transform: uppercase;
        letter-spacing: 0.7px;
    }

    .level-value {
        color: #ffffff;
        font-size: 20px;
        font-weight: 600;
        margin-top: 6px;
    }


    /* REASON */

    .reason-card {
        background: #121519;
        border-left: 3px solid #4da3ff;
        padding: 12px 15px;
        margin: 8px 0;
        border-radius: 4px 10px 10px 4px;
        color: #d5d7da;
        font-size: 14px;
    }


    /* INFO */

    .market-message {
        background: #14171b;
        border: 1px solid #292d33;
        border-radius: 12px;
        padding: 18px;
        color: #c9cdd2;
        margin: 15px 0;
    }


    /* CHAT INPUT */

    [data-testid="stChatInput"] {
        background: #15181c;
        border: 1px solid #30343a;
        border-radius: 18px;
    }


    /* BUTTONS */

    .stButton > button {
        background: #171a1f;
        color: #d8dadd;
        border: 1px solid #30343a;
        border-radius: 10px;
        transition: 0.2s;
    }

    .stButton > button:hover {
        border-color: #4da3ff;
        color: #ffffff;
        background: #1c2026;
    }


    /* METRICS */

    [data-testid="stMetric"] {
        background: #14171b;
        border: 1px solid #292d33;
        border-radius: 12px;
        padding: 15px;
    }


    /* EXPANDER */

    [data-testid="stExpander"] {
        background: #121519;
        border: 1px solid #292d33;
        border-radius: 12px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# API
# ============================================================

API_KEY = st.secrets["TWELVE_DATA_API_KEY"]

td = TDClient(
    apikey=API_KEY
)

IST = ZoneInfo(
    "Asia/Kolkata"
)


# ============================================================
# MARKET STATUS
# ============================================================

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

        status = "NO FRESH DATA"


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


# ============================================================
# QUANT ENGINE
# ============================================================

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


    # ========================================================
    # EMA
    # ========================================================

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


    # ========================================================
    # RSI
    # ========================================================

    delta = data["Close"].diff()


    gain = delta.clip(

        lower=0

    )


    loss = -delta.clip(

        upper=0

    )


    average_gain = (

        gain

        .rolling(14)

        .mean()

    )


    average_loss = (

        loss

        .rolling(14)

        .mean()

    )


    rs = (

        average_gain

        /

        average_loss

    )


    data["RSI"] = (

        100

        -

        (

            100

            /

            (1 + rs)

        )

    )


    # ========================================================
    # ATR
    # ========================================================

    high_low = (

        data["High"]

        -

        data["Low"]

    )


    high_close = abs(

        data["High"]

        -

        data["Close"].shift()

    )


    low_close = abs(

        data["Low"]

        -

        data["Close"].shift()

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


    # ========================================================
    # MACD
    # ========================================================

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

        ema12

        -

        ema26

    )


    data["MACD_SIGNAL"] = (

        data["MACD"]

        .ewm(

            span=9,

            adjust=False

        )

        .mean()

    )


    # ========================================================
    # MOMENTUM
    # ========================================================

    data["Momentum"] = (

        data["Close"]

        .pct_change(8)

        *

        100

    )


    data = data.dropna()


    latest = data.iloc[-1]


    # ========================================================
    # QUANT SCORE
    # ========================================================

    score = 0


    reasons = []


    if latest["EMA20"] > latest["EMA50"]:

        score += 25

        reasons.append(

            "EMA 20 is above EMA 50. The short-term trend is bullish."

        )


    else:

        score -= 25

        reasons.append(

            "EMA 20 is below EMA 50. The short-term trend is bearish."

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

            "MACD confirms bullish price momentum."

        )


    else:

        score -= 25

        reasons.append(

            "MACD confirms bearish price momentum."

        )


    if latest["Momentum"] > 0:

        score += 20

        reasons.append(

            "Two-hour price momentum is positive."

        )


    else:

        score -= 20

        reasons.append(

            "Two-hour price momentum is negative."

        )


    score = max(

        -100,

        min(

            100,

            score

        )

    )


    # ========================================================
    # SIGNAL
    # ========================================================

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


    # ========================================================
    # MODEL LEVELS
    # ========================================================

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

            entry

            -

            (1.5 * atr)

        )


        target_1 = (

            entry

            +

            (1.5 * atr)

        )


        target_2 = (

            entry

            +

            (3 * atr)

        )


    elif decision in [

        "SELL",

        "STRONG SELL"

    ]:

        stop_loss = (

            entry

            +

            (1.5 * atr)

        )


        target_1 = (

            entry

            -

            (1.5 * atr)

        )


        target_2 = (

            entry

            -

            (3 * atr)

        )


    else:

        stop_loss = None

        target_1 = None

        target_2 = None


    market = get_data_status(

        data

    )


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


# ============================================================
# ANALYSIS RESPONSE
# ============================================================

def display_analysis(result):

    market = result["market"]

    latest = result["latest"]

    decision = result["decision"]


    if decision in [

        "BUY",

        "STRONG BUY"

    ]:

        signal_class = "signal-buy"


    elif decision in [

        "SELL",

        "STRONG SELL"

    ]:

        signal_class = "signal-sell"


    else:

        signal_class = "signal-wait"


    st.markdown(

        f"""
        <div class="signal-card">

            <div class="signal-label">
                QuantEdge Model Signal
            </div>

            <div class="{signal_class}">
                {decision}
            </div>

            <div style="
                color:#8b949e;
                margin-top:8px;
            ">

                Quant Score:
                {result["score"]} / 100

            </div>

        </div>
        """,

        unsafe_allow_html=True

    )


    if not market["active"]:

        st.markdown(

            f"""
            <div class="market-message">

            <b>XAU/USD market data is not active.</b>

            <br><br>

            Market Status:
            {market["status"]}

            <br>

            Last available candle:
            {market["last_candle"]}

            <br><br>

            QuantEdge is displaying the last
            available model analysis.

            No active strategy levels are
            displayed while fresh market data
            is unavailable.

            </div>
            """,

            unsafe_allow_html=True

        )


    elif decision == "WAIT":

        st.markdown(

            """
            <div class="market-message">

            <b>No valid model setup.</b>

            <br><br>

            The quantitative indicators have
            mixed confirmation.

            QuantEdge is waiting for stronger
            strategy alignment.

            </div>
            """,

            unsafe_allow_html=True

        )


    else:

        st.markdown(

            "### Model Strategy Levels"

        )


        col1, col2, col3, col4 = (

            st.columns(4)

        )


        with col1:

            st.markdown(

                f"""
                <div class="level-card">

                    <div class="level-title">
                        Entry Reference
                    </div>

                    <div class="level-value">
                        {result["entry"]:.2f}
                    </div>

                </div>
                """,

                unsafe_allow_html=True

            )


        with col2:

            st.markdown(

                f"""
                <div class="level-card">

                    <div class="level-title">
                        Stop Level
                    </div>

                    <div class="level-value">
                        {result["stop_loss"]:.2f}
                    </div>

                </div>
                """,

                unsafe_allow_html=True

            )


        with col3:

            st.markdown(

                f"""
                <div class="level-card">

                    <div class="level-title">
                        Target 1
                    </div>

                    <div class="level-value">
                        {result["target_1"]:.2f}
                    </div>

                </div>
                """,

                unsafe_allow_html=True

            )


        with col4:

            st.markdown(

                f"""
                <div class="level-card">

                    <div class="level-title">
                        Target 2
                    </div>

                    <div class="level-value">
                        {result["target_2"]:.2f}
                    </div>

                </div>
                """,

                unsafe_allow_html=True

            )


    st.markdown(

        "### Why did the model generate this signal?"

    )


    for reason in result["reasons"]:

        st.markdown(

            f"""
            <div class="reason-card">
                {reason}
            </div>
            """,

            unsafe_allow_html=True

        )


    with st.expander(

        "View Market Metrics"

    ):

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

            f'{latest["Momentum"]:.3f}%'

        )


    with st.expander(

        "Open XAU/USD Chart"

    ):

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

            height=480,

            template="plotly_dark",

            paper_bgcolor="#121519",

            plot_bgcolor="#121519",

            hovermode="x unified",

            margin=dict(

                l=20,

                r=20,

                t=30,

                b=20

            )

        )


        st.plotly_chart(

            fig,

            use_container_width=True

        )


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.markdown(

        """
        <div class="quant-logo">
            Quant<span>Edge</span>
        </div>

        <div class="quant-subtitle">
            XAU/USD Quant Research
        </div>
        """,

        unsafe_allow_html=True

    )


    if st.button(

        "+ New Analysis",

        use_container_width=True

    ):

        st.session_state.messages = []

        if "result" in st.session_state:

            del st.session_state.result

        st.rerun()


    st.markdown("---")


    st.markdown("##### MARKET")


    st.write("XAU/USD")

    st.caption("Spot Gold / US Dollar")


    st.markdown("##### TIMEFRAME")


    st.write("15 Minutes")


    st.markdown("##### TIMEZONE")


    st.write("Indian Standard Time")


    st.markdown("---")


    with st.expander(

        "Quant Engine"

    ):

        st.write("EMA 20 / EMA 50")

        st.write("RSI 14")

        st.write("MACD")

        st.write("ATR 14")

        st.write("2H Momentum")


    st.markdown("---")


    st.caption(

        "QuantEdge Research Engine"

    )


# ============================================================
# HEADER
# ============================================================

st.markdown(

    """
    <div class="app-header">

        <div class="app-title">
            QuantEdge AI
        </div>

        <div style="
            color:#8b949e;
            font-size:13px;
            margin-top:5px;
        ">

            Explainable quantitative analysis
            for XAU/USD

        </div>

    </div>
    """,

    unsafe_allow_html=True

)


# ============================================================
# WELCOME SCREEN
# ============================================================

if len(

    st.session_state.messages

) == 0:

    st.markdown(

        """
        <div class="welcome">

            <div class="welcome-title">
                How can I help with Gold?
            </div>

            <div class="welcome-text">

                Ask QuantEdge to analyze
                XAU/USD market conditions.

            </div>

        </div>
        """,

        unsafe_allow_html=True

    )


    col1, col2, col3 = st.columns(3)


    with col1:

        buy_prompt = st.button(

            "Should the model signal BUY or SELL?",

            use_container_width=True

        )


    with col2:

        trend_prompt = st.button(

            "Explain the current Gold trend",

            use_container_width=True

        )


    with col3:

        strategy_prompt = st.button(

            "Run quantitative analysis",

            use_container_width=True

        )


else:

    buy_prompt = False

    trend_prompt = False

    strategy_prompt = False


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(

        message["role"]

    ):

        st.markdown(

            message["content"]

        )


        if (

            message["role"] == "assistant"

            and

            message.get("show_analysis", False)

            and

            "result" in st.session_state

        ):

            display_analysis(

                st.session_state.result

            )


# ============================================================
# CHAT INPUT
# ============================================================

user_question = st.chat_input(

    "Ask QuantEdge about XAU/USD..."

)


if buy_prompt:

    user_question = (

        "Should the model signal BUY or SELL?"

    )


elif trend_prompt:

    user_question = (

        "Explain the current Gold trend"

    )


elif strategy_prompt:

    user_question = (

        "Run quantitative analysis"

    )


# ============================================================
# PROCESS QUESTION
# ============================================================

if user_question:

    st.session_state.messages.append(

        {

            "role": "user",

            "content": user_question

        }

    )


    try:

        with st.spinner(

            "Analyzing XAU/USD market data..."

        ):

            result = analyze_xauusd()


        st.session_state.result = result


        market = result["market"]


        if not market["active"]:

            response = f"""
I analyzed the latest available XAU/USD data.

The market data status is **{market["status"]}**.

The last available model signal is **{result["decision"]}**
with a Quant Score of **{result["score"]}/100**.

Because fresh market data is unavailable,
QuantEdge is not displaying active model
entry, stop, or target levels.

The indicator reasoning is shown below.
"""


        elif result["decision"] == "WAIT":

            response = f"""
I analyzed the latest XAU/USD 15-minute data.

The current model signal is **WAIT**.

Quant Score: **{result["score"]}/100**

The quantitative indicators have mixed
confirmation, so the strategy does not
currently generate a valid BUY or SELL setup.

The full model reasoning is shown below.
"""


        else:

            response = f"""
I analyzed the latest XAU/USD 15-minute data.

The quantitative model signal is
**{result["decision"]}**.

Quant Score: **{result["score"]}/100**

The research strategy generated ATR-based
model levels and indicator reasoning below.
"""


        st.session_state.messages.append(

            {

                "role": "assistant",

                "content": response,

                "show_analysis": True

            }

        )


        st.rerun()


    except Exception as error:

        st.session_state.messages.append(

            {

                "role": "assistant",

                "content": (
                    "I could not retrieve or analyze "
                    "the XAU/USD market data. "
                    f"Data error: {error}"
                ),

                "show_analysis": False

            }

        )


        st.rerun()


# ============================================================
# FOOTER
# ============================================================

st.markdown("---")

st.caption(

    "QuantEdge is an educational quantitative "
    "strategy research system. Model signals and "
    "ATR-based levels are analytical outputs, not "
    "guaranteed market outcomes or personalized "
    "trading instructions."

)
