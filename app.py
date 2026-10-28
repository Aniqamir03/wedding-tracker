# =============================================
# 💍 WEDDING FUND TRACKER: NATIVE PRO UI
# FEATURES: CUSTOM CSS TABS • NO INSTALL REQUIRED
# =============================================

import streamlit as st
import pandas as pd
import gspread
import plotly.express as px
import time
from oauth2client.service_account import ServiceAccountCredentials
from datetime import datetime, date, timedelta

# =============================================
# 🔐 CONFIGURATION
# =============================================

USER1_NAME = st.secrets["names"]["user1"]
USER2_NAME = st.secrets["names"]["user2"]

USERS_DB = {
    st.secrets["passwords"]["user1_pass"]: USER1_NAME,
    st.secrets["passwords"]["user2_pass"]: USER2_NAME
}

SHEET_NAME = "Tabung Kahwin Database"
TARGET_AMOUNT = 30000
WEDDING_DATE = date(2027, 6, 5)
COUPLE_NAMES = [USER1_NAME, USER2_NAME]

# --- 📲 TELEGRAM CONFIGURATION ---
TELEGRAM_BOT_TOKEN = st.secrets["telegram"]["bot_token"]

RECIPIENTS = {
    USER1_NAME: st.secrets["telegram"]["user1_id"],
    USER2_NAME: st.secrets["telegram"]["user2_id"]
}

# --- 🎮 GAMIFICATION MILESTONES ---
MILESTONES = [
    {"amount": 800, "title": "First Step", "icon": "🌱", "badge": "Beginner", "color": "#90EE90"},
    {"amount": 2000, "title": "Getting Started", "icon": "🚀", "badge": "Starter", "color": "#87CEEB"},
    {"amount": 5000, "title": "Quarter Way", "icon": "⭐", "badge": "Bronze", "color": "#CD7F32"},
    {"amount": 7500, "title": "One Third", "icon": "💪", "badge": "Silver", "color": "#C0C0C0"},
    {"amount": 10000, "title": "Halfway Hero", "icon": "🏆", "badge": "Gold", "color": "#FFD700"},
    {"amount": 15000, "title": "Halfway There", "icon": "🎯", "badge": "Platinum", "color": "#E5E4E2"},
    {"amount": 20000, "title": "Two Thirds", "icon": "💎", "badge": "Diamond", "color": "#B9F2FF"},
    {"amount": 25000, "title": "Almost There", "icon": "🔥", "badge": "Master", "color": "#FF6B6B"},
    {"amount": 30000, "title": "Goal Achieved!", "icon": "👑", "badge": "Champion", "color": "#FFD700"}
]

# =============================================
# 🛠️ UTILITY FUNCTIONS
# =============================================
def get_mys_time():
    return datetime.utcnow() + timedelta(hours=8)

def get_mys_date():
    return get_mys_time().date()

def send_telegram_alert(name, amount, total_now):
    msg = f"💍 *Tabung Update: Simpanan Baru* 💍\n\n👤 *Oleh:* {name}\n💵 *Jumlah:* RM {amount:.2f}\n💰 *Baki Terkini:* RM {total_now:,.2f}\n\n_Tracked via WeddingApp_"
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    
    for person, chat_id in RECIPIENTS.items():
        try: 
            import requests
            requests.post(url, data={"chat_id": chat_id, "text": msg, "parse_mode": "Markdown"})
        except: pass

def get_current_milestone(amount):
    """Get the current milestone based on amount"""
    achieved = [m for m in MILESTONES if amount >= m["amount"]]
    return achieved[-1] if achieved else None

def get_next_milestone(amount):
    """Get the next milestone to achieve"""
    upcoming = [m for m in MILESTONES if amount < m["amount"]]
    return upcoming[0] if upcoming else None

def calculate_milestone_progress(amount):
    """Calculate progress towards next milestone"""
    next_m = get_next_milestone(amount)
    if not next_m:
        return 100
    
    current_m = get_current_milestone(amount)
    start = current_m["amount"] if current_m else 0
    end = next_m["amount"]
    
    progress = ((amount - start) / (end - start)) * 100
    return min(max(progress, 0), 100)

# =============================================
# 🎨 PREMIUM CSS & ANIMATION ENGINE
# =============================================
st.set_page_config(page_title="Wedding Fund Tracker", page_icon="💍", layout="wide")

