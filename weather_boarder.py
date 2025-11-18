import requests
import streamlit as st
import pandas as pd
import altair as alt

st.title("中央氣象局天氣預報")

# API URL
url = "https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-C0032-001?Authorization=CWA-B980AEA0-9AAB-4E53-8767-C8FAACBE74FB"

# 取得資料（暫時忽略 SSL 驗證）
try:
    requests.packages.urllib3.disable_warnings()  # 隱藏警告
    response = requests.get(url, verify=False)
    response.raise_for_status()
    data = response.json()
except requests.exceptions.RequestException as e:
    st.error(f"無法取得資料: {e}")
    st.stop()

locations = data["records"]["location"]

# 選擇地區
location_names = [loc["locationName"] for loc in locations]
selected_location = st.selectbox("選擇地區", location_names)

# 找到該地區資料
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

# 轉成 DataFrame
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

# melt 轉長格式
df_long = pd.melt(df, id_vars=['time'], value_vars=['max_temp','min_temp'],
                  var_name='Temperature_Type', value_name='Temperature')


# 顯示表格
st.subheader(f"{selected_location} 天氣資料")
st.dataframe(df)

# 折線圖：最高溫 / 最低溫
st.subheader("溫度趨勢 (°C)")
temp_chart = alt.Chart(df_long).mark_line(point=True).encode(
    x=alt.X('time:N', title='時間', axis=alt.Axis(labelAngle=0)),
    y=alt.Y('Temperature:Q', title='攝氏溫度(°C)', scale=alt.Scale(domain=[10,40])),
    color=alt.Color('Temperature_Type:N', title='Type'),
    tooltip=[
    alt.Tooltip('time:N', title='時間'),
    alt.Tooltip('Temperature_Type:N', title='溫度類型'),
    alt.Tooltip('Temperature:Q', title='溫度 (°C)')
    ]
).properties(width=1000, height=400)
st.altair_chart(temp_chart)

# 柱狀圖：降雨率
st.subheader("降雨機率 (PoP%)")
pop_chart = alt.Chart(df).mark_bar(color='skyblue').encode(
    x=alt.X('time:N', title='時間', axis=alt.Axis(labelAngle=0)),
    y=alt.Y('pop:Q', title='降雨機率 (%)', scale=alt.Scale(domain=[0,100])),
    tooltip=[
    alt.Tooltip('time:N', title='時間'),
    alt.Tooltip('pop:Q', title='降雨機率 (%)')
    ]
).properties(width=1000, height=400)
st.altair_chart(pop_chart)
