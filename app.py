import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from supabase import create_client, Client

# ============================================================
#                    הגדרות עמוד
# ============================================================
st.set_page_config(
    page_title="Shiptanbul Cloud",
    page_icon="📦",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ============================================================
#                    עיצוב CSS - Branding מלא
# ============================================================
st.markdown("""
    <style>
    /* ייבוא פונט עברי מקצועי */
    @import url('https://fonts.googleapis.com/css2?family=Heebo:wght@300;400;500;700;900&display=swap');

    /* משתני צבע - לפי הלוגו */
    :root {
        --brand-blue: #1BA3E8;
        --brand-blue-dark: #1487C2;
        --brand-yellow: #F2C94C;
        --brand-yellow-dark: #E0B43A;
        --brand-black: #1A1A1A;
        --brand-gray: #6B7280;
        --brand-light: #F8FAFC;
        --brand-border: #E5E7EB;
        --brand-success: #10B981;
        --brand-danger: #EF4444;
    }

    /* RTL גלובלי + פונט */
    html, body, [class*="css"], .main, .block-container {
        direction: rtl !important;
        text-align: right !important;
        font-family: 'Heebo', -apple-system, BlinkMacSystemFont, sans-serif !important;
    }

    /* רקע ראשי */
    .stApp {
        background: linear-gradient(135deg, #F8FAFC 0%, #EFF6FF 100%);
    }

    /* כותרות */
    h1, h2, h3, h4, h5, h6 {
        direction: rtl !important;
        text-align: right !important;
        color: var(--brand-black) !important;
        font-weight: 700 !important;
        letter-spacing: -0.02em;
    }

    h1 {
        font-size: 2.5rem !important;
        background: linear-gradient(135deg, var(--brand-blue) 0%, var(--brand-blue-dark) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        padding-bottom: 0.5rem;
    }

    /* פסקאות וטקסטים */
    p, label, div, span {
        direction: rtl;
        text-align: right;
    }

    /* כותרת ראשית - Header עם לוגו */
    .brand-header {
        background: linear-gradient(135deg, var(--brand-black) 0%, #2D2D2D 100%);
        padding: 1.5rem 2rem;
        border-radius: 16px;
        margin-bottom: 2rem;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.15);
        display: flex;
        align-items: center;
        justify-content: space-between;
        flex-direction: row-reverse;
    }

    .brand-title {
        color: white !important;
        margin: 0 !important;
        display: flex;
        align-items: center;
        gap: 1rem;
        background: none !important;
        -webkit-text-fill-color: white !important;
    }

    .brand-title .ship {
        color: var(--brand-blue) !important;
        -webkit-text-fill-color: var(--brand-blue) !important;
    }

    .brand-title .tanbul {
        color: white !important;
        -webkit-text-fill-color: white !important;
    }

    .brand-badge {
        background: var(--brand-yellow);
        color: var(--brand-black);
        padding: 0.4rem 1rem;
        border-radius: 30px;
        font-weight: 700;
        font-size: 0.85rem;
        box-shadow: 0 4px 10px rgba(242, 201, 76, 0.4);
    }

    .brand-badge-standalone {
        background: linear-gradient(135deg, var(--brand-yellow) 0%, var(--brand-yellow-dark) 100%);
        color: var(--brand-black);
        padding: 0.6rem 1.5rem;
        border-radius: 30px;
        font-weight: 700;
        font-size: 1rem;
        box-shadow: 0 6px 18px rgba(242, 201, 76, 0.4);
        display: inline-block;
    }

    /* כפתורים מעוצבים */
    div.stButton > button {
        width: 100%;
        background: linear-gradient(135deg, var(--brand-blue) 0%, var(--brand-blue-dark) 100%);
        color: white !important;
        border: none;
        border-radius: 10px;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        font-size: 0.95rem;
        transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1);
        box-shadow: 0 4px 12px rgba(27, 163, 232, 0.25);
        font-family: 'Heebo', sans-serif !important;
    }

    div.stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(27, 163, 232, 0.4);
        background: linear-gradient(135deg, var(--brand-blue-dark) 0%, var(--brand-blue) 100%);
    }

    div.stButton > button:active {
        transform: translateY(0);
    }

    /* כפתור form_submit */
    div.stFormSubmitButton > button {
        background: linear-gradient(135deg, var(--brand-yellow) 0%, var(--brand-yellow-dark) 100%) !important;
        color: var(--brand-black) !important;
        font-weight: 700 !important;
        box-shadow: 0 4px 12px rgba(242, 201, 76, 0.35) !important;
    }

    div.stFormSubmitButton > button:hover {
        box-shadow: 0 6px 20px rgba(242, 201, 76, 0.5) !important;
    }

    /* Tabs מעוצבים */
    .stTabs [data-baseweb="tab-list"] {
        direction: rtl;
        gap: 0.5rem;
        background: white;
        padding: 0.5rem;
        border-radius: 14px;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        border: 1px solid var(--brand-border);
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border-radius: 10px;
        padding: 0.6rem 1.5rem;
        font-weight: 600;
        font-size: 1rem;
        color: var(--brand-gray);
        transition: all 0.2s;
        border: none;
    }

    .stTabs [data-baseweb="tab"]:hover {
        background: var(--brand-light);
        color: var(--brand-black);
    }

    .stTabs [aria-selected="true"] {
        background: linear-gradient(135deg, var(--brand-blue) 0%, var(--brand-blue-dark) 100%) !important;
        color: white !important;
        box-shadow: 0 4px 12px rgba(27, 163, 232, 0.3);
    }

    .stTabs [data-baseweb="tab-highlight"] {
        display: none;
    }

    .stTabs [data-baseweb="tab-border"] {
        display: none;
    }

    /* Expander */
    .stExpander {
        text-align: right;
        border: 1px solid var(--brand-border) !important;
        border-radius: 12px !important;
        background: white !important;
        box-shadow: 0 2px 8px rgba(0,0,0,0.03) !important;
        overflow: hidden;
        margin-bottom: 0.75rem;
    }

    .stExpander summary {
        font-weight: 600 !important;
        padding: 1rem !important;
        font-size: 1rem !important;
        color: var(--brand-black) !important;
    }

    .stExpander summary:hover {
        background: var(--brand-light) !important;
    }

    /* טפסים ושדות קלט */
    [data-testid="stForm"] {
        direction: rtl;
        background: white;
        padding: 1.5rem;
        border-radius: 14px;
        border: 1px solid var(--brand-border);
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
    }

    .stTextInput input, .stTextArea textarea, .stSelectbox > div > div, .stDateInput input {
        text-align: right !important;
        direction: rtl !important;
        border-radius: 10px !important;
        border: 1.5px solid var(--brand-border) !important;
        font-family: 'Heebo', sans-serif !important;
        transition: all 0.2s;
    }

    .stTextInput input:focus, .stTextArea textarea:focus {
        border-color: var(--brand-blue) !important;
        box-shadow: 0 0 0 3px rgba(27, 163, 232, 0.15) !important;
    }

    .stTextInput label, .stTextArea label, .stSelectbox label, .stDateInput label {
        font-weight: 600 !important;
        color: var(--brand-black) !important;
        font-size: 0.9rem !important;
    }

    /* טבלה */
    .stTable {
        direction: rtl;
    }

    .stTable table {
        border-radius: 12px;
        overflow: hidden;
        box-shadow: 0 4px 12px rgba(0,0,0,0.06);
        border: none !important;
    }

    .stTable thead tr th {
        background: linear-gradient(135deg, var(--brand-black) 0%, #2D2D2D 100%) !important;
        color: white !important;
        font-weight: 700 !important;
        text-align: right !important;
        padding: 1rem !important;
        font-size: 0.95rem !important;
        border: none !important;
    }

    .stTable tbody tr td {
        text-align: right !important;
        padding: 0.9rem 1rem !important;
        background: white !important;
        border-bottom: 1px solid var(--brand-border) !important;
        font-size: 0.95rem !important;
    }

    .stTable tbody tr:hover td {
        background: var(--brand-light) !important;
    }

    /* הודעת אזהרה - הודעת הנהלה */
    .management-alert {
        background: linear-gradient(135deg, var(--brand-yellow) 0%, var(--brand-yellow-dark) 100%);
        color: var(--brand-black);
        padding: 1.2rem 1.5rem;
        border-radius: 14px;
        margin-bottom: 1.5rem;
        font-weight: 600;
        box-shadow: 0 6px 20px rgba(242, 201, 76, 0.35);
        border-right: 6px solid var(--brand-black);
        display: flex;
        align-items: center;
        gap: 0.75rem;
        font-size: 1rem;
    }

    .management-alert-icon {
        font-size: 1.5rem;
    }

    /* Success / Info / Warning / Error */
    .stAlert {
        border-radius: 12px !important;
        border: none !important;
        font-weight: 500;
    }

    div[data-baseweb="notification"] {
        direction: rtl !important;
        text-align: right !important;
    }

    /* Divider */
    hr {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, var(--brand-border), transparent);
        margin: 1.5rem 0;
    }

    /* כרטיסי פריטים (זיכויים / שאלות) */
    .item-card {
        background: white;
        border: 1px solid var(--brand-border);
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 0.75rem;
        box-shadow: 0 2px 8px rgba(0,0,0,0.04);
        transition: all 0.2s;
    }

    .item-card:hover {
        box-shadow: 0 4px 16px rgba(0,0,0,0.08);
        transform: translateY(-1px);
    }

    /* Status badges */
    .status-pending {
        display: inline-block;
        background: var(--brand-yellow);
        color: var(--brand-black);
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
    }

    .status-done {
        display: inline-block;
        background: var(--brand-success);
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: 700;
    }

    /* Checkbox */
    .stCheckbox {
        direction: rtl;
    }

    .stCheckbox label {
        direction: rtl !important;
        flex-direction: row-reverse !important;
        gap: 0.5rem;
    }

    /* טקסט מחוק */
    .stMarkdown del {
        color: #94A3B8;
        text-decoration: line-through;
    }

    /* הסתרת כפתור deploy ופוטר Streamlit */
    [data-testid="stToolbar"] { display: none; }
    footer { display: none; }
    #MainMenu { visibility: hidden; }

    /* responsive */
    @media (max-width: 768px) {
        .brand-header {
            padding: 1rem;
            flex-direction: column-reverse;
            gap: 1rem;
        }
        h1 { font-size: 1.8rem !important; }
    }
    </style>
""", unsafe_allow_html=True)

# ============================================================
#                    Header עם Branding - לוגו תמונה
# ============================================================
header_col1, header_col2 = st.columns([1, 4])
with header_col1:
    try:
        st.image("logo.png", width=200)
    except:
        st.markdown("### 📦 SHIPTANBUL")
with header_col2:
    st.markdown("""
        <div style="display: flex; align-items: center; height: 100%; padding-top: 1.5rem;">
            <div class="brand-badge-standalone">📦 מערכת ניהול פנימית</div>
        </div>
    """, unsafe_allow_html=True)

st.markdown("<hr style='margin-top: 0; margin-bottom: 2rem;'>", unsafe_allow_html=True)

# ============================================================
#                    רשימות קבועות
# ============================================================
MANAGERS = ["אורלי", "שמואל", "סיון"]
REPS = ["סיון", "אורלי", "דנה", "אלינה", "כסיף", "מעין", "שירה", "נעמי", "גדיר"]

# ============================================================
#                    פונקציות עזר
# ============================================================
def send_notification(message):
    try:
        if "TELEGRAM_TOKEN" in st.secrets and "TELEGRAM_CHAT_ID" in st.secrets:
            token = st.secrets["TELEGRAM_TOKEN"]
            chat_id = st.secrets["TELEGRAM_CHAT_ID"]
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
    except:
        pass

# התחברות ל-Supabase
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("⚠️ שגיאה בחיבור למסד הנתונים")
    st.stop()

# ============================================================
#       פונקציות טעינה עם Cache לביצועים מהירים
#       ttl=10 = הנתונים מתעדכנים כל 10 שניות
# ============================================================
@st.cache_data(ttl=10)
def load_global_message():
    res = supabase.table("global_msg").select("content").eq("id", 1).execute()
    return res.data[0]['content'] if res.data else "אין הודעה פעילה"

@st.cache_data(ttl=10)
def load_flights():
    res = supabase.table("flights").select("*").execute()
    return res.data if res.data else []

@st.cache_data(ttl=10)
def load_credits():
    res = supabase.table("credits").select("*").order("id", desc=True).execute()
    return res.data if res.data else []

@st.cache_data(ttl=10)
def load_questions(rep_filter="הצג הכל"):
    query = supabase.table("questions").select("*")
    if rep_filter != "הצג הכל":
        query = query.eq("rep_name", rep_filter)
    res = query.order("id", desc=True).execute()
    return res.data if res.data else []

def clear_all_cache():
    """מנקה את ה-cache אחרי שינוי בנתונים"""
    st.cache_data.clear()

# ============================================================
#                    הודעת הנהלה
# ============================================================
global_message = load_global_message()

st.markdown(f"""
    <div class="management-alert">
        <span class="management-alert-icon">📢</span>
        <span><strong>הודעת הנהלה:</strong> {global_message}</span>
    </div>
""", unsafe_allow_html=True)

with st.expander("⚙️ ערוך הודעת הנהלה"):
    new_global_msg = st.text_area("תוכן ההודעה החדשה", value=global_message, height=100)
    if st.button("💾 עדכן הודעה", key="update_global"):
        supabase.table("global_msg").update({"content": new_global_msg}).eq("id", 1).execute()
        send_notification(f"📢 הודעת הנהלה חדשה:\n{new_global_msg}")
        clear_all_cache()
        st.rerun()

st.markdown("<br>", unsafe_allow_html=True)

# ============================================================
#                    Tabs ראשיים
# ============================================================
tab1, tab2, tab3 = st.tabs(["✈️  עדכוני טיסות", "💰  ניהול זיכויים", "💬  שאלות ובקשות"])

# --- טאב 1: טיסות ---
with tab1:
    st.markdown("### ✈️ סטטוס טיסות ויעדים")
    st.caption("ניהול ועדכון תדירות הטיסות לכל היעדים הפעילים")

    fixed_destinations = ["אנגליה", "ארה\"ב", "יוון", "דובאי"]
    flights_data = load_flights()
    existing_dests = [r['destination'] for r in flights_data]

    # אם חסרים יעדים - הוסף אותם
    missing_dests = [d for d in fixed_destinations if d not in existing_dests]
    if missing_dests:
        for dest in missing_dests:
            supabase.table("flights").insert({
                "destination": dest,
                "regular": "ממתין לעדכון",
                "liquid": "ממתין לעדכון"
            }).execute()
        clear_all_cache()
        flights_data = load_flights()

    df_fl = pd.DataFrame(flights_data)
    df_fl = df_fl[df_fl['destination'].isin(fixed_destinations)]

    st.markdown("<br>", unsafe_allow_html=True)
    st.table(
        df_fl[['destination', 'regular', 'liquid']].rename(columns={
            'destination': '🌍 יעד',
            'regular': '📅 תדירות רגילה',
            'liquid': '💧 נוזלים אחרון'
        })
    )

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### ✏️ עריכת יעדים")

    cols = st.columns(2)
    for i, row in enumerate(flights_data):
        with cols[i % 2]:
            with st.expander(f"🌍 {row['destination']}"):
                nr = st.text_input("📅 תדירות רגילה", value=row['regular'], key=f"r_{row['id']}")
                nl = st.text_input("💧 תאריך נוזלים", value=row['liquid'], key=f"l_{row['id']}")
                if st.button("💾 שמור שינויים", key=f"f_b_{row['id']}"):
                    supabase.table("flights").update({"regular": nr, "liquid": nl}).eq("id", row['id']).execute()
                    send_notification(f"✈️ עדכון {row['destination']}: רגילה {nr}, נוזלים {nl}")
                    clear_all_cache()
                    st.rerun()

# --- טאב 2: זיכויים ---
with tab2:
    st.markdown("### 💰 מעקב זיכויים")
    st.caption("ניהול ומעקב אחר בקשות זיכוי מכל המחסנים")

    credits_data = load_credits()

    with st.expander("➕ העלאת זיכוי חדש"):
        with st.form("c_form"):
            col1, col2 = st.columns(2)
            with col1:
                pn = st.text_input("📦 מספר חבילה")
                ph = st.text_input("📞 טלפון")
                cb = st.text_input("👤 שם נציג מעביר")
            with col2:
                rd = st.date_input("📅 תאריך")
                rs = st.selectbox("📋 סיבה", [
                    "מחסן יוון", "מחסן אנגליה", "מחסן ארה\"ב",
                    "מחסן דובאי", "אקסלוט", "זיכוי פנימי"
                ])
                tr = st.text_input("🔗 קישור טרלו")
            if st.form_submit_button("✅ שלח זיכוי"):
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                supabase.table("credits").insert({
                    "package_num": pn,
                    "phone": ph,
                    "reason": rs,
                    "trello": tr,
                    "status": "ממתין",
                    "timestamp": now,
                    "request_date": rd.strftime("%d/%m/%Y"),
                    "credited_by": cb
                }).execute()
                send_notification(f"💰 זיכוי חדש מ{cb}!\nחבילה: {pn}")
                clear_all_cache()
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📋 רשימת זיכויים")

    if credits_data:
        for row in credits_data:
            status_class = "status-done" if row['status'] == 'בוצע' else "status-pending"
            status_icon = "✅" if row['status'] == 'בוצע' else "⏳"

            st.markdown(f"""
                <div class="item-card">
                    <div style="display: flex; justify-content: space-between; align-items: center; flex-direction: row-reverse;">
                        <div>
                            <strong>📦 חבילה:</strong> {row['package_num']} &nbsp;|&nbsp;
                            <strong>👤 נציג:</strong> {row.get('credited_by','-')} &nbsp;|&nbsp;
                            <span class="{status_class}">{status_icon} {row['status']}</span>
                        </div>
                    </div>
                </div>
            """, unsafe_allow_html=True)

            if row['status'] == 'ממתין':
                if st.button("✅ סמן כבוצע", key=f"c_d_{row['id']}"):
                    supabase.table("credits").update({"status": "בוצע"}).eq("id", row['id']).execute()
                    clear_all_cache()
                    st.rerun()
    else:
        st.info("📭 אין זיכויים להצגה כרגע")

# --- טאב 3: שאלות ובקשות ---
with tab3:
    st.markdown("### 💬 מערכת שאלות ופניות")
    st.caption("שלח שאלות למנהלים וצפה בתיבת הפניות האישית")

    with st.expander("❓ שלח שאלה חדשה"):
        with st.form("q_f"):
            c1, c2 = st.columns(2)
            with c1:
                rep_sender = st.selectbox("👤 מי הנציג?", REPS)
            with c2:
                assign_to = st.selectbox("📨 למי השאלה?", MANAGERS)

            question_text = st.text_area("💭 תוכן השאלה", height=100)

            if st.form_submit_button("📤 שלח שאלה"):
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                supabase.table("questions").insert({
                    "rep_name": rep_sender,
                    "assigned_to": assign_to,
                    "question": question_text,
                    "answer": "",
                    "is_done": False,
                    "timestamp": now
                }).execute()
                send_notification(f"❓ שאלה חדשה ל{assign_to} מ{rep_sender}:\n{question_text}")
                clear_all_cache()
                st.success("✅ השאלה נשלחה בהצלחה!")
                st.rerun()

    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("#### 📥 צפייה בפניות")

    selected_rep = st.selectbox(
        "🔍 בחר נציג לצפייה בתיבה האישית שלו:",
        ["הצג הכל"] + REPS
    )

    questions_data = load_questions(selected_rep)

    if questions_data:
        for row in questions_data:
            q_display = f"~~{row['question']}~~" if row['is_done'] else row['question']
            ans_display = f"~~{row['answer']}~~" if row['is_done'] and row['answer'] else row['answer']
            status_emoji = "✅" if row['is_done'] else "📌"

            with st.expander(
                f"{status_emoji} ל: {row['assigned_to']} | מאת: {row['rep_name']} | 🕐 {row['timestamp']}"
            ):
                st.markdown(f"**💭 שאלה:** {q_display}")
                if row['answer']:
                    st.markdown(f"**💡 תשובה:** {ans_display}")

                st.divider()

                c1, c2 = st.columns([3, 1])
                with c1:
                    new_ans = st.text_input(
                        "✏️ עדכן תשובה",
                        value=row['answer'],
                        key=f"ans_in_{row['id']}"
                    )
                with c2:
                    is_done_val = st.checkbox(
                        "✅ סמן כבוצע",
                        value=row['is_done'],
                        key=f"done_ch_{row['id']}"
                    )

                if st.button("💾 עדכן פנייה", key=f"up_q_{row['id']}"):
                    supabase.table("questions").update({
                        "answer": new_ans,
                        "is_done": is_done_val
                    }).eq("id", row['id']).execute()

                    if not row['is_done'] and is_done_val:
                        send_notification(
                            f"✅ פנייה של {row['rep_name']} ל{row['assigned_to']} סומנה כבוצעה."
                        )

                    clear_all_cache()
                    st.success("✅ עודכן בהצלחה!")
                    st.rerun()
    else:
        st.info("📭 אין שאלות להצגה בתיבה זו")

# ============================================================
#                    Footer
# ============================================================
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; padding: 1.5rem; color: #6B7280; font-size: 0.85rem; border-top: 1px solid #E5E7EB; margin-top: 2rem;">
        © 2026 <strong style="color: #1BA3E8;">SHIP</strong><strong style="color: #1A1A1A;">TANBUL</strong> - מערכת ניהול פנימית
    </div>
""", unsafe_allow_html=True)