def local_css():
    st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;600;700;800&display=swap');
    @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:wght@600;700&display=swap');

    :root {
        --sage-dark: #2E5834;
        --sage-primary: #4F7942;
        --sage-light: #8FBC8F;
        --gold: #C5A059;
        --text-color: #1a1a1a;
        --bg-color: #F1F8E9;
    }

    html, body, [class*="css"] { font-family: 'Inter', sans-serif; color: var(--text-color); }
    
    .stApp {
        background: linear-gradient(135deg, #F1F8E9 0%, #E0F2F1 50%, #E8F5E9 100%);
        background-attachment: fixed;
    }

    /* SIDEBAR FIX */
    [data-testid="stSidebar"] { background-color: #ffffff; border-right: 1px solid #e0e0e0; }
    [data-testid="stSidebar"] * { color: #333333 !important; }

    /* 🔥 CUSTOM TAB DESIGN (GAYA IPHONE) 🔥 */
    /* Container Tab */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background-color: #ffffff;
        padding: 10px;
        border-radius: 50px;
        box-shadow: 0 4px 10px rgba(0,0,0,0.05);
        margin-bottom: 20px;
        display: flex;
        justify-content: center;
    }

    /* Butang Tab (Belum Select) */
    .stTabs [data-baseweb="tab"] {
        background-color: transparent;
        border: none;
        color: #666;
        font-weight: 600;
        font-size: 14px;
        padding: 8px 20px;
        border-radius: 30px;
        transition: all 0.3s ease;
    }

    /* Butang Tab (Bila Hover) */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #f0f0f0;
        color: #333;
    }

    /* Butang Tab (SELECTED - AKTIF) */
    .stTabs [aria-selected="true"] {
        background-color: var(--sage-primary) !important;
        color: white !important;
        box-shadow: 0 4px 10px rgba(79, 121, 66, 0.3);
    }

    /* REMOVE DEFAULT RED LINE */
    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }

    /* ANIMATIONS (CSS ONLY) */
    @keyframes pulse-glow {
        0% { transform: scale(1); filter: drop-shadow(0 0 0px rgba(197, 160, 89, 0)); }
        50% { transform: scale(1.1); filter: drop-shadow(0 0 10px rgba(197, 160, 89, 0.5)); }
        100% { transform: scale(1); filter: drop-shadow(0 0 0px rgba(197, 160, 89, 0)); }
    }
    
    .header-ring {
        font-size: 80px;
        display: inline-block;
        animation: pulse-glow 3s infinite ease-in-out;
        margin-bottom: 10px;
    }

    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }
    
    .sidebar-wallet {
        font-size: 60px;
        text-align: center;
        display: block;
        margin: 0 auto 20px auto;
        animation: bounce 2s infinite ease-in-out;
    }

    /* HEADER TEXT - FORCED CENTER */
    .header-container { text-align: center; margin-bottom: 20px; margin-top: -20px; }
    
    /* GLASS CARD */
    .glass-card {
        background: rgba(255, 255, 255, 0.8);
        backdrop-filter: blur(12px);
        -webkit-backdrop-filter: blur(12px);
        border: 1px solid rgba(255, 255, 255, 0.9);
        box-shadow: 0 10px 30px -5px rgba(0, 0, 0, 0.05);
        border-radius: 24px;
        padding: 25px;
        margin-bottom: 20px;
        text-align: center;
        transition: transform 0.3s ease;
    }
    .glass-card:hover { transform: translateY(-5px); box-shadow: 0 15px 35px -5px rgba(79, 121, 66, 0.15); }

    .metric-val { font-size: 36px; font-weight: 800; color: var(--sage-dark); letter-spacing: -1px; margin-top: 5px;}
    .metric-lbl { font-size: 12px; text-transform: uppercase; color: #888; letter-spacing: 1.5px; font-weight: 700; }

    /* GAMIFICATION STYLES */
    @keyframes shine {
        0% { background-position: -200% center; }
        100% { background-position: 200% center; }
    }
    
    @keyframes float {
        0%, 100% { transform: translateY(0px); }
        50% { transform: translateY(-10px); }
    }
    
    .milestone-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.85));
        border-radius: 20px;
        padding: 20px;
        margin-bottom: 15px;
        border: 2px solid #e0e0e0;
        transition: all 0.4s cubic-bezier(0.175, 0.885, 0.32, 1.275);
        position: relative;
        overflow: hidden;
    }
    
    .milestone-card.achieved {
        border: 2px solid;
        box-shadow: 0 8px 25px rgba(0,0,0,0.12);
        background: linear-gradient(135deg, rgba(255,255,255,0.98), rgba(240,255,240,0.95));
    }
    
    .milestone-card.achieved::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.6), transparent);
        animation: shine 3s infinite;
    }
    
    .milestone-card:hover {
        transform: translateY(-5px) scale(1.02);
        box-shadow: 0 12px 35px rgba(0,0,0,0.15);
    }
    
    .milestone-icon {
        font-size: 48px;
        display: inline-block;
        margin-bottom: 10px;
    }
    
    .milestone-card.achieved .milestone-icon {
        animation: float 2s ease-in-out infinite;
    }
    
    .badge {
        display: inline-block;
        padding: 6px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 1px;
        color: white;
        box-shadow: 0 4px 10px rgba(0,0,0,0.15);
    }
    
    .progress-ring {
        width: 80px;
        height: 80px;
        border-radius: 50%;
        border: 6px solid #e0e0e0;
        display: flex;
        align-items: center;
        justify-content: center;
        font-weight: 800;
        font-size: 16px;
        position: relative;
        background: white;
    }
    
    .leaderboard-card {
        background: linear-gradient(135deg, rgba(255,255,255,0.95), rgba(255,255,255,0.85));
        border-radius: 20px;
        padding: 25px;
        margin-bottom: 15px;
        border: 2px solid #e0e0e0;
        display: flex;
        justify-content: space-between;
        align-items: center;
        transition: all 0.3s ease;
        position: relative;
        overflow: hidden;
    }
    
    .leaderboard-card.rank-1 {
        background: linear-gradient(135deg, #FFF9E6, #FFFBF0);
        border: 3px solid #FFD700;
        box-shadow: 0 8px 25px rgba(255, 215, 0, 0.3);
    }
    
    .leaderboard-card.rank-1::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,215,0,0.3), transparent);
        animation: shine 3s infinite;
    }
    
    .leaderboard-card:hover {
        transform: translateX(5px);
        box-shadow: 0 8px 20px rgba(0,0,0,0.1);
    }
    
    .rank-badge {
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 28px;
        font-weight: 800;
        background: linear-gradient(135deg, #f0f0f0, #e0e0e0);
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }
    
    .rank-badge.rank-1 {
        background: linear-gradient(135deg, #FFD700, #FFA500);
        color: white;
        animation: pulse-glow 2s infinite;
    }

    /* TIMELINE FEED */
    .timeline-item { display: flex; gap: 15px; margin-bottom: 20px; align-items: flex-start; animation: fadeIn 0.5s ease-in; }
    .timeline-icon { min-width: 45px; height: 45px; border-radius: 50%; background: white; display: flex; align-items: center; justify-content: center; font-size: 20px; border: 2px solid var(--sage-light); box-shadow: 0 4px 10px rgba(0,0,0,0.05); z-index: 2; }
    .timeline-content { background: rgba(255, 255, 255, 0.85); border-radius: 15px; padding: 15px 20px; width: 100%; border: 1px solid rgba(255,255,255,0.8); box-shadow: 0 4px 15px rgba(0,0,0,0.03); }
    .t-header { display: flex; justify-content: space-between; margin-bottom: 5px; }
    .t-name { font-weight: 700; color: var(--sage-dark); font-size: 1.05rem; }
    .t-amount { font-weight: 700; color: var(--gold); font-size: 1.1rem; }
    .t-date { font-size: 0.8rem; color: #888; display: block; margin-bottom: 8px; }
    .t-note { font-size: 0.95rem; color: #444; background: #f4f9f4; padding: 8px; border-radius: 8px; display: inline-block; }

    @keyframes fadeIn { from { opacity: 0; transform: translateY(10px); } to { opacity: 1; transform: translateY(0); } }

    /* UI BUTTONS */
    div.stButton > button { background-color: var(--sage-primary); color: white !important; border-radius: 15px; font-weight: 700; border: none; padding: 15px; width: 100%; transition: all 0.3s; box-shadow: 0 5px 15px rgba(79, 121, 66, 0.2); }
    div.stButton > button:hover { background-color: var(--sage-dark); transform: scale(1.02); box-shadow: 0 8px 20px rgba(79, 121, 66, 0.3); }
    </style>
    """, unsafe_allow_html=True)

# =============================================
# 🔌 DATABASE & LOGIC
# =============================================
def get_gspread_client():
    scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
   
    creds_dict = dict(st.secrets["gcp_service_account"])
    creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
    return gspread.authorize(creds)

@st.cache_resource
def connect_to_sheet():
    client = get_gspread_client()
    return client.open(SHEET_NAME).sheet1

def record_login(username):
    try:
        client = get_gspread_client()
        client.open(SHEET_NAME).worksheet("Logs").append_row([get_mys_time().strftime("%Y-%m-%d %H:%M:%S"), username])
    except: pass 

def predict_completion(df, target):
    if df.empty or len(df) < 2: return "Insufficient Data"
    df['Tarikh'] = pd.to_datetime(df['Tarikh'])
    days = max((df['Tarikh'].max() - df['Tarikh'].min()).days, 1)
    rate = df['Jumlah'].sum() / days
    if rate <= 0: return "Need Consistent Data"
    days_left = (target - df['Jumlah'].sum()) / rate
    return (get_mys_date() + timedelta(days=int(days_left))).strftime('%d %B %Y')

# =============================================
# 🚀 MAIN APP
# =============================================
def main():
    if 'logged_in' not in st.session_state: st.session_state.logged_in = False
    if 'current_user' not in st.session_state: st.session_state.current_user = ""

    # --- LOGIN SCREEN ---
    if not st.session_state.logged_in:
        st.markdown("<br><br><br>", unsafe_allow_html=True)
        col1, col2, col3 = st.columns([1,2,1])
        with col2:
            st.markdown("<h2 style='text-align:center; color:#4F7942;'>SECURE ACCESS</h2>", unsafe_allow_html=True)
            password = st.text_input("Enter Passkey", type="password")
            if st.button("Access Dashboard"):
                if password in USERS_DB:
                    user = USERS_DB[password]
                    st.session_state.logged_in = True
                    st.session_state.current_user = user
                    record_login(user)
                    st.toast(f"Welcome back, {user}", icon="🔒")
                    time.sleep(0.5)
                    st.rerun()
                else: st.error("Invalid Passkey.")
        return

    # --- DASHBOARD LOAD ---
    local_css()
    try:
        sheet = connect_to_sheet()
        df = pd.DataFrame(sheet.get_all_records())
    except:
        st.error("⚠️ Database Connection Error. Check credentials.")
        return

    # =============================================
    # 📝 SIDEBAR (ANIMATED CSS)
    # =============================================
    with st.sidebar:
        st.markdown("<div class='sidebar-wallet'>💰</div>", unsafe_allow_html=True)
        
        st.markdown(f"### 👋 Hello, **{st.session_state.current_user}**") 
        st.markdown("---")
        
        with st.form("entry_form"):
            st.markdown("#### ➕ New Deposit")
            st.text_input("Contributor", value=st.session_state.current_user, disabled=True)
            amount_input = st.number_input("Amount (RM)", min_value=0.0, step=10.0)
            category = st.selectbox("Source", ["Salary", "Bonus", "Side Income", "Gift", "Others"])
            note = st.text_input("Reference Note")
            
            if st.form_submit_button("Submit Record 💾"):
                if amount_input < 1.0:
                    st.error("⚠️ Minimum amount is RM 1.00")
                else:
                    name = st.session_state.current_user
                    sheet.append_row([get_mys_time().strftime('%Y-%m-%d %H:%M:%S'), name, amount_input, category, note])
                    df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce').fillna(0)
                    total_now = df['Jumlah'].sum() + amount_input
                    send_telegram_alert(name, amount_input, total_now)
                    st.success("Record Saved!")
                    st.cache_data.clear()
                    time.sleep(1)
                    st.rerun()
        
        st.markdown("---")
        if st.button("Logout"):
            st.session_state.logged_in = False
            st.rerun()

    # =============================================
    # 💍 HEADER SECTION
    # =============================================
    
    st.markdown("""
    <div style='text-align: center;'>
        <div class='header-ring'>💍</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div style='text-align: center; width: 100%; margin-top: -10px; margin-bottom: 20px;'>
        <p style='font-family: "Playfair Display", serif; color: #888; font-size: 1.1rem; letter-spacing: 2px; margin-bottom: 5px;'>بِسْمِ اللَّهِ الرَّحْمَنِ الرَّحِيم</p>
        <div style='font-family: "Playfair Display", serif; font-weight: 700; font-size: 3.5rem; color: #2E5834; text-shadow: 0 4px 10px rgba(0,0,0,0.05);'>
            {USER1_NAME} <span style='color: #C5A059; font-style: italic;'>&</span> {USER2_NAME}
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.warning("No data found. Please add a transaction.")
        return

    # Data Processing
    if 'Jumlah' in df.columns:
        df['Jumlah'] = df['Jumlah'].astype(str).str.replace(r'[^\d.-]', '', regex=True)
        df['Jumlah'] = pd.to_numeric(df['Jumlah'], errors='coerce').fillna(0)
    
    total = df['Jumlah'].sum()
    progress = min(total / TARGET_AMOUNT, 1.0)
    days_left = (WEDDING_DATE - get_mys_date()).days

    # --- HERO PROGRESS ---
    pct = progress * 100
    
    st.markdown(f"""
<div class='glass-card' style='border-top: 5px solid #4F7942;'>
<div class='metric-lbl' style='font-size:14px; margin-bottom:15px;'>⏳ {days_left} DAYS UNTIL THE BIG DAY</div>
<div style='position: relative; background: #e0e0e0; border-radius: 30px; height: 35px; width: 100%; margin-bottom: 10px; overflow: hidden;'>
<div style='background: linear-gradient(90deg, #8FBC8F, #4F7942); width: {pct}%; height: 100%; border-radius: 30px;'></div>
<div style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;'>
<span style='color: #1a1a1a; font-weight: 700; font-size: 13px; text-shadow: 0px 0px 2px rgba(255,255,255,0.8); white-space: nowrap;'>{pct:.1f}% FUNDED</span>
</div>
</div>
<div style='color:#666; font-size:0.9rem;'>Goal: <b>RM {TARGET_AMOUNT:,.0f}</b></div>
</div>
""", unsafe_allow_html=True)

    # --- TABS (CUSTOM STYLED) ---
    tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs(["Overview", "Health", "Analytics", "Leaders", "Predictor", "History"])

    with tab1:
        c1, c2, c3 = st.columns(3)
        c1.markdown(f"<div class='glass-card'><div class='metric-lbl'>Accumulated</div><div class='metric-val'>RM {total:,.2f}</div></div>", unsafe_allow_html=True)
        c2.markdown(f"<div class='glass-card'><div class='metric-lbl'>Goal Target</div><div class='metric-val'>RM {TARGET_AMOUNT:,.0f}</div></div>", unsafe_allow_html=True)
        c3.markdown(f"<div class='glass-card'><div class='metric-lbl'>Remaining</div><div class='metric-val' style='color:#C62828'>RM {TARGET_AMOUNT - total:,.2f}</div></div>", unsafe_allow_html=True)
        st.info(f"🤖 **AI Insight:** Based on current trends, you are projected to reach the goal by **{predict_completion(df, TARGET_AMOUNT)}**.")

    with tab2:
        df['Tarikh'] = pd.to_datetime(df['Tarikh'])
        start_date = df['Tarikh'].min().date()
        total_days = max((WEDDING_DATE - start_date).days, 1)
        exp_prog = min(max((get_mys_date() - start_date).days / total_days, 0.0), 1.0)
        status_color = "#43a047" if progress >= exp_prog else "#e53935"
        status_text = "ON TRACK" if progress >= exp_prog else "BEHIND SCHEDULE"
        
        st.markdown(f"<div class='glass-card' style='background: linear-gradient(135deg, {status_color}20, #ffffff); border-color:{status_color};'><h2 style='color:{status_color}; margin:0;'>{status_text}</h2><p style='color:#666;'>Your savings pace vs timeline</p></div>", unsafe_allow_html=True)
        col1, col2 = st.columns(2)
        col1.markdown(f"<div class='glass-card'><h5>💰 Actual Progress</h5><h2 style='color:#4F7942'>{progress*100:.1f}%</h2></div>", unsafe_allow_html=True)
        col2.markdown(f"<div class='glass-card'><h5>⏳ Timeline Elapsed</h5><h2 style='color:#555'>{exp_prog*100:.1f}%</h2></div>", unsafe_allow_html=True)

    with tab3:
        col1, col2 = st.columns(2)
        with col1:
            pie_data = df.groupby('Nama')['Jumlah'].sum().reset_index()
            fig = px.pie(pie_data, values='Jumlah', names='Nama', hole=0.7, color='Nama', color_discrete_map={COUPLE_NAMES[0]: '#4F7942', COUPLE_NAMES[1]: '#8FBC8F'})
            st.subheader("Contribution Ratio"); st.plotly_chart(fig, use_container_width=True)
        with col2:
            df_s = df.sort_values('Tarikh'); df_s['Cumulative'] = df_s.groupby('Nama')['Jumlah'].cumsum()
            fig = px.line(df_s, x='Tarikh', y='Cumulative', color='Nama', markers=True, color_discrete_map={COUPLE_NAMES[0]: '#4F7942', COUPLE_NAMES[1]: '#8FBC8F'})
            st.subheader("Growth Trajectory"); st.plotly_chart(fig, use_container_width=True)

    with tab4:
        # =============================================
        # 🎮 GAMIFICATION TAB - PROFESSIONAL DESIGN
        # =============================================
        
        st.markdown("### 🏆 Leaderboard & Achievements")
        
        # Calculate individual totals
        rank = df.groupby('Nama')['Jumlah'].sum().sort_values(ascending=False)
        
        # Display leaderboard
        col1, col2 = st.columns([2, 1])
        
        with col1:
            st.markdown("#### 👥 Top Contributors")
            for idx, (name, amount) in enumerate(rank.items(), 1):
                rank_class = "rank-1" if idx == 1 else ""
                rank_emoji = "👑" if idx == 1 else f"#{idx}"
                
                # Get current milestone for this person
                current_milestone = get_current_milestone(amount)
                badge_info = current_milestone if current_milestone else {"badge": "Beginner", "color": "#90EE90"}
                
                st.markdown(f"""
                <div class='leaderboard-card {rank_class}'>
                    <div style='display: flex; align-items: center; gap: 20px;'>
                        <div class='rank-badge {rank_class}'>{rank_emoji}</div>
                        <div>
                            <div style='font-weight: 700; font-size: 22px; color: #333; margin-bottom: 5px;'>{name}</div>
                            <span class='badge' style='background: {badge_info["color"]};'>{badge_info["badge"]}</span>
                        </div>
                    </div>
                    <div style='text-align: right;'>
                        <div style='font-weight: 800; font-size: 28px; color: #4F7942;'>RM {amount:,.2f}</div>
                        <div style='font-size: 13px; color: #888;'>{(amount/total*100):.1f}% of total</div>
                    </div>
                </div>
                """, unsafe_allow_html=True)
        
        with col2:
            st.markdown("#### 🎯 Current Status")
            current_m = get_current_milestone(total)
            next_m = get_next_milestone(total)
            
            if current_m:
                st.markdown(f"""
                <div class='glass-card' style='background: linear-gradient(135deg, {current_m["color"]}30, #ffffff);'>
                    <div style='font-size: 60px; margin-bottom: 10px;'>{current_m["icon"]}</div>
                    <div style='font-weight: 700; font-size: 20px; color: #333;'>{current_m["title"]}</div>
                    <span class='badge' style='background: {current_m["color"]};'>{current_m["badge"]}</span>
                    <div style='margin-top: 15px; font-size: 24px; font-weight: 800; color: #4F7942;'>RM {total:,.2f}</div>
                </div>
                """, unsafe_allow_html=True)
            
            if next_m:
                progress_to_next = calculate_milestone_progress(total)
                remaining = next_m["amount"] - total
                
                st.markdown(f"""
                <div class='glass-card' style='margin-top: 15px;'>
                    <div style='font-size: 14px; color: #888; text-transform: uppercase; letter-spacing: 1px; margin-bottom: 10px;'>Next Milestone</div>
                    <div style='font-size: 40px; margin-bottom: 10px;'>{next_m["icon"]}</div>
                    <div style='font-weight: 700; font-size: 18px; color: #333; margin-bottom: 5px;'>{next_m["title"]}</div>
                    <div style='font-size: 20px; font-weight: 800; color: #C5A059; margin-bottom: 15px;'>RM {next_m["amount"]:,}</div>
                    <div style='position: relative; background: #e0e0e0; border-radius: 20px; height: 25px; width: 100%; margin-bottom: 10px; overflow: hidden;'>
                        <div style='background: linear-gradient(90deg, #8FBC8F, #4F7942); width: {progress_to_next}%; height: 100%; border-radius: 20px;'></div>
                        <div style='position: absolute; top: 0; left: 0; width: 100%; height: 100%; display: flex; align-items: center; justify-content: center;'>
                            <span style='color: #1a1a1a; font-weight: 700; font-size: 12px;'>{progress_to_next:.1f}%</span>
                        </div>
                    </div>
                    <div style='font-size: 13px; color: #666;'>RM {remaining:,.2f} to go!</div>
                </div>
                """, unsafe_allow_html=True)
        
        st.markdown("---")
        st.markdown("### 🎖️ Milestone Journey")
        
        # Display all milestones
        cols = st.columns(3)
        for idx, milestone in enumerate(MILESTONES):
            col = cols[idx % 3]
            
            is_achieved = total >= milestone["amount"]
            card_class = "achieved" if is_achieved else ""
            opacity = "1.0" if is_achieved else "0.5"
            
            with col:
                st.markdown(f"""
                <div class='milestone-card {card_class}' style='opacity: {opacity}; border-color: {milestone["color"] if is_achieved else "#e0e0e0"};'>
                    <div class='milestone-icon'>{milestone["icon"]}</div>
                    <div style='font-weight: 700; font-size: 18px; color: #333; margin-bottom: 8px;'>{milestone["title"]}</div>
                    <span class='badge' style='background: {milestone["color"]};'>{milestone["badge"]}</span>
                    <div style='margin-top: 12px; font-size: 20px; font-weight: 800; color: #4F7942;'>RM {milestone["amount"]:,}</div>
                    <div style='margin-top: 10px; font-size: 24px;'>{"✅" if is_achieved else "🔒"}</div>
                </div>
                """, unsafe_allow_html=True)

    with tab5:
        st.markdown("### 🔮 Future Simulator")
        needed = TARGET_AMOUNT - total
        if needed <= 0: st.success("Target Achieved!")
        else:
            monthly = st.slider("Projected Monthly Saving (Joint)", 500, 5000, 1500, 100)
            months = needed / monthly
            future = get_mys_date() + timedelta(days=int(months * 30))
            st.markdown(f"<div class='glass-card'><h5 style='color:#666'>Estimated Completion Date</h5><h1 style='color:#C5A059; margin:10px 0;'>{future.strftime('%d %B %Y')}</h1><p>({int(months)} months from now)</p></div>", unsafe_allow_html=True)

    with tab6:
        st.markdown("### 📜 Recent Transactions (Last 10)")
        icons = {"Salary": "💼", "Bonus": "🎉", "Side Income": "🚀", "Gift": "🎁", "Others": "🔹"}
        df_hist = df.sort_index(ascending=False).head(10)
        
        for i, row in df_hist.iterrows():
            st.markdown(f"""
            <div class='timeline-item'>
                <div class='timeline-icon'>{icons.get(row['Kategori'], '🔹')}</div>
                <div class='timeline-content'>
                    <div class='t-header'>
                        <span class='t-name'>{row['Nama']}</span>
                        <span class='t-amount'>+ RM {row['Jumlah']:,.2f}</span>
                    </div>
                    <span class='t-date'>{pd.to_datetime(row['Tarikh']).strftime('%d %b %Y, %I:%M %p')} • {row['Kategori']}</span>
                    <div class='t-note'>📝 {row.iloc[4] if len(row) > 4 else '-'}</div>
                </div>
            </div>
            """, unsafe_allow_html=True)
        st.caption("Showing the latest 10 transactions only.")

if __name__ == "__main__":
    main()
