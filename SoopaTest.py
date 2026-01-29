import streamlit as st
import pandas as pd
from datetime import date
from datetime import datetime
from streamlit_calendar import calendar
import re

# Page config
st.set_page_config(
    page_title="Live Schedule",
    layout="wide"
)

st.title("📅 Live Soopa Rental Schedule")



# Load data
@st.cache_data(ttl=30)
def load_data():
    url = "https://docs.google.com/spreadsheets/d/1qw_0cW4ipW5eYh1_sqUyvZdIcjmYXLcsS4J6Y4NoU6A/export?format=csv&gid=1912796754"
    df = pd.read_csv(url, header=6)
    df["Delivery_Date"] = pd.to_datetime(df["Delivery_Date"])
    return df

df = load_data()
# Filter only INV-R
df = df[df["TYPE"] == "INV-R"]
#--------------------------------------------------




# first calendar-------- Build events list --------
events = []
for _, row in df.iterrows():
    events.append({
        "title": f"{row['Item_1']} ({row['INVOICE_NUM']})",
        "start": row["Delivery_Date"].strftime("%Y-%m-%d"),
        "end": row["Delivery_Date"].strftime("%Y-%m-%d"),
        # optional: set colors etc
        "backgroundColor": "#4caf50",
        "borderColor": "#4caf50",
        "textColor": "#ffffff",
    })

# -------- Calendar config --------
calendar_options = {
    "initialView": "dayGridMonth",       # month view
    "headerToolbar": {
        "left": "prev,next today",
        "center": "title",
        "right": "dayGridMonth,timeGridWeek,listWeek"
    },
    "selectable": True,                  # allow selection
    "editable": False,                   # not editable for now
}

# -------- Render calendar --------
if events:
    cal_state = calendar(
        events=events,
        options=calendar_options,
        key="schedule_calendar"
    )
else:
    st.info("No events to show this month.")

# -------- Show clicked details (optional) --------

if cal_state and "eventClick" in cal_state:
    ev = cal_state["eventClick"]["event"]
    st.markdown(f"### 📌 Selected event: {ev['title']}")
    st.write("🗓 Date:", ev["start"])


#capture clicked date
selected_cal_date = None

if cal_state and cal_state.get("dateClick"):
    clicked = cal_state["dateClick"]["date"]
    
    selected_cal_date = (
    pd.to_datetime(clicked, utc=True)
      .tz_convert("Asia/Kuala_Lumpur")
      .date()
      )

#convert it
if selected_cal_date:
    #filter data for that date
    daily_df = df[df["Delivery_Date"].dt.date == selected_cal_date]
else:
    daily_df = pd.DataFrame()

if st.button("🔄 Refresh data"):
    st.cache_data.clear()

if daily_df.empty:
    st.info("No schedule for this date.")
else:
    st.subheader("📋 Schedule of the Day")

    for _, row in daily_df.iterrows():
        st.markdown(f"""
        <div style="
            padding:12px;
            margin-bottom:10px;
            border-left:5px solid #2196F3;
            background:rgba(255,255,255,0.05);
            border-radius:8px;
        ">
            <b>Customer:</b> {row['NAME']}<br>
            <b>Product:</b> {row['Item_1']}<br>
            <b>Location:</b> {row['Cawangan/Stokis']}<br>
        </div>
        """, unsafe_allow_html=True)

    #------------------------------------------------
    # section 2 - Available items logic

    # Define inventory
    INVENTORY = [
        "BANANA",
        "HIPPO",
        "THOMAS",
        "BOAT",
        "TWISTER",
        "BBALL",
        "LITTLEBALL",
        "DOLPHIN",
        "ARIEL",
        "UNICORN",
        "FROZEN",
        "SPIDER",
        "CANDY",
        "HULK",
        "RACING",
        "COURT",
        "GATOR",
        "PRINCESS",
        "HOTWHEEL",
        "BUILDER",
        "ATLANTICA",
        "MARVEL",
        "CROCC",
        "POSEIDON",
        "PLAYLAND",
        "ISLAND",
        "RAMBO",
        "UNIVERSE",
        "MEGALODON",
        "TORNADO",
        "MINI SPONGEBOB",
        "MINI TRANSFORMERS",
        "MINI MAZE",
        "SPARROW",
        "TROPICANA",
        "SPONGEBOB",
        "TRANSFORMERS",
        "MAZE HOUSE",
        "DOMINION",
        "MICKEY"
    ]

    # Parsing logic
    def extract_products(text):
        if not isinstance(text, str):
            return set()

        text = text.upper()

        found = set()
        for product in INVENTORY:
            if product in text:
                found.add(product)
    
        return found

    

    
    # determine booked items
    booked_items = set()

    for text in daily_df['Item_1'].fillna(''):
        booked_items.update(extract_products(text))
        

    # availability
    available_items = [i for i in INVENTORY if i not in booked_items]
    unavailable_items = [i for i in INVENTORY if i in booked_items]


    #display result 
    st.subheader("📦 Availability for the Day")

    col1, col2 = st.columns(2)

    with col1:
        st.markdown("### ✅ Available")
        for item in available_items:
            st.success(item)

    with col2:
        st.markdown("### ❌ Booked")
        for item in unavailable_items:
            st.error(item)
    #------------------------------------------------

