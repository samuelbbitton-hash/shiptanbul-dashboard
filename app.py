import streamlit as st
import pandas as pd
from datetime import datetime
import io
import requests
from supabase import create_client, Client

# הגדרות עמוד
st.set_page_config(page_title="Shiptanbul Cloud", page_icon="📦", layout="wide")

# פונקציית שליחה לטלגרם - תדווח על כל שינוי
def send_telegram_msg(message):
    try:
        token = st.secrets["TELEGRAM_TOKEN"]
        chat_id = st.secrets["TELEGRAM_CHAT_ID"]
        url = f"https://api.telegram.org/bot{token}/sendMessage"
        payload = {"chat_id": chat_id, "text": message, "parse_mode": "Markdown"}
        requests.post(url, data=payload)
    except Exception as e:
        st.error(f"שגיאה בשליחת הודעה לטלגרם: {e}")

# התחברות ל-Supabase
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except:
    st.error("שגיאה בחיבור למסד הנתונים. בדוק את ה-Secrets.")
    st.stop()

# פונקציות עזר
def get_data(table_name):
    return supabase.table(table_name).select("*").execute()

# טעינת הודעה גלובלית
msg_res = supabase.table("global_msg").select("content").eq("id", 1).execute()
global_message = msg_res.data[0]['content'] if msg_res.data else "אין הודעה פעילה"

st.warning(f"📢 **הודעת הנהלה:** {global_message}")
st.title("📦 Shiptanbul Cloud - לוח תפעול")

tab1, tab2, tab3, tab4 = st.tabs(["📊 סטטוס מחסנים", "✈️ טיסות ולוגיסטיקה", "💰 ניהול זיכויים", "💬 שאלות ובקשות"])

# --- טאב 1: מחסנים ---
with tab1:
    st.header("עדכון סטטוס מחסנים")
    with st.expander("📝 ערוך הודעה לכל הנציגים"):
        new_msg = st.text_area("תוכן ההודעה", value=global_message)
        if st.button("עדכן הודעה כללית"):
            supabase.table("global_msg").update({"content": new_msg}).eq("id", 1).execute()
            send_telegram_msg(f"📢 *הודעת הנהלה חדשה:* \n{new_msg}")
            st.success("ההודעה עודכנה!")
            st.rerun()

    wh_res = get_data("warehouses")
    if wh_res.data:
        cols = st.columns(4)
        for i, row in enumerate(sorted(wh_res.data, key=lambda x: x['id'])):
            with cols[i]:
                st.subheader(row['location'])
                st.info(f"**סטטוס:** {row['status']}\n**העלאה:** {row['upload']}\n**איחוד:** {row['consolidation']}")
                with st.expander(f"ערוך {row['location']}"):
                    n_st = st.selectbox("סטטוס", ["פעיל", "חצי יום", "סגור", "חג מקומי"], key=f"wh_st_{row['id']}", index=["פעיל", "חצי יום", "סגור", "חג מקומי"].index(row['status']) if row['status'] in ["פעיל", "חצי יום", "סגור", "חג מקומי"] else 0)
                    n_up = st.text_input("העלאה", value=row['upload'], key=f"wh_up_{row['id']}")
                    n_con = st.text_input("איחוד", value=row['consolidation'], key=f"wh_con_{row['id']}")
                    if st.button("עדכן מחסן", key=f"wh_btn_{row['id']}"):
                        supabase.table("warehouses").update({"status": n_st, "upload": n_up, "consolidation": n_con}).eq("id", row['id']).execute()
                        send_telegram_msg(f"🏗️ *עדכון מחסן {row['location']}:*\nסטטוס: {n_st}\nהעלאה: {n_up}\nאיחוד: {n_con}")
                        st.rerun()

# --- טאב 2: טיסות ---
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
                if st.button(f"עדכן טיסות {row['destination']}", key=f"f_b_{row['id']}"):
                    supabase.table("flights").update({"regular": nr, "liquid": nl}).eq("id", row['id']).execute()
                    send_telegram_msg(f"✈️ *עדכון טיסות ליעד {row['destination']}:*\nרגילה: {nr}\nנוזלים: {nl}")
                    st.rerun()

# --- טאב 3: זיכויים ---
with tab3:
    st.header("מעקב זיכויים")
    cred_res = supabase.table("credits").select("*").order("id", desc=True).execute()
    
    with st.expander("➕ העלאת זיכוי חדש"):
        with st.form("c_form"):
            pn = st.text_input("מספר חבילה")
            ph = st.text_input("טלפון")
            rd = st.date_input("תאריך בקשה")
            rs = st.selectbox("סיבה", ["מחסן יוון", "מחסן אנגליה", "מחסן ארה\"ב", "מחסן דובאי", "אקסלוט", "זיכוי פנימי"])
            tr = st.text_input("קישור טרלו")
            if st.form_submit_button("שלח למערכת"):
                now = datetime.now().strftime("%d/%m/%Y %H:%M")
                supabase.table("credits").insert({
                    "package_num": pn, "phone": ph, "reason": rs, "trello": tr, 
                    "status": "ממתין", "timestamp": now, "request_date": rd.strftime("%d/%m/%Y")
                }).execute()
                send_telegram_msg(f"💰 *זיכוי חדש הועלה!*\n📦 חבילה: {pn}\n📞 טלפון: {ph}\n📝 סיבה: {rs}\n🔗 [קישור לטרלו]({tr})")
                st.rerun()

    for row in cred_res.data:
        with st.container():
            c_i, c_b = st.columns([4, 1])
            with c_i:
                st.write(f"**חבילה {row['package_num']}** | {row['reason']} | {row['status']}")
            with c_b:
                if row['status'] == 'ממתין' and st.button("בוצע ✅", key=f"c_d_{row['id']}"):
                    supabase.table("credits").update({"status": "בוצע"}).eq("id", row['id']).execute()
                    send_telegram_msg(f"✅ *זיכוי טופל!*\nחבילה: {row['package_num']} סומנה כבוצעה.")
                    st.rerun()
            st.write("---")

# --- טאב 4: שאלות ---
with tab4:
    st.header("פניות נציגים")
    with st.form("q_f"):
        rn = st.text_input("שם הנציג")
        qt = st.text_area("השאלה/בקשה")
        if st.form_submit_button("שלח שאלה"):
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            supabase.table("questions").insert({"rep_name": rn, "question": qt, "answer": "", "status": "פתוח", "timestamp": now}).execute()
            send_telegram_msg(f"❓ *שאלה חדשה מנציג!*\n👤 מאת: {rn}\n💬 שאלה: {qt}")
            st.rerun()
    
    q_res = supabase.table("questions").select("*").order("id", desc=True).execute()
    for row in q_res.data:
        with st.expander(f"📌 {row['rep_name']}: {row['question'][:30]}..."):
            st.write(f"*שאלה:* {row['question']}")
            ans = st.text_input("תשובה", value=row['answer'], key=f"ans_{row['id']}")
            if st.button("שלח תשובה", key=f"u_q_{row['id']}"):
                supabase.table("questions").update({"answer": ans}).eq("id", row['id']).execute()
                send_telegram_msg(f"💡 *יש תשובה לנציג {row['rep_name']}!*\nשאלה: {row['question']}\nתשובה: {ans}")
                st.success("התשובה נשלחה!")
                st.rerun()