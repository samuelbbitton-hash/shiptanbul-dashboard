import streamlit as st
import pandas as pd
from datetime import datetime
import requests
from supabase import create_client, Client

# הגדרות עמוד
st.set_page_config(page_title="Shiptanbul Cloud", page_icon="📦", layout="wide")

# פונקציית שליחה לטלגרם - גרסה חסינה מתקלות
def send_telegram_msg(message):
    try:
        # בדיקה אם המפתחות קיימים ב-Secrets
        if "TELEGRAM_TOKEN" in st.secrets and "TELEGRAM_CHAT_ID" in st.secrets:
            token = st.secrets["TELEGRAM_TOKEN"]
            chat_id = str(st.secrets["TELEGRAM_CHAT_ID"])
            url = f"https://api.telegram.org/bot{token}/sendMessage"
            params = {"chat_id": chat_id, "text": message}
            # ביצוע השליחה ברקע מבלי לעצור את האתר
            requests.get(url, params=params, timeout=5)
    except Exception as e:
        # הדפסה ללוגים הפנימיים בלבד (לא למשתמש)
        print(f"Telegram Notification Error: {e}")

# התחברות ל-Supabase
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("שגיאה בחיבור למסד הנתונים. וודא שה-Secrets מוגדרים.")
    st.stop()

# --- המשך הקוד (סטטוס מחסנים, טיסות וכו') ---
# (השארתי את הלוגיקה זהה כדי שלא ייווצרו תקלות חדשות)

def get_data(table_name):
    return supabase.table(table_name).select("*").execute()

msg_res = supabase.table("global_msg").select("content").eq("id", 1).execute()
global_message = msg_res.data[0]['content'] if msg_res.data else "אין הודעה פעילה"

st.warning(f"📢 הודעת הנהלה: {global_message}")
st.title("📦 Shiptanbul Cloud - לוח תפעול")

tab1, tab2, tab3, tab4 = st.tabs(["📊 סטטוס מחסנים", "✈️ טיסות ולוגיסטיקה", "💰 ניהול זיכויים", "💬 שאלות ובקשות"])

with tab1:
    st.header("עדכון סטטוס מחסנים")
    with st.expander("📝 ערוך הודעה לכל הנציגים"):
        new_msg = st.text_area("תוכן ההודעה", value=global_message)
        if st.button("עדכן הודעה כללית"):
            supabase.table("global_msg").update({"content": new_msg}).eq("id", 1).execute()
            send_telegram_msg(f"הודעת הנהלה חדשה: {new_msg}")
            st.success("ההודעה עודכנה!")
            st.rerun()
    
    wh_res = get_data("warehouses")
    if wh_res.data:
        cols = st.columns(4)
        for i, row in enumerate(sorted(wh_res.data, key=lambda x: x['id'])):
            with cols[i]:
                st.subheader(row['location'])
                st.info(f"סטטוס: {row['status']}\nהעלאה: {row['upload']}\nאיחוד: {row['consolidation']}")
                with st.expander(f"ערוך {row['location']}"):
                    n_st = st.selectbox("סטטוס", ["פעיל", "חצי יום", "סגור", "חג מקומי"], key=f"wh_st_{row['id']}")
                    n_up = st.text_input("העלאה", value=row['upload'], key=f"wh_up_{row['id']}")
                    n_con = st.text_input("איחוד", value=row['consolidation'], key=f"wh_con_{row['id']}")
                    if st.button("עדכן", key=f"wh_btn_{row['id']}"):
                        supabase.table("warehouses").update({"status": n_st, "upload": n_up, "consolidation": n_con}).eq("id", row['id']).execute()
                        send_telegram_msg(f"עדכון מחסן {row['location']}: {n_st}")
                        st.rerun()

with tab2:
    st.header("עדכוני טיסות")
    fl_res = get_data("flights")
    if fl_res.data:
        df_fl = pd.DataFrame(fl_res.data).sort_values('id')
        st.table(df_fl[['destination', 'regular', 'liquid']].rename(columns={'destination':'יעד', 'regular':'טיסה רגילה', 'liquid':'טיסת נוזלים'}))
        with st.expander("ערוך נתוני טיסות"):
            for row in fl_res.data:
                c1, c2 = st.columns(2)
                with c1: nr = st.text_input(f"רגילה {row['destination']}", value=row['regular'], key=f"r_{row['id']}")
                with c2: nl = st.text_input(f"נוזלים {row['destination']}", value=row['liquid'], key=f"l_{row['id']}")
                if st.button(f"עדכן {row['destination']}", key=f"f_b_{row['id']}"):
                    supabase.table("flights").update({"regular": nr, "liquid": nl}).eq("id", row['id']).execute()
                    send_telegram_msg(f"עדכון טיסות {row['destination']}")
                    st.rerun()

with tab3:
    st.header("מעקב זיכויים")
    cred_res = supabase.table("credits").select("*").order("id", desc=True).execute()
    with st.expander("➕ העלאת זיכוי חדש"):
        with st.form("c_form"):
            pn = st.text_input("מספר חבילה")
            ph = st.text_input("טלפון")
            rs = st.selectbox("סיבה", ["מחסן יוון", "מחסן אנגליה", "מחסן ארה\"ב", "מחסן דובאי", "אקסלוט", "זיכוי פנימי"])
            if st.form_submit_button("שלח"):
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                supabase.table("credits").insert({"package_num": pn, "phone": ph, "reason": rs, "status": "ממתין", "timestamp": now}).execute()
                send_telegram_msg(f"💰 זיכוי חדש! חבילה: {pn}, סיבה: {rs}")
                st.rerun()
    for row in cred_res.data:
        st.write(f" חבילה {row['package_num']} | {row['reason']} | {row['status']}")

with tab4:
    st.header("פניות נציגים")
    with st.form("q_f"):
        rn = st.text_input("שם הנציג")
        qt = st.text_area("השאלה")
        if st.form_submit_button("שלח שאלה"):
            supabase.table("questions").insert({"rep_name": rn, "question": qt, "status": "פתוח"}).execute()
            send_telegram_msg(f"❓ שאלה מ{rn}: {qt}")
            st.rerun()