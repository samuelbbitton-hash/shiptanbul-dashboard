import streamlit as st
import pandas as pd
from datetime import datetime
import io
from supabase import create_client, Client

# הגדרות עמוד
st.set_page_config(page_title="Shiptanbul Cloud", page_icon="📦", layout="wide")

# התחברות ל-Supabase
try:
    url: str = st.secrets["SUPABASE_URL"]
    key: str = st.secrets["SUPABASE_KEY"]
    supabase: Client = create_client(url, key)
except Exception as e:
    st.error("שגיאה בחיבור ל-Supabase. וודא שהגדרת את secrets.toml כראוי.")
    st.stop()

# פונקציות עזר
def get_data(table_name):
    try:
        return supabase.table(table_name).select("*").execute()
    except Exception:
        return None

# --- הצגת הודעה גלובלית ---
try:
    msg_res = supabase.table("global_msg").select("content").eq("id", 1).execute()
    global_message = msg_res.data[0]['content'] if (msg_res and msg_res.data) else "אין הודעה פעילה"
except:
    global_message = "שגיאה בטעינת הודעה"

st.warning(f"📢 **הודעת הנהלה:** {global_message}")
st.title("📦 Shiptanbul Cloud - לוח תפעול")

tab1, tab2, tab3, tab4 = st.tabs(["📊 סטטוס מחסנים", "✈️ טיסות ולוגיסטיקה", "💰 ניהול זיכויים", "💬 שאלות ובקשות"])

# --- טאב 1: מחסנים והודעה ---
with tab1:
    st.header("עדכון סטטוס מחסנים")
    with st.expander("📝 ערוך הודעה לכל הנציגים"):
        new_msg = st.text_area("תוכן ההודעה", value=global_message)
        if st.button("עדכן הודעה"):
            supabase.table("global_msg").update({"content": new_msg}).eq("id", 1).execute()
            st.success("ההודעה עודכנה!")
            st.rerun()

    wh_res = get_data("warehouses")
    if wh_res and wh_res.data:
        cols = st.columns(4)
        for i, row in enumerate(sorted(wh_res.data, key=lambda x: x.get('id', 0))):
            with cols[i]:
                st.subheader(row['location'])
                st.info(f"**סטטוס:** {row['status']}\n**העלאה:** {row['upload']}\n**איחוד:** {row['consolidation']}")
                with st.expander(f"ערוך {row['location']}"):
                    n_st = st.selectbox("סטטוס", ["פעיל", "חצי יום", "סגור", "חג מקומי"], key=f"wh_st_{row['id']}")
                    n_up = st.text_input("העלאה", value=row['upload'], key=f"wh_up_{row['id']}")
                    n_con = st.text_input("איחוד", value=row['consolidation'], key=f"wh_con_{row['id']}")
                    if st.button("עדכן", key=f"wh_btn_{row['id']}"):
                        supabase.table("warehouses").update({"status": n_st, "upload": n_up, "consolidation": n_con}).eq("id", row['id']).execute()
                        st.rerun()
    else:
        st.error("לא נמצאו נתוני מחסנים. וודא שהרצת את ה-SQL ב-Supabase.")

# --- טאב 2: טיסות ---
with tab2:
    st.header("עדכוני טיסות")
    fl_res = get_data("flights")
    if fl_res and fl_res.data:
        df_fl = pd.DataFrame(fl_res.data)
        if 'id' in df_fl.columns:
            df_fl = df_fl.sort_values('id')
        
        st.table(df_fl[['destination', 'regular', 'liquid']].rename(columns={'destination':'יעד', 'regular':'טיסה רגילה', 'liquid':'טיסת נוזלים'}))
        
        with st.expander("ערוך נתוני טיסות"):
            for row in fl_res.data:
                c1, c2 = st.columns(2)
                with c1: nr = st.text_input(f"רגילה {row['destination']}", value=row['regular'], key=f"r_{row['id']}")
                with c2: nl = st.text_input(f"נוזלים {row['destination']}", value=row['liquid'], key=f"l_{row['id']}")
                if st.button(f"עדכן טיסות {row['destination']}", key=f"f_b_{row['id']}"):
                    supabase.table("flights").update({"regular": nr, "liquid": nl}).eq("id", row['id']).execute()
                    st.rerun()
    else:
        st.info("אין נתוני טיסות להצגה.")

