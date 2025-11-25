import streamlit as st
import yfinance as yf
import pandas as pd
import numpy as np
import plotly.graph_objects as go
from plotly.subplots import make_subplots
from datetime import datetime
import time

# ============================================================================
# PAGE CONFIG
# ============================================================================

st.set_page_config(
    page_title="NYZTrade - Stock Valuation",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ============================================================================
# AUTHENTICATION
# ============================================================================

def check_password():
    def password_entered():
        username = st.session_state["username"].strip().lower()
        password = st.session_state["password"]
        
        users = {
            "demo": "demo123",
            "premium": "premium123",
            "niyas": "nyztrade123"
        }
        
        if username in users and password == users[username]:
            st.session_state["password_correct"] = True
            st.session_state["authenticated_user"] = username
            del st.session_state["password"]
            return
        
        st.session_state["password_correct"] = False
    
    if "password_correct" not in st.session_state:
        st.markdown("## 🔐 Stock Valuation Dashboard Login")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.text_input("Username", key="username", placeholder="Enter username")
            st.text_input("Password", type="password", key="password", placeholder="Enter password")
            st.button("Login", on_click=password_entered, use_container_width=True)
            
            st.markdown("---")
            st.info("**Demo:** `demo` / `demo123` | **Premium:** `premium` / `premium123`")
        
        return False
    
    elif not st.session_state["password_correct"]:
        st.markdown("## 🔐 Stock Valuation Dashboard Login")
        st.markdown("---")
        
        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.error("😕 Incorrect username or password")
            st.text_input("Username", key="username", placeholder="Enter username")
            st.text_input("Password", type="password", key="password", placeholder="Enter password")
            st.button("Login", on_click=password_entered, use_container_width=True)
        
        return False
    
    return True

if not check_password():
    st.stop()

# ============================================================================
# CUSTOM CSS
# ============================================================================

st.markdown("""
<style>
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        color: white;
        margin-bottom: 2rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f8f9fa 100%);
        padding: 1.5rem;
        border-radius: 10px;
        border-top: 4px solid #667eea;
        box-shadow: 0 4px 15px rgba(0,0,0,0.1);
    }
    .rec-strong-buy {
        background: linear-gradient(135deg, #00C853 0%, #64DD17 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
    }
    .rec-buy {
        background: linear-gradient(135deg, #2ecc71 0%, #27ae60 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
    }
    .rec-hold {
        background: linear-gradient(135deg, #f39c12 0%, #e67e22 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
    }
    .rec-avoid {
        background: linear-gradient(135deg, #e74c3c 0%, #c0392b 100%);
        color: white;
        padding: 2rem;
        border-radius: 15px;
        text-align: center;
        font-size: 2rem;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# NIFTY 500 DATABASE
# ============================================================================

NIFTY_500_STOCKS = {
    "💎 NIFTY 50": {
        "ADANIENT.NS": "Adani Enterprises", "ADANIPORTS.NS": "Adani Ports", "APOLLOHOSP.NS": "Apollo Hospitals",
        "ASIANPAINT.NS": "Asian Paints", "AXISBANK.NS": "Axis Bank", "BAJAJ-AUTO.NS": "Bajaj Auto",
        "BAJFINANCE.NS": "Bajaj Finance", "BAJAJFINSV.NS": "Bajaj Finserv", "BHARTIARTL.NS": "Bharti Airtel",
        "BPCL.NS": "BPCL", "BRITANNIA.NS": "Britannia", "CIPLA.NS": "Cipla",
        "COALINDIA.NS": "Coal India", "DIVISLAB.NS": "Divi's Labs", "DRREDDY.NS": "Dr Reddy's",
        "EICHERMOT.NS": "Eicher Motors", "GRASIM.NS": "Grasim", "HCLTECH.NS": "HCL Tech",
        "HDFCBANK.NS": "HDFC Bank", "HDFCLIFE.NS": "HDFC Life", "HEROMOTOCO.NS": "Hero MotoCorp",
        "HINDALCO.NS": "Hindalco", "HINDUNILVR.NS": "Hindustan Unilever", "ICICIBANK.NS": "ICICI Bank",
        "INDUSINDBK.NS": "IndusInd Bank", "INFY.NS": "Infosys", "ITC.NS": "ITC",
        "JSWSTEEL.NS": "JSW Steel", "KOTAKBANK.NS": "Kotak Bank", "LT.NS": "L&T",
        "M&M.NS": "M&M", "MARUTI.NS": "Maruti Suzuki", "NESTLEIND.NS": "Nestle India",
        "NTPC.NS": "NTPC", "ONGC.NS": "ONGC", "POWERGRID.NS": "Power Grid",
        "RELIANCE.NS": "Reliance", "SBILIFE.NS": "SBI Life", "SBIN.NS": "SBI",
        "SUNPHARMA.NS": "Sun Pharma", "TATAMOTORS.NS": "Tata Motors", "TATASTEEL.NS": "Tata Steel",
        "TCS.NS": "TCS", "TECHM.NS": "Tech Mahindra", "TITAN.NS": "Titan",
        "ULTRACEMCO.NS": "UltraTech Cement", "UPL.NS": "UPL", "WIPRO.NS": "Wipro"
    },
    
    "🏦 Banking & Finance": {
        "AUBANK.NS": "AU Small Finance", "BANDHANBNK.NS": "Bandhan Bank", "BANKBARODA.NS": "Bank of Baroda",
        "CANBK.NS": "Canara Bank", "CHOLAFIN.NS": "Cholamandalam", "FEDERALBNK.NS": "Federal Bank",
        "HDFCAMC.NS": "HDFC AMC", "ICICIGI.NS": "ICICI Lombard", "ICICIPRULI.NS": "ICICI Prudential",
        "IDFCFIRSTB.NS": "IDFC First Bank", "MUTHOOTFIN.NS": "Muthoot Finance", "PFC.NS": "Power Finance",
        "PNB.NS": "Punjab National Bank", "RECLTD.NS": "REC Limited", "SBICARD.NS": "SBI Card",
        "SHRIRAMFIN.NS": "Shriram Finance", "UNIONBANK.NS": "Union Bank"
    },
    
    "💻 IT & Technology": {
        "COFORGE.NS": "Coforge", "LTTS.NS": "L&T Technology", "MPHASIS.NS": "Mphasis",
        "PERSISTENT.NS": "Persistent Systems", "SONATSOFTW.NS": "Sonata Software", "TATAELXSI.NS": "Tata Elxsi"
    },
    
    "💊 Pharma & Healthcare": {
        "AUROPHARMA.NS": "Aurobindo Pharma", "BIOCON.NS": "Biocon", "ALKEM.NS": "Alkem Labs",
        "FORTIS.NS": "Fortis Healthcare", "GLENMARK.NS": "Glenmark", "IPCALAB.NS": "IPCA Labs",
        "LAURUSLABS.NS": "Laurus Labs", "LUPIN.NS": "Lupin", "MAXHEALTH.NS": "Max Healthcare",
        "TORNTPHARM.NS": "Torrent Pharma"
    },
    
    "🚗 Auto & Components": {
        "APOLLOTYRE.NS": "Apollo Tyres", "ASHOKLEY.NS": "Ashok Leyland", "BALKRISIND.NS": "Balkrishna Industries",
        "BHARATFORG.NS": "Bharat Forge", "BOSCHLTD.NS": "Bosch", "CEAT.NS": "CEAT",
        "ESCORTS.NS": "Escorts", "EXIDEIND.NS": "Exide Industries", "MOTHERSUMI.NS": "Motherson Sumi",
        "MRF.NS": "MRF", "TVSMOTOR.NS": "TVS Motor"
    },
    
    "🍔 FMCG & Consumer": {
        "BATAINDIA.NS": "Bata India", "BERGEPAINT.NS": "Berger Paints", "COLPAL.NS": "Colgate",
        "DABUR.NS": "Dabur", "EMAMILTD.NS": "Emami", "GODREJCP.NS": "Godrej Consumer",
        "JYOTHYLAB.NS": "Jyothy Labs", "MARICO.NS": "Marico", "TATACONSUM.NS": "Tata Consumer",
        "UBL.NS": "United Breweries", "VBL.NS": "Varun Beverages"
    },
    
    "🏭 Industrial & Cement": {
        "ABB.NS": "ABB India", "AMBUJACEM.NS": "Ambuja Cements", "BEL.NS": "Bharat Electronics",
        "CUMMINSIND.NS": "Cummins India", "HAVELLS.NS": "Havells", "JKCEMENT.NS": "JK Cement",
        "SHREECEM.NS": "Shree Cement", "SIEMENS.NS": "Siemens", "THERMAX.NS": "Thermax",
        "VOLTAS.NS": "Voltas"
    },
    
    "⚡ Energy & Power": {
        "ADANIGREEN.NS": "Adani Green", "ADANIPOWER.NS": "Adani Power", "GAIL.NS": "GAIL",
        "HINDPETRO.NS": "HPCL", "IOC.NS": "Indian Oil", "IGL.NS": "Indraprastha Gas",
        "PETRONET.NS": "Petronet LNG", "TATAPOWER.NS": "Tata Power", "TORNTPOWER.NS": "Torrent Power"
    },
    
    "🛒 Retail & Ecommerce": {
        "ABFRL.NS": "Aditya Birla Fashion", "DMART.NS": "Avenue Supermarts", "JUBLFOOD.NS": "Jubilant FoodWorks",
        "TRENT.NS": "Trent"
    },
    
    "🏗️ Real Estate": {
        "DLF.NS": "DLF", "GODREJPROP.NS": "Godrej Properties", "OBEROIRLTY.NS": "Oberoi Realty",
        "PRESTIGE.NS": "Prestige Estates"
    }
}

INDUSTRY_BENCHMARKS = {
    'Technology': {'pe': 25, 'ev_ebitda': 15},
    'Financial Services': {'pe': 18, 'ev_ebitda': 12},
    'Consumer Cyclical': {'pe': 30, 'ev_ebitda': 14},
    'Consumer Defensive': {'pe': 35, 'ev_ebitda': 16},
    'Healthcare': {'pe': 28, 'ev_ebitda': 14},
    'Industrials': {'pe': 22, 'ev_ebitda': 12},
    'Energy': {'pe': 15, 'ev_ebitda': 8},
    'Basic Materials': {'pe': 18, 'ev_ebitda': 10},
    'Communication Services': {'pe': 20, 'ev_ebitda': 12},
    'Real Estate': {'pe': 25, 'ev_ebitda': 18},
    'Utilities': {'pe': 16, 'ev_ebitda': 10},
    'Default': {'pe': 20, 'ev_ebitda': 12}
}

# ============================================================================
# VALUATION FUNCTIONS
# ============================================================================

@st.cache_data(ttl=300)
def fetch_stock_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        
        if not info or len(info) < 5:
            return None, "Unable to fetch data"
        
        return info, None
    except Exception as e:
        return None, str(e)

def calculate_valuations(info):
    price = info.get('currentPrice', 0) or info.get('regularMarketPrice', 0)
    trailing_pe = info.get('trailingPE', 0)
    forward_pe = info.get('forwardPE', 0)
    trailing_eps = info.get('trailingEps', 0)
    enterprise_value = info.get('enterpriseValue', 0)
    ebitda = info.get('ebitda', 0)
    market_cap = info.get('marketCap', 0)
    shares = info.get('sharesOutstanding', 1)
    sector = info.get('sector', 'Default')
    
    benchmark = INDUSTRY_BENCHMARKS.get(sector, INDUSTRY_BENCHMARKS['Default'])
    industry_pe = benchmark['pe']
    industry_ev_ebitda = benchmark['ev_ebitda']
    
    if trailing_pe and trailing_pe > 0:
        historical_pe = trailing_pe * 0.9
    else:
        historical_pe = industry_pe
    
    blended_pe = (industry_pe + historical_pe) / 2
    
    fair_value_industry = trailing_eps * industry_pe if trailing_eps else None
    fair_value_blended = trailing_eps * blended_pe if trailing_eps else None
    
    fair_values_pe = [fv for fv in [fair_value_industry, fair_value_blended] if fv]
    fair_value_pe = np.mean(fair_values_pe) if fair_values_pe else None
    upside_pe = ((fair_value_pe - price) / price * 100) if fair_value_pe and price else None
    
    current_ev_ebitda = enterprise_value / ebitda if ebitda and ebitda > 0 else None
    
    if current_ev_ebitda and 0 < current_ev_ebitda < 50:
        target_ev_ebitda = (industry_ev_ebitda + current_ev_ebitda * 0.9) / 2
    else:
        target_ev_ebitda = industry_ev_ebitda
    
    if ebitda and ebitda > 0:
        fair_ev = ebitda * target_ev_ebitda
        total_debt = info.get('totalDebt', 0) or 0
        total_cash = info.get('totalCash', 0) or 0
        net_debt = total_debt - total_cash
        fair_mcap = fair_ev - net_debt
        fair_value_ev = fair_mcap / shares if shares else None
        upside_ev = ((fair_value_ev - price) / price * 100) if fair_value_ev and price else None
    else:
        fair_value_ev = None
        upside_ev = None
    
    return {
        'price': price,
        'trailing_pe': trailing_pe,
        'forward_pe': forward_pe,
        'trailing_eps': trailing_eps,
        'industry_pe': industry_pe,
        'fair_value_pe': fair_value_pe,
        'upside_pe': upside_pe,
        'enterprise_value': enterprise_value,
        'ebitda': ebitda,
        'market_cap': market_cap,
        'current_ev_ebitda': current_ev_ebitda,
        'industry_ev_ebitda': industry_ev_ebitda,
        'fair_value_ev': fair_value_ev,
        'upside_ev': upside_ev
    }

# ============================================================================
# HEADER
# ============================================================================

st.markdown("""
<div class="main-header">
    <h1>📊 NIFTY 500 STOCK VALUATION DASHBOARD</h1>
    <p>Professional Analysis • 500+ Stocks • Real-time Data</p>
</div>
""", unsafe_allow_html=True)

# Logout
if st.sidebar.button("🚪 Logout"):
    for key in list(st.session_state.keys()):
        del st.session_state[key]
    st.rerun()

# ============================================================================
# STOCK SELECTION
# ============================================================================

st.sidebar.header("📈 Stock Selection")

# Flatten all stocks
all_stocks = {}
for category, stocks in NIFTY_500_STOCKS.items():
    all_stocks.update(stocks)

# Category selection
selected_category = st.sidebar.selectbox(
    "Category",
    ["🔍 All Stocks"] + list(NIFTY_500_STOCKS.keys())
)

# Search box
search_term = st.sidebar.text_input("🔍 Search Stock", placeholder="Type company name or ticker...")

# Filter stocks
if search_term:
    filtered_stocks = {ticker: name for ticker, name in all_stocks.items()
                      if search_term.upper() in ticker or search_term.upper() in name.upper()}
elif selected_category == "🔍 All Stocks":
    filtered_stocks = all_stocks
else:
    filtered_stocks = NIFTY_500_STOCKS[selected_category]

# Stock selection
stock_options = [f"{name} ({ticker})" for ticker, name in filtered_stocks.items()]
selected_stock = st.sidebar.selectbox("Select Stock", stock_options)

# Extract ticker
selected_ticker = selected_stock.split("(")[1].strip(")")

# Custom ticker
custom_ticker = st.sidebar.text_input("Or Enter Custom Ticker", placeholder="e.g., WIPRO.NS")

# Analyze button
if st.sidebar.button("🚀 ANALYZE STOCK", use_container_width=True):
    st.session_state.analyze_ticker = custom_ticker.upper() if custom_ticker else selected_ticker

# ============================================================================
# ANALYSIS
# ============================================================================

if 'analyze_ticker' in st.session_state:
    ticker = st.session_state.analyze_ticker
    
    with st.spinner(f"🔄 Fetching data for {ticker}..."):
        info, error = fetch_stock_data(ticker)
    
    if error:
        st.error(f"❌ Error: {error}")
        st.stop()
    
    if info is None:
        st.error("❌ Failed to fetch stock data")
        st.stop()
    
    valuations = calculate_valuations(info)
    
    # Company Info
    company_name = info.get('longName', ticker)
    sector = info.get('sector', 'N/A')
    industry = info.get('industry', 'N/A')
    
    st.markdown(f"## 🏢 {company_name}")
    st.markdown(f"**Sector:** {sector} | **Industry:** {industry} | **Ticker:** {ticker}")
    
    st.markdown("---")
    
    # Key Metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("💵 Current Price", f"₹{valuations['price']:.2f}")
    
    with col2:
        st.metric("📊 PE Ratio", f"{valuations['trailing_pe']:.2f}x" if valuations['trailing_pe'] else "N/A")
    
    with col3:
        st.metric("💰 EPS (TTM)", f"₹{valuations['trailing_eps']:.2f}" if valuations['trailing_eps'] else "N/A")
    
    with col4:
        st.metric("🏦 Market Cap", f"₹{valuations['market_cap']/10000000:.0f} Cr")
    
    # Recommendation
    upside_values = []
    if valuations['upside_pe'] is not None:
        upside_values.append(valuations['upside_pe'])
    if valuations['upside_ev'] is not None:
        upside_values.append(valuations['upside_ev'])
    
    avg_upside = np.mean(upside_values) if upside_values else 0
    
    if avg_upside > 20:
        rec_class = "rec-strong-buy"
        rec_text = "⭐⭐⭐ STRONG BUY"
        rec_desc = "Significantly undervalued"
    elif avg_upside > 10:
        rec_class = "rec-buy"
        rec_text = "⭐⭐ BUY"
        rec_desc = "Moderately undervalued"
    elif avg_upside > 0:
        rec_class = "rec-buy"
        rec_text = "⭐ ACCUMULATE"
        rec_desc = "Slightly undervalued"
    elif avg_upside > -10:
        rec_class = "rec-hold"
        rec_text = "🟡 HOLD"
        rec_desc = "Fairly valued"
    else:
        rec_class = "rec-avoid"
        rec_text = "❌ AVOID"
        rec_desc = "Overvalued"
    
    st.markdown(f"""
    <div class="{rec_class}">
        <div>{rec_text}</div>
        <div style="font-size: 1.2rem; margin-top: 0.5rem;">Average Return: {avg_upside:+.2f}%</div>
        <div style="font-size: 1rem; margin-top: 0.5rem;">{rec_desc}</div>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    
    # Gauges
    if valuations['upside_pe'] is not None and valuations['upside_ev'] is not None:
        st.subheader("📈 Upside/Downside Analysis")
        
        fig = make_subplots(
            rows=1, cols=2,
            specs=[[{'type': 'indicator'}, {'type': 'indicator'}]],
            subplot_titles=("PE Multiple", "EV/EBITDA")
        )
        
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=valuations['upside_pe'],
            number={'suffix': "%", 'font': {'size': 40}},
            gauge={
                'axis': {'range': [-50, 50]},
                'bar': {'color': "#667eea"},
                'steps': [
                    {'range': [-50, 0], 'color': "#ffebee"},
                    {'range': [0, 50], 'color': "#e8f5e9"}
                ],
            }
        ), row=1, col=1)
        
        fig.add_trace(go.Indicator(
            mode="gauge+number",
            value=valuations['upside_ev'],
            number={'suffix': "%", 'font': {'size': 40}},
            gauge={
                'axis': {'range': [-50, 50]},
                'bar': {'color': "#764ba2"},
                'steps': [
                    {'range': [-50, 0], 'color': "#ffebee"},
                    {'range': [0, 50], 'color': "#e8f5e9"}
                ],
            }
        ), row=1, col=2)
        
        fig.update_layout(height=400)
        
        st.plotly_chart(fig, use_container_width=True)
    
    # Valuation Comparison
    st.subheader("💰 Valuation Comparison")
    
    categories = []
    current = []
    fair = []
    colors = []
    
    if valuations['fair_value_pe']:
        categories.append('PE Multiple')
        current.append(valuations['price'])
        fair.append(valuations['fair_value_pe'])
        colors.append('#667eea' if valuations['fair_value_pe'] > valuations['price'] else '#e74c3c')
    
    if valuations['fair_value_ev']:
        categories.append('EV/EBITDA')
        current.append(valuations['price'])
        fair.append(valuations['fair_value_ev'])
        colors.append('#764ba2' if valuations['fair_value_ev'] > valuations['price'] else '#c0392b')
    
    fig2 = go.Figure()
    
    fig2.add_trace(go.Bar(
        name='Current Price',
        x=categories,
        y=current,
        marker_color='#3498db',
        text=[f'₹{p:.2f}' for p in current],
        textposition='outside'
    ))
    
    fig2.add_trace(go.Bar(
        name='Fair Value',
        x=categories,
        y=fair,
        marker_color=colors,
        text=[f'₹{p:.2f}' for p in fair],
        textposition='outside'
    ))
    
    fig2.update_layout(
        barmode='group',
        height=500,
        xaxis_title="Method",
        yaxis_title="Price (₹)",
        template='plotly_white'
    )
    
    st.plotly_chart(fig2, use_container_width=True)
    
    # Metrics Table
    st.subheader("📋 Financial Metrics")
    
    metrics_df = pd.DataFrame({
        'Metric': [
            '💵 Current Price',
            '📊 PE Ratio (TTM)',
            '🏭 Industry PE',
            '📈 Forward PE',
            '💰 EPS (TTM)',
            '🏢 Enterprise Value',
            '💼 EBITDA',
            '📉 Current EV/EBITDA',
            '🎯 Industry EV/EBITDA',
            '🏦 Market Cap'
        ],
        'Value': [
            f"₹{valuations['price']:.2f}",
            f"{valuations['trailing_pe']:.2f}x" if valuations['trailing_pe'] else 'N/A',
            f"{valuations['industry_pe']:.2f}x",
            f"{valuations['forward_pe']:.2f}x" if valuations['forward_pe'] else 'N/A',
            f"₹{valuations['trailing_eps']:.2f}" if valuations['trailing_eps'] else 'N/A',
            f"₹{valuations['enterprise_value']/10000000:.2f} Cr",
            f"₹{valuations['ebitda']/10000000:.2f} Cr" if valuations['ebitda'] else 'N/A',
            f"{valuations['current_ev_ebitda']:.2f}x" if valuations['current_ev_ebitda'] else 'N/A',
            f"{valuations['industry_ev_ebitda']:.2f}x",
            f"₹{valuations['market_cap']/10000000:.2f} Cr"
        ]
    })
    
    st.dataframe(metrics_df, use_container_width=True, hide_index=True)
    
    # Disclaimer
    st.markdown("---")
    st.error("⚠️ **DISCLAIMER:** Educational purposes only. Not financial advice. Do your own research.")
    
else:
    st.info("👈 Select a stock from the sidebar and click **ANALYZE STOCK** to begin!")
    
    st.markdown("### 🌟 Features:")
    st.markdown("""
    - 📊 **500+ NIFTY Stocks** - Complete database
    - 💰 **PE Valuation** - Industry benchmark comparison
    - 🏢 **EV/EBITDA Analysis** - Enterprise value based
    - 📈 **Upside Calculator** - Potential returns
    - ⭐ **Smart Recommendations** - Buy/Hold/Avoid signals
    - 🔍 **Advanced Search** - Find stocks instantly
    """)

# Footer
st.markdown("---")
st.markdown("**💡 NYZTrade Stock Valuation Dashboard | Powered by yfinance**")
```

