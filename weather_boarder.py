import requests
import streamlit as st
import pandas as pd
import altair as alt

# 取得資料
url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWA-B980AEA0-9AAB-4E53-8767-C8FAACBE74FB"
data = requests.get(url).json()
locations = data["records"]["location"]

st.title("中央氣象局天氣預報")

# 選地區
location_names = [loc["locationName"] for loc in locations]
selected_location = st.selectbox("選擇地區", location_names)

# 找到資料
loc = next(loc for loc in locations if loc["locationName"] == selected_location)
weather = {}

for item in loc["weatherElement"]:
    element = item["elementName"]
    for i in item['time']:
        time_range = f"{i['startTime']}~{i['endTime']}"
        value = i["parameter"]["parameterName"]
        if time_range not in weather:
            weather[time_range] = {}
        weather[time_range][element] = value

# 轉 DataFrame
df = pd.DataFrame([
    {
        "time": time_range,
        "weather": elements.get("Wx", "—"),
        "pop": float(elements.get("PoP", 0)),
        "max_temp": float(elements.get("MaxT", 0)),
        "min_temp": float(elements.get("MinT", 0)),
    }
    for time_range, elements in weather.items()
])

# Melt 轉長格式
df_long = pd.melt(df, id_vars=['time'], value_vars=['max_temp','min_temp'],
                  var_name='Temperature_Type', value_name='Temperature')

# 顯示表格
st.subheader(f"{selected_location} 天氣資料")
st.dataframe(df)

# 折線圖：溫度
st.subheader("Temperature Trend (°C)")
temp_chart = alt.Chart(df_long).mark_line(point=True).encode(
    x=alt.X('time:N', title='Time'),
    y=alt.Y('Temperature:Q', title='°C'),
    color=alt.Color('Temperature_Type:N', title='Type'),
    tooltip=['time', 'Temperature_Type', 'Temperature']
).properties(width=700, height=400)
st.altair_chart(temp_chart)

# 降雨率柱狀圖
st.subheader("Rain Probability (PoP%)")
pop_chart = alt.Chart(df).mark_bar(color='skyblue').encode(
    x=alt.X('time:N', title='Time'),
    y=alt.Y('pop:Q', title='PoP (%)'),
    tooltip=['time', 'pop']
).properties(width=700, height=400)
st.altair_chart(pop_chart)
