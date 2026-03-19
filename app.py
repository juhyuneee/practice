# app.py

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="서울시 소음-건강 영향 분석", layout="wide")

st.title("📊 서울시 소음과 스트레스·수면 영향 분석")
st.markdown("간단한 시뮬레이션 기반 분석 앱")

# 데이터 (보고서 기반)
data = {
    "지역": ["주거", "상권", "교통"],
    "야간소음(dB)": [47.3, 56.14, 68.04],
    "스트레스": [19.1, 23.86, 32.3],
    "PSQI": [6.3, 8.23, 11.74],
    "수면시간": [6.62, 5.93, 4.99]
}

df = pd.DataFrame(data)

# 사이드바
st.sidebar.header("⚙️ 설정")
region = st.sidebar.selectbox("지역 선택", df["지역"])
noise_change = st.sidebar.slider("야간 소음 변화량 (dB)", -10, 10, 0)

# 선택 데이터
selected = df[df["지역"] == region].copy()
base_noise = selected["야간소음(dB)"].values[0]
new_noise = base_noise + noise_change

# 회귀 기반 계산
stress = selected["스트레스"].values[0] + (noise_change * 0.48)
psqi = selected["PSQI"].values[0] + (noise_change * 0.20)
sleep = selected["수면시간"].values[0] - (noise_change * 0.053)

# 결과 표시
st.subheader("📌 결과")
col1, col2, col3 = st.columns(3)

col1.metric("스트레스", f"{stress:.2f}")
col2.metric("PSQI", f"{psqi:.2f}")
col3.metric("수면시간", f"{sleep:.2f} 시간")

st.write(f"야간 소음: {base_noise:.1f} dB → {new_noise:.1f} dB")

# 그래프
st.subheader("📈 소음 변화 영향")

noise_range = np.arange(base_noise - 10, base_noise + 11, 1)
stress_line = selected["스트레스"].values[0] + ((noise_range - base_noise) * 0.48)
sleep_line = selected["수면시간"].values[0] - ((noise_range - base_noise) * 0.053)

fig, ax = plt.subplots()
ax.plot(noise_range, stress_line, label="스트레스")
ax.plot(noise_range, sleep_line, label="수면시간")

ax.set_xlabel("야간 소음 (dB)")
ax.set_ylabel("값")
ax.legend()

st.pyplot(fig)

# 정책 메시지
st.subheader("💡 정책 제안")

if region == "교통":
    st.warning("속도 제한, 저소음 포장, 야간 차량 관리 필요")
elif region == "상권":
    st.info("심야 소음 및 배달 차량 관리 필요")
else:
    st.success("생활소음 관리 및 차음 성능 개선 필요")
