import streamlit as st
import pandas as pd
from datetime import datetime
import gspread
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
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
    background: linear-gradient(135deg, #1a1a2e 0%, #16213e 50%, #0f3460 100%);
    min-height: 100vh;
}
#MainMenu, footer, header { visibility: hidden; }
.block-container { padding: 1rem 1rem 2rem 1rem !important; max-width: 900px; margin: auto; }

.bank-header { text-align: center; padding: 2rem 1rem 1.5rem; margin-bottom: 1.5rem; }
.bank-header h1 {
    font-family: 'Baloo 2', cursive; font-size: 2.4rem; font-weight: 800;
    color: #fff; margin: 0; letter-spacing: -1px;
}
.bank-header p { color: #a0b4cc; font-size: 0.95rem; margin: 0.3rem 0 0; }
.bank-emoji { font-size: 2.8rem; display: block; margin-bottom: 0.4rem; }

div[data-baseweb="tab-list"] {
    background: rgba(255,255,255,0.05) !important; border-radius: 16px !important;
    padding: 6px !important; gap: 6px !important; border: none !important;
}
div[data-baseweb="tab"] {
    background: transparent !important; border-radius: 12px !important;
    color: #a0b4cc !important; font-weight: 700 !important;
    font-size: 1rem !important; padding: 0.6rem 1.2rem !important; border: none !important;
}
div[aria-selected="true"][data-baseweb="tab"] {
    background: linear-gradient(135deg, #e94560, #f5a623) !important; color: #fff !important;
}

.balance-card {
    background: linear-gradient(135deg, #e94560 0%, #f5a623 100%);
    border-radius: 24px; padding: 2rem 1.8rem; color: white;
    margin-bottom: 1.2rem; box-shadow: 0 8px 32px rgba(233,69,96,0.35);
    position: relative; overflow: hidden;
}
.balance-card::before {
    content: ''; position: absolute; top: -40px; right: -40px;
    width: 150px; height: 150px; background: rgba(255,255,255,0.08); border-radius: 50%;
}
.balance-label { font-size: 0.85rem; font-weight: 600; opacity: 0.85; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 0.3rem; }
.balance-amount { font-family: 'Baloo 2', cursive; font-size: 3.2rem; font-weight: 800; line-height: 1; margin-bottom: 0.5rem; }
.balance-name { font-size: 1.1rem; font-weight: 700; opacity: 0.9; }

.stat-row { display: flex; gap: 0.8rem; margin-bottom: 1.2rem; flex-wrap: wrap; }
.stat-pill {
    background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.12);
    border-radius: 14px; padding: 0.8rem 1.2rem; flex: 1; min-width: 120px; text-align: center;
}
.stat-pill .s-label { font-size: 0.72rem; color: #a0b4cc; font-weight: 700; text-transform: uppercase; letter-spacing: 1px; }
.stat-pill .s-value { font-family: 'Baloo 2', cursive; font-size: 1.4rem; font-weight: 700; color: #fff; margin-top: 0.1rem; }
.stat-pill .s-value.green { color: #4ade80; }
.stat-pill .s-value.red   { color: #f87171; }

.form-card {
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.1);
    border-radius: 20px; padding: 1.5rem 1.5rem 0.5rem; margin-bottom: 1.2rem;
}

.stTextInput input, .stNumberInput input, .stSelectbox select, .stTextArea textarea {
    background: rgba(255,255,255,0.08) !important; border: 1.5px solid rgba(255,255,255,0.18) !important;
    border-radius: 12px !important; color: #fff !important;
    font-family: 'Nunito', sans-serif !important; font-size: 1rem !important;
}
label, .stSelectbox label, .stTextInput label, .stNumberInput label, .stTextArea label {
    color: #a0b4cc !important; font-weight: 700 !important;
    font-size: 0.85rem !important; text-transform: uppercase; letter-spacing: 0.8px;
}
.stSelectbox div[data-baseweb="select"] > div {
    background: #1a2744 !important; border-radius: 12px !important; color: #fff !important;
}
.stButton > button {
    background: linear-gradient(135deg, #e94560, #f5a623) !important;
    color: #fff !important; border: none !important; border-radius: 14px !important;
    font-family: 'Nunito', sans-serif !important; font-weight: 800 !important;
    font-size: 1rem !important; padding: 0.65rem 1.8rem !important; width: 100% !important;
    box-shadow: 0 4px 18px rgba(233,69,96,0.4) !important;
}
[data-testid="stDataFrame"] > div {
    background: rgba(255,255,255,0.04) !important; border-radius: 16px !important;
    border: 1px solid rgba(255,255,255,0.08) !important; overflow: hidden;
}
.stSuccess { background: rgba(74,222,128,0.15)  !important; border-radius: 12px !important; border-left: 4px solid #4ade80 !important; color: #4ade80 !important; }
.stWarning { background: rgba(245,166,35,0.15)  !important; border-radius: 12px !important; border-left: 4px solid #f5a623 !important; }
.stError   { background: rgba(233,69,96,0.15)   !important; border-radius: 12px !important; border-left: 4px solid #e94560 !important; color: #f87171 !important; }
.stInfo    { background: rgba(100,160,255,0.12) !important; border-radius: 12px !important; border-left: 4px solid #64a0ff !important; color: #a0c4ff !important; }
.section-title {
    font-family: 'Baloo 2', cursive; font-size: 1.05rem; font-weight: 700;
    color: #a0b4cc; text-transform: uppercase; letter-spacing: 1.5px; margin: 1.4rem 0 0.6rem;
}
hr { border-color: rgba(255,255,255,0.08) !important; }
.stRadio > label { color: #a0b4cc !important; }
.stRadio div[role="radiogroup"] label { color: #d0dce8 !important; }
.auth-box {
    background: rgba(255,255,255,0.06); border: 1px solid rgba(255,255,255,0.15);
    border-radius: 20px; padding: 2rem; text-align: center; margin: 2rem auto; max-width: 500px;
}
.auth-box h2 { font-family: 'Baloo 2', cursive; color: #fff; font-size: 1.4rem; margin-bottom: 0.5rem; }
.auth-box p  { color: #a0b4cc; font-size: 0.95rem; line-height: 1.6; }
.auth-url {
    background: rgba(0,0,0,0.3); border-radius: 10px; padding: 0.8rem 1rem;
    word-break: break-all; font-size: 0.78rem; color: #64a0ff; margin: 1rem 0; text-align: left;
}
</style>
""", unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
SCOPES            = ["https://www.googleapis.com/auth/spreadsheets"]
TOKEN_FILE        = "token.json"          # used only in local mode
MONTHLY_ALLOWANCE = 20.0
CHILDREN = {
    "Çocuk 1": {"emoji": "🌟", "sheet": "Cocuk1"},
    "Çocuk 2": {"emoji": "🚀", "sheet": "Cocuk2"},
}
CATEGORIES = [
    "Harçlık", "Oyuncak", "Kitap", "Kırtasiye", "Oyun",
    "Yiyecek & İçecek", "Kıyafet", "Ulaşım", "Diğer"
]
COLUMNS = ["Tarih", "Tutar", "Açıklama", "Kategori"]

# ── Detect environment ────────────────────────────────────────────────────────
def is_cloud() -> bool:
    """True when running on Streamlit Community Cloud (secrets are present)."""
    try:
        _ = st.secrets["spreadsheet_id"]
        return True
    except (KeyError, FileNotFoundError):
        return False

# ── Spreadsheet ID ────────────────────────────────────────────────────────────
def get_spreadsheet_id() -> str:
    try:
        return st.secrets["spreadsheet_id"]
    except Exception:
        pass
    if os.path.exists("spreadsheet_id.txt"):
        return open("spreadsheet_id.txt").read().strip()
    return os.environ.get("SPREADSHEET_ID", "")

# ══════════════════════════════════════════════════════════════════════════════
# AUTH — Cloud path (token stored in st.secrets)
# ══════════════════════════════════════════════════════════════════════════════
def get_cloud_credentials() -> Credentials:
    """
    On Streamlit Cloud we store the OAuth token JSON inside secrets
    under the key  [oauth_token]  as a TOML table.
    """
    token_dict = dict(st.secrets["oauth_token"])
    creds = Credentials.from_authorized_user_info(token_dict, SCOPES)
    if creds.expired and creds.refresh_token:
        creds.refresh(Request())
    return creds

# ══════════════════════════════════════════════════════════════════════════════
# AUTH — Local path (token stored in token.json + OAuth flow)
# ══════════════════════════════════════════════════════════════════════════════
def load_local_credentials() -> Credentials | None:
    if not os.path.exists(TOKEN_FILE):
        return None
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    if creds and creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
            _save_token(creds)
        except Exception:
            return None
    return creds if (creds and creds.valid) else None

def _save_token(creds: Credentials):
    with open(TOKEN_FILE, "w") as f:
        f.write(creds.to_json())

def start_oauth_flow() -> str:
    flow = InstalledAppFlow.from_client_secrets_file(
        "client_secret.json",
        scopes=SCOPES,
        redirect_uri="urn:ietf:wg:oauth:2.0:oob",
    )
    auth_url, _ = flow.authorization_url(prompt="consent")
    st.session_state["oauth_flow"] = flow
    return auth_url

def finish_oauth_flow(code: str) -> Credentials | None:
    flow = st.session_state.get("oauth_flow")
    if not flow:
        return None
    try:
        flow.fetch_token(code=code)
        creds = flow.credentials
        _save_token(creds)
        # Print token so user can copy it into Streamlit Cloud secrets
        print("\n✅ TOKEN JSON (Streamlit Cloud secrets için kopyalayın):\n")
        print(creds.to_json())
        return creds
    except Exception as e:
        st.error(f"Kimlik doğrulama hatası: {e}")
        return None

# ── gspread client ────────────────────────────────────────────────────────────
@st.cache_resource
def get_gc_cloud():
    creds = get_cloud_credentials()
    return gspread.authorize(creds)

@st.cache_resource
def get_gc_local(token_sig: str):   # token_sig keeps cache fresh on re-auth
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)
    return gspread.authorize(creds)

def get_gc():
    if is_cloud():
        return get_gc_cloud()
    token_sig = open(TOKEN_FILE).read()[:40] if os.path.exists(TOKEN_FILE) else ""
    return get_gc_local(token_sig)

# ── Worksheet helper ──────────────────────────────────────────────────────────
def get_worksheet(child_name: str):
    gc  = get_gc()
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

# ── Data helpers ──────────────────────────────────────────────────────────────
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
# UI HEADER (always shown)
# ══════════════════════════════════════════════════════════════════════════════
st.markdown("""
<div class="bank-header">
  <span class="bank-emoji">🏦</span>
  <h1>Aile Sanal Bankası</h1>
  <p>Çocuklarınızın harçlıklarını kolayca yönetin</p>
</div>
""", unsafe_allow_html=True)

# ══════════════════════════════════════════════════════════════════════════════
# AUTH GATE — local only (cloud uses secrets, no interactive login needed)
# ══════════════════════════════════════════════════════════════════════════════
if not is_cloud():
    creds = load_local_credentials()
    if not creds:
        if "oauth_url" not in st.session_state:
            if not os.path.exists("client_secret.json"):
                st.error("❌ `client_secret.json` bulunamadı. Lütfen Google Cloud Console'dan indirin.")
                st.stop()
            st.session_state["oauth_url"] = start_oauth_flow()

        auth_url = st.session_state["oauth_url"]
        st.markdown(f"""
        <div class="auth-box">
          <h2>🔐 Google ile Giriş Yap</h2>
          <p>Aşağıdaki bağlantıyı tarayıcınızda açın, izin verin<br>
             ve size gösterilen <b>kodu</b> aşağıya yapıştırın.</p>
          <div class="auth-url">{auth_url}</div>
        </div>
        """, unsafe_allow_html=True)
        st.link_button("🌐 Google Yetkilendirme Sayfasını Aç", auth_url)

        code = st.text_input("Google'dan aldığınız kodu buraya yapıştırın:", placeholder="4/0AX...")
        if st.button("✅ Kodu Onayla ve Giriş Yap"):
            if not code.strip():
                st.error("Lütfen kodu girin.")
            else:
                with st.spinner("Doğrulanıyor..."):
                    creds = finish_oauth_flow(code.strip())
                if creds:
                    get_gc_local.clear()
                    st.success("✅ Giriş başarılı!")
                    st.info("💡 Termux loglarında token JSON'ı göreceksiniz — Streamlit Cloud kurulumu için saklayın.")
                    st.rerun()
        st.stop()

# ══════════════════════════════════════════════════════════════════════════════
# MAIN APP
# ══════════════════════════════════════════════════════════════════════════════
maybe_apply_monthly_allowance()

tabs = st.tabs([f"{CHILDREN[c]['emoji']}  {c}" for c in CHILDREN])

for tab, child_name in zip(tabs, CHILDREN):
    info = CHILDREN[child_name]
    with tab:
        with st.spinner("Veriler yükleniyor..."):
            df = load_ledger(child_name)

        balance_str = f"{get_balance(df):,.2f} ₺"
        st.markdown(f"""
        <div class="balance-card">
          <div class="balance-label">Güncel Bakiye</div>
          <div class="balance-amount">{balance_str}</div>
          <div class="balance-name">{info['emoji']} {child_name}</div>
        </div>
        """, unsafe_allow_html=True)

        credits  = df[df["Tutar"] > 0]["Tutar"].sum() if not df.empty else 0.0
        debits   = df[df["Tutar"] < 0]["Tutar"].sum() if not df.empty else 0.0
        st.markdown(f"""
        <div class="stat-row">
          <div class="stat-pill"><div class="s-label">Gelir</div><div class="s-value green">+{credits:,.2f}₺</div></div>
          <div class="stat-pill"><div class="s-label">Harcama</div><div class="s-value red">{debits:,.2f}₺</div></div>
          <div class="stat-pill"><div class="s-label">İşlem Sayısı</div><div class="s-value">{len(df)}</div></div>
        </div>
        """, unsafe_allow_html=True)

        st.markdown("<hr>", unsafe_allow_html=True)

        st.markdown('<div class="section-title">➕ Yeni İşlem Ekle</div>', unsafe_allow_html=True)
        st.markdown('<div class="form-card">', unsafe_allow_html=True)
        c1, c2 = st.columns([1, 1])
        with c1:
            tx_type = st.radio("İşlem Türü", ["💰 Gelir", "💸 Harcama"], horizontal=True, key=f"type_{child_name}")
        with c2:
            amount_abs = st.number_input("Tutar (₺)", min_value=0.01, max_value=10000.0, value=10.0, step=0.5, format="%.2f", key=f"amt_{child_name}")
        description = st.text_input("Açıklama", placeholder="Örn: Peluş oyuncak, Kitap...", key=f"desc_{child_name}")
        category    = st.selectbox("Kategori", CATEGORIES, key=f"cat_{child_name}")

        if st.button("İşlemi Kaydet", key=f"save_{child_name}"):
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
            if st.button("🔄 Şimdi Ekle", key=f"allowance_{child_name}"):
                ym = datetime.now().strftime("%Y-%m")
                df2 = load_ledger(child_name)
                already = (
                    not df2.empty and
                    (df2["Tarih"].str.startswith(ym) & (df2["Tutar"] == MONTHLY_ALLOWANCE) & df2["Açıklama"].str.contains("Aylık Harçlık", na=False)).any()
                )
                if already:
                    st.warning("Bu ay harçlık zaten eklendi.")
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
            disp["Tutar"] = disp["Tutar"].apply(lambda x: f"+{x:.2f} ₺" if x >= 0 else f"{x:.2f} ₺")
            st.dataframe(disp, use_container_width=True, hide_index=True,
                column_config={
                    "Tarih":    st.column_config.TextColumn("📅 Tarih",    width="medium"),
                    "Tutar":    st.column_config.TextColumn("💰 Tutar",    width="small"),
                    "Açıklama": st.column_config.TextColumn("📝 Açıklama", width="large"),
                    "Kategori": st.column_config.TextColumn("🏷️ Kategori", width="medium"),
                })

        if not is_cloud():
            with st.expander("⚙️ Hesap Ayarları"):
                if st.button("🔓 Oturumu Kapat", key=f"logout_{child_name}"):
                    if os.path.exists(TOKEN_FILE):
                        os.remove(TOKEN_FILE)
                    get_gc_local.clear()
                    for k in ["oauth_flow", "oauth_url", "allowance_applied"]:
                        st.session_state.pop(k, None)
                    st.rerun()

st.markdown("""
<div style="text-align:center;color:#4a6080;font-size:0.8rem;margin-top:3rem;padding-bottom:2rem;">
  🏦 Aile Sanal Bankası &nbsp;•&nbsp; Google Sheets ile senkronize
</div>
""", unsafe_allow_html=True)
