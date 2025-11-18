import requests
import json
import streamlit as st
import pandas as pd
import altair as alt

# 取得資料
data = requests.get(
    "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWA-B980AEA0-9AAB-4E53-8767-C8FAACBE74FB"
).json()
locations = data["records"]["location"]

# Streamlit app
st.title("中央氣象局天氣預報")

# 選擇地區
location_names = [loc["locationName"] for loc in locations]
selected_location = st.selectbox("選擇地區", location_names)

# 找到選定地區的資料
loc = next(loc for loc in locations if loc["locationName"] == selected_location)
weather = {}

for item in loc["weatherElement"]:
    element = item["elementName"]
    for i in item['time']:
        startTime = i['startTime']
        endTime = i['endTime']
        time = f"{startTime}~{endTime}"
        value = i["parameter"]["parameterName"]
        if time not in weather:
            weather[time] = {}
        weather[time][element] = value

# 將資料轉成 DataFrame
df = pd.DataFrame([
    {
        "時間": time,
        "天氣": elements.get("Wx", "—"),
        "降雨率": float(elements.get("PoP", 0)),
        "最高溫": float(elements.get("MaxT", 0)),
        "最低溫": float(elements.get("MinT", 0)),
    }
    for time, elements in weather.items()
])

# 顯示表格
st.subheader(f"{selected_location} 天氣資料")
st.dataframe(df)

# 折線圖：最高溫與最低溫
st.subheader("溫度趨勢")
temp_chart = alt.Chart(df).transform_fold(
    ["最高溫", "最低溫"],
    as_=['溫度類型', '溫度']
).mark_line(point=True).encode(
    x='時間',
    y='溫度',
    color='溫度類型'
).properties(width=700, height=400)
st.altair_chart(temp_chart)

# 柱狀圖：降雨率
st.subheader("降雨率趨勢")
pop_chart = alt.Chart(df).mark_bar(color='skyblue').encode(
    x='時間',
    y='降雨率'
).properties(width=700, height=400)
st.altair_chart(pop_chart)
