# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import folium
from streamlit.components.v1 import html

st.set_page_config(page_title="서울시 소음-건강 영향 분석 시스템", layout="wide")

# ---------------------------
# 제목
# ---------------------------
st.title("서울시 소음과 건강 영향 분석 시스템")
st.markdown("보건환경연구원 정책 시뮬레이션 및 시각화 도구")

# ---------------------------
# 데이터 (보고서 기반 + 좌표 추가)
# ---------------------------
data = pd.DataFrame({
    "지역": ["주거", "상권", "교통"],
    "noise": [47.3, 56.14, 68.04],
    "stress": [19.1, 23.86, 32.3],
    "psqi": [6.3, 8.23, 11.74],
    "sleep": [6.62, 5.93, 4.99],
    "lat": [37.654, 37.566, 37.550],
    "lon": [127.056, 126.978, 126.990]
})

# ---------------------------
# 사이드바
# ---------------------------
st.sidebar.header("분석 설정")

region = st.sidebar.selectbox("지역 선택", data["지역"])
noise_change = st.sidebar.slider("야간 소음 변화량 (dB)", -10, 10, 0)

selected = data[data["지역"] == region].iloc[0]

base_noise = selected["noise"]
new_noise = base_noise + noise_change

# ---------------------------
# 회귀 기반 계산
# ---------------------------
stress = selected["stress"] + (noise_change * 0.48)
psqi = selected["psqi"] + (noise_change * 0.20)
sleep = selected["sleep"] - (noise_change * 0.053)

# ---------------------------
# 결과 KPI
# ---------------------------
st.subheader("핵심 결과 지표")

col1, col2, col3 = st.columns(3)

col1.metric("스트레스 점수", f"{stress:.2f}")
col2.metric("수면 질 (PSQI)", f"{psqi:.2f}")
col3.metric("수면시간", f"{sleep:.2f} 시간")

st.info(f"야간 소음 변화: {base_noise:.1f} dB → {new_noise:.1f} dB")

# ---------------------------
# 지도 (Folium → 폰트 안전)
# ---------------------------
st.subheader("서울 지역 시각화")

m = folium.Map(location=[37.5665, 126.9780], zoom_start=11)

for _, row in data.iterrows():
    folium.CircleMarker(
        location=[row["lat"], row["lon"]],
        radius=10,
        popup=f"{row['지역']}<br>소음:{row['noise']} dB",
        color="blue",
        fill=True
    ).add_to(m)

html(m._repr_html_(), height=500)

# ---------------------------
# 그래프 (영어로 → 깨짐 방지)
# ---------------------------
st.subheader("Noise Impact Analysis")

noise_range = np.arange(base_noise - 10, base_noise + 11, 1)

stress_line = selected["stress"] + ((noise_range - base_noise) * 0.48)
sleep_line = selected["sleep"] - ((noise_range - base_noise) * 0.053)

fig, ax = plt.subplots()

ax.plot(noise_range, stress_line, label="Stress")
ax.plot(noise_range, sleep_line, label="Sleep Time")

ax.set_xlabel("Night Noise (dB)")
ax.set_ylabel("Value")
ax.set_title("Noise vs Health Impact")
ax.legend()

st.pyplot(fig)

# ---------------------------
# 정책 인사이트
# ---------------------------
st.subheader("정책 시사점")

if region == "교통":
    st.warning("교통지역은 속도 제한, 저소음 포장 등 정책 적용 시 효과가 가장 큼")
elif region == "상권":
    st.info("상권지역은 심야 소음 관리 정책이 중요")
else:
    st.success("주거지역은 생활소음 관리와 차음 성능 개선 필요")

# ---------------------------
# 결론
# ---------------------------
st.subheader("결론")

st.write("""
- 야간 소음은 스트레스 증가와 수면 감소에 직접적인 영향을 미침
- 교통지역에서 건강 영향이 가장 크게 나타남
- 소음 저감 정책은 수면 개선 및 스트레스 완화 효과 기대 가능
""")