# --- טאב 3: זיכויים ---
with tab3:
    st.header("מעקב זיכויים")
    try:
        cred_res = supabase.table("credits").select("*").order("id", desc=True).execute()
        df_cred = pd.DataFrame(cred_res.data)
        
        if not df_cred.empty:
            buffer = io.BytesIO()
            with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                df_cred.to_excel(writer, index=False)
            st.download_button("📥 הורד אקסל", data=buffer.getvalue(), file_name="credits.xlsx")

        with st.expander("➕ העלאת זיכוי חדש"):
            with st.form("c_form"):
                pn = st.text_input("מספר חבילה")
                ph = st.text_input("טלפון")
                rd = st.date_input("תאריך בקשה")
                rs = st.selectbox("סיבה", ["מחסן יוון", "מחסן אנגליה", "מחסן ארה\"ב", "מחסן דובאי", "אקסלוט", "זיכוי פנימי"])
                tr = st.text_input("טרלו")
                if st.form_submit_button("שלח"):
                    now = datetime.now().strftime("%d/%m/%Y %H:%M")
                    supabase.table("credits").insert({
                        "package_num": pn, "phone": ph, "reason": rs, "trello": tr, 
                        "status": "ממתין", "timestamp": now, "request_date": rd.strftime("%d/%m/%Y")
                    }).execute()
                    st.rerun()

        for row in cred_res.data:
            with st.container():
                c_i, c_b = st.columns([4, 1])
                with c_i:
                    st.write(f"{'~~' if row['status']=='בוצע' else ''}**חבילה {row['package_num']}** | {row['reason']} | {row['phone']}{'~~' if row['status']=='בוצע' else ''}")
                    st.caption(f"בקשה: {row['request_date']} | [טרלו]({row['trello']})")
                with c_b:
                    if row['status'] == 'ממתין' and st.button("בוצע", key=f"c_d_{row['id']}"):
                        supabase.table("credits").update({"status": "בוצע"}).eq("id", row['id']).execute()
                        st.rerun()
                    elif row['status'] == 'בוצע': st.success("טופל")
                st.write("---")
    except:
        st.info("ממתין לנתוני זיכויים...")

# --- טאב 4: שאלות ---
with tab4:
    st.header("פניות נציגים")
    with st.form("q_f"):
        rn = st.text_input("נציג")
        qt = st.text_area("שאלה")
        if st.form_submit_button("שלח"):
            now = datetime.now().strftime("%d/%m/%Y %H:%M")
            supabase.table("questions").insert({"rep_name": rn, "question": qt, "answer": "", "status": "פתוח", "timestamp": now}).execute()
            st.rerun()
    
    try:
        q_res = supabase.table("questions").select("*").order("id", desc=True).execute()
        for row in q_res.data:
            with st.expander(f"📌 {row['rep_name']}: {row['question'][:20]}..."):
                st.write(row['question'])
                ans = st.text_input("תשובה", value=row['answer'], key=f"ans_{row['id']}")
                c1, c2 = st.columns(2)
                with c1:
                    if st.button("עדכן תשובה", key=f"u_q_{row['id']}"):
                        supabase.table("questions").update({"answer": ans}).eq("id", row['id']).execute()
                        st.success("עודכן")
                with c2:
                    if st.button("מחק 🗑️", key=f"d_q_{row['id']}"):
                        supabase.table("questions").delete().eq("id", row['id']).execute()
                        st.rerun()
    except:
        st.info("אין שאלות פתוחות כרגע.")