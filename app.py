# -*- coding: utf-8 -*-
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

st.set_page_config(page_title="Noise Health App", layout="wide")

# ---------------------------
# UI (한글은 Streamlit에서만 사용)
# ---------------------------
st.title("서울시 소음과 스트레스·수면 영향 분석")
st.markdown("시뮬레이션 기반 분석 앱")

# ---------------------------
# 데이터 (컬럼은 영어로 → 깨짐 방지)
# ---------------------------
data = {
    "region": ["Residential", "Commercial", "Traffic"],
    "noise": [47.3, 56.14, 68.04],
    "stress": [19.1, 23.86, 32.3],
    "psqi": [6.3, 8.23, 11.74],
    "sleep": [6.62, 5.93, 4.99]
}

df = pd.DataFrame(data)

# ---------------------------
# 한글 표시용 매핑
# ---------------------------
region_map = {
    "Residential": "주거",
    "Commercial": "상권",
    "Traffic": "교통"
}

# ---------------------------
# 사이드바
# ---------------------------
st.sidebar.header("설정")

region_kor = st.sidebar.selectbox("지역 선택", list(region_map.values()))

# 선택된 영어 키 찾기
region_eng = [k for k, v in region_map.items() if v == region_kor][0]

noise_change = st.sidebar.slider("야간 소음 변화량 (dB)", -10, 10, 0)

# ---------------------------
# 데이터 선택
# ---------------------------
selected = df[df["region"] == region_eng].iloc[0]

base_noise = selected["noise"]
new_noise = base_noise + noise_change

# ---------------------------
# 계산 (보고서 기반 계수)
# ---------------------------
stress = selected["stress"] + (noise_change * 0.48)
psqi = selected["psqi"] + (noise_change * 0.20)
sleep = selected["sleep"] - (noise_change * 0.053)

# ---------------------------
# 결과 출력
# ---------------------------
st.subheader("결과")

col1, col2, col3 = st.columns(3)

col1.metric("스트레스", f"{stress:.2f}")
col2.metric("PSQI", f"{psqi:.2f}")
col3.metric("수면시간", f"{sleep:.2f} 시간")

st.write(f"야간 소음: {base_noise:.1f} dB → {new_noise:.1f} dB")

# ---------------------------
# 그래프 (영어만 사용 → 절대 안 깨짐)
# ---------------------------
st.subheader("Noise Impact Simulation")

noise_range = np.arange(base_noise - 10, base_noise + 11, 1)

stress_line = selected["stress"] + ((noise_range - base_noise) * 0.48)
sleep_line = selected["sleep"] - ((noise_range - base_noise) * 0.053)

fig, ax = plt.subplots()

ax.plot(noise_range, stress_line, label="Stress")
ax.plot(noise_range, sleep_line, label="Sleep Time")

ax.set_xlabel("Night Noise (dB)")
ax.set_ylabel("Value")
ax.legend()

st.pyplot(fig)

# ---------------------------
# 정책 메시지
# ---------------------------
st.subheader("정책 제안")

if region_eng == "Traffic":
    st.warning("교통지역: 속도 제한, 저소음 포장, 야간 차량 관리 필요")
elif region_eng == "Commercial":
    st.info("상권지역: 심야 소음 및 배달 차량 관리 필요")
else:
    st.success("주거지역: 생활소음 관리 및 차음 성능 개선 필요")
