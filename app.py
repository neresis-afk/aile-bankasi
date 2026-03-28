import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
import urllib.request
import json
import os

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Aile Sanal Bankası",
    page_icon="🏦",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Nunito:wght@400;600;700;800;900&family=Baloo+2:wght@400;600;700;800&display=swap');

html, body, [class*="css"] { font-family: 'Nunito', sans-serif; }
.stApp {
    background: linear-gradient(135deg, #0d1b2a 0%, #1b2d45 50%, #0f3460 100%);
    min-height: 100vh;
}
#MainMenu, footer, header { visibility: hidden; }

/* ── Compact layout for mobile ── */
.block-container {
    padding: 0.4rem 0.7rem 1rem 0.7rem !important;
    max-width: 860px; margin: auto;
}

/* ── Minimal inline header ── */
.bank-header {
    display: flex; align-items: center; gap: 0.5rem;
    padding: 0.5rem 0 0.6rem; margin-bottom: 0.3rem;
}
.bank-header h1 {
    font-family: 'Baloo 2', cursive; font-size: 1.35rem; font-weight: 800;
    color: #fff; margin: 0; letter-spacing: -0.5px; line-height: 1;
}
.bank-header .sub { color: #6a8aaa; font-size: 0.72rem; display: block; margin-top: 1px; }
.bank-emoji { font-size: 1.6rem; flex-shrink: 0; }

/* ── Tabs ── */
div[data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.07) !important;
    border-radius: 14px !important; padding: 4px !important;
    gap: 4px !important; border: none !important;
}
/* unselected — clearly visible */
div[data-baseweb="tab"] {
    background: rgba(255,255,255,0.14) !important;
    border-radius: 10px !important; color: #c8d8ea !important;
    font-weight: 700 !important; font-size: 0.95rem !important;
    padding: 0.45rem 1rem !important; border: none !important;
}
/* selected — blue */
div[aria-selected="true"][data-baseweb="tab"] {
    background: linear-gradient(135deg, #1a6fd4, #2196f3) !important;
    color: #fff !important;
}

/* ── Balance card — blue ── */
.balance-card {
    background: linear-gradient(135deg, #1565c0 0%, #1e88e5 100%);
    border-radius: 18px; padding: 1rem 1.2rem; color: white;
    margin-bottom: 0.7rem; box-shadow: 0 6px 24px rgba(21,101,192,0.4);
    position: relative; overflow: hidden;
    display: flex; align-items: center; justify-content: space-between;
}
.balance-card::before {
    content: ''; position: absolute; top: -30px; right: -30px;
    width: 110px; height: 110px; background: rgba(255,255,255,0.07); border-radius: 50%;
}
.balance-label {
    font-size: 0.7rem; font-weight: 700; opacity: 0.8;
    text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.1rem;
}
.balance-amount {
    font-family: 'Baloo 2', cursive; font-size: 2.4rem; font-weight: 800; line-height: 1;
}
.balance-name { font-size: 0.85rem; font-weight: 700; opacity: 0.85; margin-top: 0.2rem; }
.balance-emoji { font-size: 2.4rem; opacity: 0.5; }

/* ── Stat pills ── */
.stat-row { display: flex; gap: 0.5rem; margin-bottom: 0.7rem; }
.stat-pill {
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 12px; padding: 0.5rem 0.8rem; flex: 1; text-align: center;
}
.stat-pill .s-label {
    font-size: 0.65rem; color: #7a9ab8; font-weight: 700;
    text-transform: uppercase; letter-spacing: 0.8px;
}
.stat-pill .s-value {
    font-family: 'Baloo 2', cursive; font-size: 1.15rem; font-weight: 700;
    color: #fff; margin-top: 0.05rem;
}
.stat-pill .s-value.green { color: #4ade80; }
.stat-pill .s-value.red   { color: #f87171; }

/* ── Form card ── */
.form-card {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.09);
    border-radius: 16px; padding: 0.9rem 1rem 0.3rem; margin-bottom: 0.7rem;
}

/* ── Inputs ── */
.stTextInput input, .stNumberInput input, .stTextArea textarea {
    background: rgba(255,255,255,0.08) !important;
    border: 1.5px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important; color: #fff !important;
    font-family: 'Nunito', sans-serif !important; font-size: 0.95rem !important;
}
.stTextInput input:focus, .stNumberInput input:focus {
    border-color: #2196f3 !important;
    box-shadow: 0 0 0 2px rgba(33,150,243,0.25) !important;
}
.stSelectbox div[data-baseweb="select"] > div {
    background: rgba(255,255,255,0.08) !important;
    border: 1.5px solid rgba(255,255,255,0.15) !important;
    border-radius: 10px !important; color: #fff !important;
}
label, .stSelectbox label, .stTextInput label,
.stNumberInput label, .stTextArea label {
    color: #7a9ab8 !important; font-weight: 700 !important;
    font-size: 0.75rem !important; text-transform: uppercase; letter-spacing: 0.8px;
}

/* ── Reduce Streamlit default vertical gaps ── */
div[data-testid="stVerticalBlock"] > div { gap: 0.4rem !important; }
.stRadio { margin-bottom: 0 !important; }
[data-testid="stHorizontalBlock"] { gap: 0.5rem !important; }

/* ── Buttons — blue ── */
.stButton > button {
    background: linear-gradient(135deg, #1565c0, #2196f3) !important;
    color: #fff !important; border: none !important; border-radius: 12px !important;
    font-family: 'Nunito', sans-serif !important; font-weight: 800 !important;
    font-size: 0.95rem !important; padding: 0.5rem 1.2rem !important; width: 100% !important;
    box-shadow: 0 3px 12px rgba(21,101,192,0.45) !important;
}
.stButton > button:hover { opacity: 0.88 !important; }

/* ── Dataframe ── */
[data-testid="stDataFrame"] > div {
    background: rgba(255,255,255,0.03) !important; border-radius: 14px !important;
    border: 1px solid rgba(255,255,255,0.07) !important; overflow: hidden;
}

/* ── Alerts ── */
.stSuccess { background: rgba(74,222,128,0.12)  !important; border-radius: 10px !important; border-left: 3px solid #4ade80 !important; color: #4ade80 !important; }
.stWarning { background: rgba(250,204,21,0.12)  !important; border-radius: 10px !important; border-left: 3px solid #facc15 !important; }
.stError   { background: rgba(248,113,113,0.12) !important; border-radius: 10px !important; border-left: 3px solid #f87171 !important; color: #f87171 !important; }
.stInfo    { background: rgba(33,150,243,0.12)  !important; border-radius: 10px !important; border-left: 3px solid #2196f3 !important; color: #90caf9 !important; }

/* ── Section titles ── */
.section-title {
    font-family: 'Baloo 2', cursive; font-size: 0.8rem; font-weight: 700;
    color: #6a8aaa; text-transform: uppercase; letter-spacing: 1.5px;
    margin: 0.7rem 0 0.3rem;
}
hr { border-color: rgba(255,255,255,0.07) !important; margin: 0.5rem 0 !important; }
.stRadio > label { color: #7a9ab8 !important; }
.stRadio div[role="radiogroup"] label { color: #c8d8ea !important; font-size: 0.9rem !important; }

/* ── Login / denied boxes ── */
.login-box {
    background: rgba(255,255,255,0.05); border: 1px solid rgba(255,255,255,0.12);
    border-radius: 20px; padding: 2rem 1.8rem; text-align: center;
    margin: 1.5rem auto; max-width: 420px;
}
.login-box h2 { font-family: 'Baloo 2', cursive; color: #fff; font-size: 1.5rem; margin-bottom: 0.3rem; }
.login-box p  { color: #7a9ab8; font-size: 0.9rem; line-height: 1.6; margin-bottom: 1rem; }
.login-icon   { font-size: 3rem; display: block; margin-bottom: 0.5rem; }
.auth-url {
    background: rgba(0,0,0,0.3); border-radius: 8px; padding: 0.6rem 0.8rem;
    word-break: break-all; font-size: 0.72rem; color: #64a0ff;
    margin: 0.8rem 0; text-align: left;
}
.denied-box {
    background: rgba(248,113,113,0.08); border: 1px solid rgba(248,113,113,0.25);
    border-radius: 20px; padding: 2rem 1.8rem; text-align: center;
    margin: 1.5rem auto; max-width: 420px;
}
.denied-box h2 { font-family: 'Baloo 2', cursive; color: #f87171; font-size: 1.5rem; margin-bottom: 0.3rem; }
.denied-box p  { color: #7a9ab8; font-size: 0.9rem; line-height: 1.6; }

/* ── User badge ── */
.user-badge {
    display: inline-flex; align-items: center; gap: 6px;
    background: rgba(33,150,243,0.12); border: 1px solid rgba(33,150,243,0.25);
    border-radius: 20px; padding: 0.25rem 0.9rem;
    font-size: 0.8rem; color: #90caf9;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
# Two separate scope sets:
#   SHEETS_SCOPES → app's own token, reads/writes Google Sheets
#   LOGIN_SCOPES  → visitor's personal token, only reads their email
SHEETS_SCOPES = ["https://www.googleapis.com/auth/spreadsheets"]
LOGIN_SCOPES  = ["https://www.googleapis.com/auth/userinfo.email", "openid"]

TOKEN_FILE        = "token.json"   # visitor login token (local dev only)
MONTHLY_ALLOWANCE = 20.0
CHILDREN = {
    "Çocuk 1": {"emoji": "🌟", "sheet": "Cocuk1"},
    "Çocuk 2": {"emoji": "🚀", "sheet": "Cocuk2"},
}
CATEGORIES = [
    "Harçlık", "Oyuncak", "Kitap", "Kırtasiye", "Oyun",
    "Yiyecek & İçecek", "Kıyafet", "Ulaşım", "Diğer"
]
COLUMNS      = ["Tarih", "Tutar", "Açıklama", "Kategori"]
SESSION_KEYS = ["oauth_flow", "oauth_url", "visitor_email",
                "visitor_creds", "allowance_applied"]

# ── Environment helpers ───────────────────────────────────────────────────────
def is_cloud() -> bool:
    try:
        _ = st.secrets["spreadsheet_id"]
        return True
    except Exception:
        return False

def get_spreadsheet_id() -> str:
    try:
        return st.secrets["spreadsheet_id"]
    except Exception:
        pass
    if os.path.exists("spreadsheet_id.txt"):
        return open("spreadsheet_id.txt").read().strip()
    return ""

def get_allowed_emails() -> list[str]:
    try:
        return [e.strip().lower() for e in st.secrets["allowed_emails"]]
    except Exception:
        pass
    if os.path.exists("allowed_emails.txt"):
        return [l.strip().lower() for l in open("allowed_emails.txt") if l.strip()]
    return []

def do_logout():
    for k in SESSION_KEYS:
        st.session_state.pop(k, None)

# ── App-level Sheets credentials (dedicated, never exposed to visitors) ───────
def get_sheets_credentials() -> Credentials:
    """
    Cloud → [sheets_token] in secrets (Sheets scope only).
    Local → sheets_token.json.
    Completely separate from visitor login.
    """
    if is_cloud():
        creds = Credentials.from_authorized_user_info(
            dict(st.secrets["sheets_token"]), SHEETS_SCOPES
        )
    else:
        creds = Credentials.from_authorized_user_file(
            "sheets_token.json", SHEETS_SCOPES
        )
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds

# ── Visitor login helpers ─────────────────────────────────────────────────────
def get_user_email(creds: Credentials) -> str:
    req = urllib.request.Request(
        "https://www.googleapis.com/oauth2/v1/userinfo?alt=json",
        headers={"Authorization": f"Bearer {creds.token}"},
    )
    with urllib.request.urlopen(req) as resp:
        return json.loads(resp.read()).get("email", "").lower()

def start_login_flow() -> str:
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json", scopes=LOGIN_SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob",
    )
    auth_url, _ = flow.authorization_url(prompt="consent")
    st.session_state["oauth_flow"] = flow
    return auth_url

def finish_login_flow(code: str) -> Credentials | None:
    flow = st.session_state.get("oauth_flow")
    if not flow:
        return None
    try:
        flow.fetch_token(code=code)
        return flow.credentials
    except Exception as e:
        st.error(f"Giriş hatası: {e}")
        return None

# ── Compact header (always shown) ────────────────────────────────────────────
st.markdown("""
<div class="bank-header">
  <span class="bank-emoji">🏦</span>
  <div>
    <h1>Aile Sanal Bankası</h1>
    <span class="sub">Çocuklarınızın harçlıklarını yönetin</span>
  </div>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# VISITOR LOGIN GATE
# Each visitor must sign in with their own Google account every session.
# Credentials live only in session_state (memory) — never written to disk
# on the cloud, never shared between users.
# ══════════════════════════════════════════════════════════════════════════════
visitor_creds: Credentials | None = st.session_state.get("visitor_creds")

# Local dev convenience: reuse token.json between restarts
if not visitor_creds and not is_cloud() and os.path.exists(TOKEN_FILE):
    try:
        c = Credentials.from_authorized_user_file(TOKEN_FILE, LOGIN_SCOPES)
        if c.expired and c.refresh_token:
            c.refresh(Request())
        if c.valid:
            visitor_creds = c
            st.session_state["visitor_creds"] = c
    except Exception:
        pass

if not visitor_creds:
    if not os.path.exists("client_secret.json") and not is_cloud():
        st.error("❌ `client_secret.json` bulunamadı.")
        st.stop()

    if "oauth_url" not in st.session_state:
        st.session_state["oauth_url"] = start_login_flow()

    auth_url = st.session_state["oauth_url"]
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="login-box">
          <span class="login-icon">🔐</span>
          <h2>Google ile Giriş Yap</h2>
          <p>Bu uygulama yalnızca aile üyelerine özeldir.<br>
             Google hesabınızla kimliğinizi doğrulayın.</p>
          <div class="auth-url">{auth_url}</div>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("🌐 Google Giriş Sayfasını Aç", auth_url)
        code = st.text_input("Google'dan aldığınız kodu yapıştırın:", placeholder="4/0AX...")
        if st.button("✅ Kodu Onayla ve Giriş Yap"):
            if not code.strip():
                st.error("Lütfen kodu girin.")
            else:
                with st.spinner("Doğrulanıyor..."):
                    creds = finish_login_flow(code.strip())
                if creds:
                    st.session_state["visitor_creds"] = creds
                    if not is_cloud():
                        open(TOKEN_FILE, "w").write(creds.to_json())
                    st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# EMAIL WHITELIST CHECK
# ══════════════════════════════════════════════════════════════════════════════
if "visitor_email" not in st.session_state:
    try:
        st.session_state["visitor_email"] = get_user_email(visitor_creds)
    except Exception:
        st.session_state["visitor_email"] = ""

visitor_email  = st.session_state["visitor_email"]
allowed_emails = get_allowed_emails()

if allowed_emails and visitor_email not in allowed_emails:
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown(f"""
        <div class="denied-box">
          <span class="login-icon">🚫</span>
          <h2>Erişim Reddedildi</h2>
          <p><b>{visitor_email}</b> hesabının<br>erişim izni bulunmuyor.</p>
        </div>
        """, unsafe_allow_html=True)
        if st.button("🔄 Farklı Hesapla Giriş Yap"):
            do_logout()
            st.rerun()
    st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# GOOGLE SHEETS  (app's own dedicated token — separate from visitor login)
# ══════════════════════════════════════════════════════════════════════════════
@st.cache_resource
def get_sheets_gc():
    return gspread.authorize(get_sheets_credentials())

def get_worksheet(child_name: str):
    gc  = get_sheets_gc()
    sid = get_spreadsheet_id()
    if not sid:
        st.error("❌ Spreadsheet ID bulunamadı.")
        st.stop()
    ss  = gc.open_by_key(sid)
    tab = CHILDREN[child_name]["sheet"]
    try:
        ws = ss.worksheet(tab)
    except gspread.WorksheetNotFound:
        ws = ss.add_worksheet(title=tab, rows=1000, cols=4)
    if not ws.get_all_values() or ws.cell(1, 1).value != "Tarih":
        ws.clear()
        ws.append_row(COLUMNS)
    return ws

def load_ledger(child_name: str) -> pd.DataFrame:
    records = get_worksheet(child_name).get_all_records()
    if not records:
        return pd.DataFrame(columns=COLUMNS)
    df = pd.DataFrame(records)[COLUMNS]
    df["Tutar"] = pd.to_numeric(df["Tutar"], errors="coerce").fillna(0.0)
    return df

def add_transaction(child_name: str, amount: float, desc: str, cat: str):
    get_worksheet(child_name).append_row(
        [datetime.now().strftime("%Y-%m-%d %H:%M"), round(amount, 2), desc, cat]
    )

def get_balance(df: pd.DataFrame) -> float:
    return round(df["Tutar"].sum(), 2) if not df.empty else 0.0

# ── Monthly allowance ─────────────────────────────────────────────────────────
def maybe_apply_monthly_allowance():
    if st.session_state.get("allowance_applied"):
        return
    ym = datetime.now().strftime("%Y-%m")
    for child in CHILDREN:
        df = load_ledger(child)
        already = (
            not df.empty and
            (
                df["Tarih"].str.startswith(ym) &
                (df["Tutar"] == MONTHLY_ALLOWANCE) &
                df["Açıklama"].str.contains("Aylık Harçlık", na=False)
            ).any()
        )
        if not already:
            add_transaction(child, MONTHLY_ALLOWANCE, "Aylık Harçlık", "Harçlık")
    st.session_state["allowance_applied"] = True

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
maybe_apply_monthly_allowance()

# ── User badge + logout ───────────────────────────────────────────────────────
col_usr, col_out = st.columns([4, 1])
with col_usr:
    st.markdown(f'<div class="user-badge">✅ {visitor_email}</div>', unsafe_allow_html=True)
with col_out:
    if st.button("🚪 Çıkış"):
        do_logout()
        st.rerun()

# ── Tabs ──────────────────────────────────────────────────────────────────────
tabs = st.tabs([f"{CHILDREN[c]['emoji']}  {c}" for c in CHILDREN])

for tab, child_name in zip(tabs, CHILDREN):
    info = CHILDREN[child_name]
    with tab:
        with st.spinner("Yükleniyor..."):
            df = load_ledger(child_name)

        balance_str = f"{get_balance(df):,.2f} ₺"
        st.markdown(f"""
        <div class="balance-card">
          <div class="balance-left">
            <div class="balance-label">Güncel Bakiye</div>
            <div class="balance-amount">{balance_str}</div>
            <div class="balance-name">{info['emoji']} {child_name}</div>
          </div>
          <div class="balance-emoji">{info['emoji']}</div>
        </div>
        """, unsafe_allow_html=True)

        credits = df[df["Tutar"] > 0]["Tutar"].sum() if not df.empty else 0.0
        debits  = df[df["Tutar"] < 0]["Tutar"].sum() if not df.empty else 0.0
        st.markdown(f"""
        <div class="stat-row">
          <div class="stat-pill">
            <div class="s-label">Gelir</div>
            <div class="s-value green">+{credits:,.2f}₺</div>
          </div>
          <div class="stat-pill">
            <div class="s-label">Harcama</div>
            <div class="s-value red">{debits:,.2f}₺</div>
          </div>
          <div class="stat-pill">
            <div class="s-label">İşlem</div>
            <div class="s-value">{len(df)}</div>
          </div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">➕ Yeni İşlem</div>', unsafe_allow_html=True)
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        with c1:
            tx_type = st.radio(
                "İşlem Türü", ["💰 Gelir", "💸 Harcama"],
                horizontal=True, key=f"type_{child_name}"
            )
        with c2:
            amount_abs = st.number_input(
                "Tutar (₺)", min_value=0.01, max_value=10000.0,
                value=10.0, step=0.5, format="%.2f", key=f"amt_{child_name}"
            )
        description = st.text_input(
            "Açıklama", placeholder="Örn: Peluş oyuncak...", key=f"desc_{child_name}"
        )
        category = st.selectbox("Kategori", CATEGORIES, key=f"cat_{child_name}")
        if st.button("💾 İşlemi Kaydet", key=f"save_{child_name}"):
            if not description.strip():
                st.error("Lütfen bir açıklama girin.")
            else:
                final = amount_abs if "Gelir" in tx_type else -amount_abs
                with st.spinner("Kaydediliyor..."):
                    add_transaction(child_name, final, description.strip(), category)
                st.success(f"✅ {'+'if final>0 else ''}{final:.2f}₺ — {description}")
                st.rerun()
        st.markdown('</div>', unsafe_allow_html=True)

        st.markdown('<div class="section-title">⚙️ Aylık Harçlık</div>', unsafe_allow_html=True)
        ci, cb = st.columns([3, 1])
        with ci:
            st.info(f"Her ayın başında **{MONTHLY_ALLOWANCE:.0f} ₺** otomatik eklenir.")
        with cb:
            if st.button("🔄 Ekle", key=f"allowance_{child_name}"):
                ym = datetime.now().strftime("%Y-%m")
                df2 = load_ledger(child_name)
                already = (
                    not df2.empty and
                    (
                        df2["Tarih"].str.startswith(ym) &
                        (df2["Tutar"] == MONTHLY_ALLOWANCE) &
                        df2["Açıklama"].str.contains("Aylık Harçlık", na=False)
                    ).any()
                )
                if already:
                    st.warning("Bu ay zaten eklendi.")
                else:
                    with st.spinner("Ekleniyor..."):
                        add_transaction(child_name, MONTHLY_ALLOWANCE, "Aylık Harçlık", "Harçlık")
                    st.success(f"✅ {MONTHLY_ALLOWANCE:.0f}₺ eklendi!")
                    st.rerun()

        st.markdown('<div class="section-title">📋 İşlem Geçmişi</div>', unsafe_allow_html=True)
        df_fresh = load_ledger(child_name)
        if df_fresh.empty:
            st.info("Henüz işlem bulunmuyor.")
        else:
            disp = df_fresh.copy()
            disp["Tutar"] = disp["Tutar"].apply(
                lambda x: f"+{x:.2f} ₺" if x >= 0 else f"{x:.2f} ₺"
            )
            st.dataframe(
                disp, use_container_width=True, hide_index=True,
                column_config={
                    "Tarih":    st.column_config.TextColumn("📅 Tarih",    width="medium"),
                    "Tutar":    st.column_config.TextColumn("💰 Tutar",    width="small"),
                    "Açıklama": st.column_config.TextColumn("📝 Açıklama", width="large"),
                    "Kategori": st.column_config.TextColumn("🏷️ Kategori", width="medium"),
                }
            )

st.markdown("""
<div style="text-align:center;color:#2a4060;font-size:0.72rem;margin-top:1rem;padding-bottom:0.5rem;">
  🏦 Aile Sanal Bankası &nbsp;•&nbsp; Google Sheets ile senkronize
</div>
""", unsafe_allow_html=True)
