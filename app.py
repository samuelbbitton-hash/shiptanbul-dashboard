import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from supabase import create_client, Client

# הגדרות עמוד
st.set_page_config(page_title="Shiptanbul Cloud", page_icon="📦", layout="wide")

# --- הזרקת CSS לעיצוב RTL (מימין לשמאל) ---
st.markdown("""
    <style>
    .main { direction: rtl; text-align: right; }
    div.stButton > button { width: 100%; }
    .stTabs [data-baseweb="tab-list"] { direction: rtl; }
    .stExpander { text-align: right; }
    p, h1, h2, h3, h4, h5, h6, label, div { text-align: right; direction: rtl; }
    /* תיקון ליישור טפסים */
    [data-testid="stForm"] { direction: rtl; }
    </style>
""", unsafe_allow_html=True)

# פונקציית שליחת הודעות (גם טלגרם וגם וואטסאפ)
def send_notification(message):
    # שליחה לטלגרם
    try:
        if "TELEGRAM_TOKEN" in st.secrets and "TELEGRAM_CHAT_ID" in st.secrets:
            token = st.secrets["TELEGRAM_TOKEN"]
            chat_id = st.secrets["TELEGRAM_CHAT_ID"]
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            requests.post(url, json={"chat_id": chat_id, "text": message}, timeout=5)
    except Exception as e:
        print(f"Telegram Error: {e}")

    # שליחה לוואטסאפ (באמצעות CallMeBot)
    # דורש הגדרה ב-Secrets: WHATSAPP_PHONE (בפורמט 972...) ו-WHATSAPP_API_KEY
    try:
        if "WHATSAPP_PHONE" in st.secrets and "WHATSAPP_API_KEY" in st.secrets:
            phone = st.secrets["WHATSAPP_PHONE"]
            apikey = st.secrets["WHATSAPP_API_KEY"]
            url = f"https://api.callmebot.com/whatsapp.php?phone={phone}&text={message}&apikey={apikey}"
            requests.get(url, timeout=5)
    except Exception as e:
        print(f"WhatsApp Error: {e}")

# התחברות ל-Supabase
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("שגיאה בחיבור למסד הנתונים. וודא שהגדרת את Secrets.")
    st.stop()

# טעינת הודעה גלובלית
msg_res = supabase.table("global_msg").select("content").eq("id", 1).execute()
global_message = msg_res.data[0]['content'] if msg_res.data else "אין הודעה פעילה"

st.warning(f"📢 הודעת הנהלה: {global_message}")
st.title("📦 Shiptanbul Cloud - לוח תפעול")

# הגדרת הטאבים החדשה (ללא מחסנים)
tab1, tab2, tab3 = st.tabs(["✈️ טיסות ולוגיסטיקה", "💰 ניהול זיכויים", "💬 שאלות ובקשות"])

# --- טאב 1: טיסות ---
with tab1:
    st.header("עדכוני טיסות")
    fl_res = supabase.table("flights").select("*").execute()
    if fl_res.data:
        df_fl = pd.DataFrame(fl_res.data).sort_values('id')
        st.table(df_fl[['destination', 'regular', 'liquid']].rename(columns={'destination':'יעד', 'regular':'טיסה רגילה', 'liquid':'טיסת נוזלים'}))
        
        with st.expander("ערוך נתוני טיסות"):
            for row in fl_res.data:
                c1, c2 = st.columns(2)
                with c1: nr = st.text_input(f"רגילה {row['destination']}", value=row['regular'], key=f"r_{row['id']}")
                with c2: nl = st.text_input(f"נוזלים {row['destination']}", value=row['liquid'], key=f"l_{row['id']}")
                if st.button(f"עדכן טיסות {row['destination']}", key=f"f_b_{row['id']}"):
                    supabase.table("flights").update({"regular": nr, "liquid": nl}).eq("id", row['id']).execute()
                    send_notification(f"✈️ עדכון טיסות {row['destination']}:\nרגילה: {nr}\nנוזלים: {nl}")
                    st.rerun()

# --- טאב 2: זיכויים ---
with tab2:
    st.header("מעקב זיכויים")
    cred_res = supabase.table("credits").select("*").order("id", desc=True).execute()
    
    with st.expander("➕ העלאת זיכוי חדש"):
        with st.form("c_form"):
            col1, col2 = st.columns(2)
            with col1:
                pn = st.text_input("מספר חבילה")
                ph = st.text_input("טלפון לקוח")
                credited_by = st.text_input("שם הנציג המזכה (המעביר)") # שדה חדש
            with col2:
                rd = st.date_input("תאריך בקשה")
                rs = st.selectbox("סיבה", ["מחסן יוון", "מחסן אנגליה", "מחסן ארה\"ב", "מחסן דובאי", "אקסלוט", "זיכוי פנימי"])
                tr = st.text_input("קישור טרלו")
            
            if st.form_submit_button("שלח למערכת"):
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                # וודא שהוספת עמודה credited_by ב-Supabase!
                supabase.table("credits").insert({
                    "package_num": pn, 
                    "phone": ph, 
                    "reason": rs, 
                    "trello": tr, 
                    "status": "ממתין", 
                    "timestamp": now, 
                    "request_date": rd.strftime("%d/%m/%Y"),
                    "credited_by": credited_by 
                }).execute()
                send_notification(f"💰 זיכוי חדש הועבר ע\"י {credited_by}!\nחבילה: {pn}\nסיבה: {rs}")
                st.success("הזיכוי נרשם!")
                st.rerun()

    # הצגת הזיכויים
    for row in cred_res.data:
        with st.container():
            c_i, c_b = st.columns([4, 1])
            # הצגת שם המזכה בתוך השורה
            by_user = row.get('credited_by', 'לא צוין')
            with c_i: 
                st.write(f"**חבילה:** {row['package_num']} | **סיבה:** {row['reason']} | **סטטוס:** {row['status']}")
                st.caption(f"הועבר ע\"י: {by_user} | תאריך: {row['timestamp']}")
            with c_b:
                if row['status'] == 'ממתין' and st.button("בוצע ✅", key=f"c_d_{row['id']}"):
                    supabase.table("credits").update({"status": "בוצע"}).eq("id", row['id']).execute()
                    send_notification(f"✅ זיכוי טופל!\nחבילה {row['package_num']} בוצעה בהצלחה.")
                    st.rerun()
            st.divider()

# --- טאב 3: שאלות וצא'ט ---
with tab3:
    st.header("פניות נציגים")
    with st.form("q_f"):
        rn, qt = st.text_input("שם הנציג"), st.text_area("השאלה/בקשה")
        if st.form_submit_button("שלח שאלה"):
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            supabase.table("questions").insert({"rep_name": rn, "question": qt, "answer": "", "status": "פתוח", "timestamp": now}).execute()
            send_notification(f"❓ שאלה חדשה מ{rn}:\n{qt}")
            st.rerun()
    
    q_res = supabase.table("questions").select("*").order("id", desc=True).execute()
    for row in q_res.data:
        with st.expander(f"📌 {row['rep_name']}: {row['question'][:30]}..."):
            st.write(f"**שאלה:** {row['question']}")
            ans = st.text_input("תשובה", value=row['answer'], key=f"ans_{row['id']}")
            if st.button("שלח תשובה", key=f"u_q_{row['id']}"):
                supabase.table("questions").update({"answer": ans}).eq("id", row['id']).execute()
                send_notification(f"💡 תשובה לנציג {row['rep_name']}:\n{ans}")
                st.success("התשובה נשלחה!")
                st.rerun()