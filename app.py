# -*- coding: utf-8 -*-
"""
서울시 지역 특성별 소음 노출과 건강 영향 분석 시스템
서울특별시 보건환경연구원 정책 시뮬레이션 도구
작성: 2026년 3월
"""

import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
import json

# ─────────────────────────────────────────────
# 페이지 설정
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="서울시 소음-건강 영향 분석 시스템",
    page_icon="🏙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ─────────────────────────────────────────────
# CSS 스타일
# ─────────────────────────────────────────────
st.markdown("""
<style>
  /* 전체 배경 */
  .main { background-color: #f4f6f9; }

  /* 헤더 배너 */
  .report-header {
    background: linear-gradient(135deg, #1a3a5c 0%, #2563a8 60%, #3b82c4 100%);
    color: white;
    padding: 28px 36px;
    border-radius: 10px;
    margin-bottom: 24px;
    box-shadow: 0 4px 16px rgba(37,99,168,0.18);
  }
  .report-header h1 { font-size: 1.7rem; font-weight: 700; margin: 0 0 6px 0; letter-spacing: -0.5px; }
  .report-header p  { font-size: 0.92rem; margin: 0; opacity: 0.88; }
  .report-header .badge {
    display: inline-block; background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.35);
    border-radius: 20px; padding: 2px 12px; font-size: 0.78rem; margin-top: 10px;
  }

  /* 섹션 제목 */
  .section-title {
    font-size: 1.08rem; font-weight: 700; color: #1a3a5c;
    border-left: 4px solid #2563a8; padding-left: 10px;
    margin: 22px 0 14px 0;
  }

  /* KPI 카드 */
  .kpi-card {
    background: white; border-radius: 10px;
    padding: 18px 20px; border: 1px solid #e2e8f0;
    box-shadow: 0 2px 8px rgba(0,0,0,0.06);
    text-align: center;
  }
  .kpi-label { font-size: 0.78rem; color: #64748b; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px; }
  .kpi-value { font-size: 2.0rem; font-weight: 800; color: #1a3a5c; line-height: 1.2; }
  .kpi-unit  { font-size: 0.82rem; color: #94a3b8; }
  .kpi-delta-pos { font-size: 0.82rem; color: #16a34a; font-weight: 600; }
  .kpi-delta-neg { font-size: 0.82rem; color: #dc2626; font-weight: 600; }

  /* 인포박스 */
  .info-box {
    background: #eff6ff; border: 1px solid #bfdbfe;
    border-radius: 8px; padding: 14px 18px; margin: 10px 0;
    font-size: 0.88rem; color: #1e40af;
  }
  .warn-box {
    background: #fefce8; border: 1px solid #fde68a;
    border-radius: 8px; padding: 14px 18px; margin: 10px 0;
    font-size: 0.88rem; color: #92400e;
  }
  .success-box {
    background: #f0fdf4; border: 1px solid #bbf7d0;
    border-radius: 8px; padding: 14px 18px; margin: 10px 0;
    font-size: 0.88rem; color: #14532d;
  }
  .danger-box {
    background: #fef2f2; border: 1px solid #fecaca;
    border-radius: 8px; padding: 14px 18px; margin: 10px 0;
    font-size: 0.88rem; color: #7f1d1d;
  }

  /* 사이드바 */
  [data-testid="stSidebar"] { background: #1a3a5c; }
  [data-testid="stSidebar"] * { color: white !important; }
  [data-testid="stSidebar"] .stSlider > div > div { background: #2563a8 !important; }

  /* 탭 */
  .stTabs [data-baseweb="tab"] { font-weight: 600; font-size: 0.92rem; }

  /* 테이블 */
  .data-table { width:100%; border-collapse:collapse; font-size:0.88rem; }
  .data-table th { background:#1a3a5c; color:white; padding:9px 12px; text-align:center; }
  .data-table td { padding:8px 12px; text-align:center; border-bottom:1px solid #e2e8f0; }
  .data-table tr:nth-child(even) { background:#f8fafc; }
  .data-table tr:hover { background:#eff6ff; }

  .tag-traffic  { background:#fee2e2; color:#991b1b; border-radius:12px; padding:2px 10px; font-size:0.75rem; font-weight:700; }
  .tag-commercial { background:#fef9c3; color:#78350f; border-radius:12px; padding:2px 10px; font-size:0.75rem; font-weight:700; }
  .tag-residential { background:#dcfce7; color:#14532d; border-radius:12px; padding:2px 10px; font-size:0.75rem; font-weight:700; }

  footer { visibility: hidden; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 서울 자치구 GeoJSON (주요 25개 자치구 좌표 기반 폴리곤)
# 실제 행정경계 근사 다각형 (WGS84)
# ─────────────────────────────────────────────
SEOUL_GEOJSON = {
  "type": "FeatureCollection",
  "features": [
    {"type":"Feature","properties":{"name":"강남구"},"geometry":{"type":"Polygon","coordinates":[[[127.0322,37.4979],[127.0743,37.4979],[127.0743,37.5326],[127.0559,37.5378],[127.0322,37.5200],[127.0322,37.4979]]]}},
    {"type":"Feature","properties":{"name":"강동구"},"geometry":{"type":"Polygon","coordinates":[[[127.1050,37.5209],[127.1527,37.5209],[127.1527,37.5630],[127.1268,37.5711],[127.0990,37.5499],[127.1050,37.5209]]]}},
    {"type":"Feature","properties":{"name":"강북구"},"geometry":{"type":"Polygon","coordinates":[[[126.9978,37.6277],[127.0265,37.6277],[127.0265,37.6594],[127.0080,37.6688],[126.9765,37.6450],[126.9978,37.6277]]]}},
    {"type":"Feature","properties":{"name":"강서구"},"geometry":{"type":"Polygon","coordinates":[[[126.8220,37.5390],[126.8740,37.5390],[126.8740,37.5831],[126.8435,37.5965],[126.8010,37.5640],[126.8220,37.5390]]]}},
    {"type":"Feature","properties":{"name":"관악구"},"geometry":{"type":"Polygon","coordinates":[[[126.9015,37.4640],[126.9541,37.4640],[126.9541,37.4950],[126.9342,37.5060],[126.8990,37.4870],[126.9015,37.4640]]]}},
    {"type":"Feature","properties":{"name":"광진구"},"geometry":{"type":"Polygon","coordinates":[[[127.0522,37.5300],[127.0943,37.5300],[127.0943,37.5558],[127.0762,37.5640],[127.0440,37.5480],[127.0522,37.5300]]]}},
    {"type":"Feature","properties":{"name":"구로구"},"geometry":{"type":"Polygon","coordinates":[[[126.8490,37.4880],[126.9020,37.4880],[126.9020,37.5201],[126.8810,37.5320],[126.8380,37.5090],[126.8490,37.4880]]]}},
    {"type":"Feature","properties":{"name":"금천구"},"geometry":{"type":"Polygon","coordinates":[[[126.8825,37.4492],[126.9155,37.4492],[126.9155,37.4790],[126.8997,37.4890],[126.8710,37.4680],[126.8825,37.4492]]]}},
    {"type":"Feature","properties":{"name":"노원구"},"geometry":{"type":"Polygon","coordinates":[[[127.0540,37.6450],[127.1000,37.6450],[127.1000,37.6854],[127.0750,37.6980],[127.0380,37.6680],[127.0540,37.6450]]]}},
    {"type":"Feature","properties":{"name":"도봉구"},"geometry":{"type":"Polygon","coordinates":[[[127.0265,37.6490],[127.0730,37.6490],[127.0730,37.6908],[127.0460,37.7020],[127.0060,37.6750],[127.0265,37.6490]]]}},
    {"type":"Feature","properties":{"name":"동대문구"},"geometry":{"type":"Polygon","coordinates":[[[127.0249,37.5670],[127.0620,37.5670],[127.0620,37.5940],[127.0490,37.6030],[127.0130,37.5840],[127.0249,37.5670]]]}},
    {"type":"Feature","properties":{"name":"동작구"},"geometry":{"type":"Polygon","coordinates":[[[126.9267,37.4900],[126.9810,37.4900],[126.9810,37.5240],[126.9620,37.5320],[126.9150,37.5110],[126.9267,37.4900]]]}},
    {"type":"Feature","properties":{"name":"마포구"},"geometry":{"type":"Polygon","coordinates":[[[126.8890,37.5410],[126.9390,37.5410],[126.9390,37.5750],[126.9190,37.5860],[126.8740,37.5640],[126.8890,37.5410]]]}},
    {"type":"Feature","properties":{"name":"서대문구"},"geometry":{"type":"Polygon","coordinates":[[[126.9200,37.5600],[126.9620,37.5600],[126.9620,37.5920],[126.9430,37.6010],[126.9060,37.5800],[126.9200,37.5600]]]}},
    {"type":"Feature","properties":{"name":"서초구"},"geometry":{"type":"Polygon","coordinates":[[[126.9980,37.4630],[127.0560,37.4630],[127.0560,37.5000],[127.0340,37.5130],[126.9800,37.4920],[126.9980,37.4630]]]}},
    {"type":"Feature","properties":{"name":"성동구"},"geometry":{"type":"Polygon","coordinates":[[[127.0190,37.5440],[127.0680,37.5440],[127.0680,37.5720],[127.0520,37.5810],[127.0050,37.5620],[127.0190,37.5440]]]}},
    {"type":"Feature","properties":{"name":"성북구"},"geometry":{"type":"Polygon","coordinates":[[[127.0010,37.5890],[127.0490,37.5890],[127.0490,37.6280],[127.0300,37.6380],[126.9780,37.6100],[127.0010,37.5890]]]}},
    {"type":"Feature","properties":{"name":"송파구"},"geometry":{"type":"Polygon","coordinates":[[[127.0820,37.4850],[127.1380,37.4850],[127.1380,37.5220],[127.1180,37.5380],[127.0680,37.5120],[127.0820,37.4850]]]}},
    {"type":"Feature","properties":{"name":"양천구"},"geometry":{"type":"Polygon","coordinates":[[[126.8560,37.5150],[126.9050,37.5150],[126.9050,37.5501],[126.8870,37.5620],[126.8400,37.5380],[126.8560,37.5150]]]}},
    {"type":"Feature","properties":{"name":"영등포구"},"geometry":{"type":"Polygon","coordinates":[[[126.8940,37.5030],[126.9400,37.5030],[126.9400,37.5360],[126.9230,37.5460],[126.8800,37.5240],[126.8940,37.5030]]]}},
    {"type":"Feature","properties":{"name":"용산구"},"geometry":{"type":"Polygon","coordinates":[[[126.9630,37.5200],[127.0070,37.5200],[127.0070,37.5500],[126.9910,37.5590],[126.9490,37.5390],[126.9630,37.5200]]]}},
    {"type":"Feature","properties":{"name":"은평구"},"geometry":{"type":"Polygon","coordinates":[[[126.9000,37.5960],[126.9490,37.5960],[126.9490,37.6490],[126.9230,37.6640],[126.8800,37.6300],[126.9000,37.5960]]]}},
    {"type":"Feature","properties":{"name":"종로구"},"geometry":{"type":"Polygon","coordinates":[[[126.9640,37.5730],[127.0050,37.5730],[127.0050,37.6060],[126.9870,37.6160],[126.9490,37.5960],[126.9640,37.5730]]]}},
    {"type":"Feature","properties":{"name":"중구"},"geometry":{"type":"Polygon","coordinates":[[[126.9740,37.5480],[127.0130,37.5480],[127.0130,37.5720],[127.0010,37.5810],[126.9600,37.5640],[126.9740,37.5480]]]}},
    {"type":"Feature","properties":{"name":"중랑구"},"geometry":{"type":"Polygon","coordinates":[[[127.0660,37.5840],[127.1060,37.5840],[127.1060,37.6180],[127.0870,37.6290],[127.0470,37.6040],[127.0660,37.5840]]]}}
  ]
}

# ─────────────────────────────────────────────
# 자치구 데이터 (보고서 기반)
# ─────────────────────────────────────────────
GU_DATA = {
    # 교통 특성
    "서초구":    {"유형":"교통", "표본수":6,  "주간소음":77.67, "야간소음":69.0,  "스트레스":32.30, "PSQI":11.74, "수면시간":5.58, "각성횟수":4.52},
    "구로구":    {"유형":"교통", "표본수":5,  "주간소음":76.2,  "야간소음":68.0,  "스트레스":31.80, "PSQI":11.50, "수면시간":4.76, "각성횟수":4.40},
    "강서구":    {"유형":"교통", "표본수":6,  "주간소음":76.0,  "야간소음":68.67, "스트레스":32.10, "PSQI":11.60, "수면시간":4.73, "각성횟수":4.45},
    "광진구":    {"유형":"교통", "표본수":5,  "주간소음":76.0,  "야간소음":67.4,  "스트레스":31.50, "PSQI":11.30, "수면시간":4.90, "각성횟수":4.30},
    "동대문구":  {"유형":"교통", "표본수":5,  "주간소음":75.0,  "야간소음":66.8,  "스트레스":31.00, "PSQI":11.10, "수면시간":4.92, "각성횟수":4.20},
    # 상권 특성
    "송파구":    {"유형":"상권", "표본수":4,  "주간소음":65.0,  "야간소음":57.25, "스트레스":23.86, "PSQI":8.23,  "수면시간":5.90, "각성횟수":2.82},
    "영등포구":  {"유형":"상권", "표본수":4,  "주간소음":65.0,  "야간소음":57.25, "스트레스":23.60, "PSQI":8.10,  "수면시간":5.82, "각성횟수":2.78},
    "마포구":    {"유형":"상권", "표본수":4,  "주간소음":64.75, "야간소음":57.0,  "스트레스":23.40, "PSQI":8.00,  "수면시간":5.80, "각성횟수":2.75},
    "중구":      {"유형":"상권", "표본수":5,  "주간소음":63.2,  "야간소음":55.4,  "스트레스":22.80, "PSQI":7.80,  "수면시간":5.98, "각성횟수":2.65},
    "강남구":    {"유형":"상권", "표본수":5,  "주간소음":62.0,  "야간소음":54.4,  "스트레스":22.20, "PSQI":7.60,  "수면시간":6.10, "각성횟수":2.58},
    # 주거 특성
    "양천구":    {"유형":"주거", "표본수":2,  "주간소음":57.5,  "야간소음":49.5,  "스트레스":19.60, "PSQI":6.50,  "수면시간":6.80, "각성횟수":1.90},
    "도봉구":    {"유형":"주거", "표본수":2,  "주간소음":57.0,  "야간소음":48.5,  "스트레스":19.40, "PSQI":6.40,  "수면시간":6.95, "각성횟수":1.85},
    "은평구":    {"유형":"주거", "표본수":2,  "주간소음":57.0,  "야간소음":48.5,  "스트레스":19.40, "PSQI":6.40,  "수면시간":7.00, "각성횟수":1.85},
    "노원구":    {"유형":"주거", "표본수":2,  "주간소음":56.5,  "야간소음":48.0,  "스트레스":19.10, "PSQI":6.30,  "수면시간":6.95, "각성횟수":1.80},
    "성북구":    {"유형":"주거", "표본수":2,  "주간소음":49.0,  "야간소음":42.0,  "스트레스":17.20, "PSQI":5.80,  "수면시간":5.40, "각성횟수":1.60},
    # 데이터 없는 나머지 자치구 (시나리오 기본값)
    "강동구":    {"유형":"상권", "표본수":0,  "주간소음":63.0,  "야간소음":55.0,  "스트레스":22.50, "PSQI":7.70,  "수면시간":5.95, "각성횟수":2.70},
    "강북구":    {"유형":"주거", "표본수":0,  "주간소음":55.0,  "야간소음":47.0,  "스트레스":19.00, "PSQI":6.20,  "수면시간":6.70, "각성횟수":1.78},
    "관악구":    {"유형":"상권", "표본수":0,  "주간소음":62.5,  "야간소음":54.0,  "스트레스":22.00, "PSQI":7.50,  "수면시간":6.05, "각성횟수":2.55},
    "금천구":    {"유형":"교통", "표본수":0,  "주간소음":74.0,  "야간소음":65.5,  "스트레스":30.50, "PSQI":10.90, "수면시간":5.02, "각성횟수":4.10},
    "동작구":    {"유형":"주거", "표본수":0,  "주간소음":56.0,  "야간소음":48.0,  "스트레스":19.10, "PSQI":6.30,  "수면시간":6.62, "각성횟수":1.80},
    "서대문구":  {"유형":"주거", "표본수":0,  "주간소음":55.5,  "야간소음":47.5,  "스트레스":19.05, "PSQI":6.25,  "수면시간":6.65, "각성횟수":1.79},
    "성동구":    {"유형":"교통", "표본수":0,  "주간소음":74.5,  "야간소음":66.0,  "스트레스":30.80, "PSQI":11.00, "수면시간":4.98, "각성횟수":4.15},
    "용산구":    {"유형":"상권", "표본수":0,  "주간소음":63.5,  "야간소음":55.5,  "스트레스":23.00, "PSQI":7.90,  "수면시간":5.88, "각성횟수":2.72},
    "종로구":    {"유형":"상권", "표본수":0,  "주간소음":63.0,  "야간소음":55.0,  "스트레스":22.50, "PSQI":7.70,  "수면시간":5.92, "각성횟수":2.68},
    "중랑구":    {"유형":"교통", "표본수":0,  "주간소음":74.0,  "야간소음":65.0,  "스트레스":30.20, "PSQI":10.80, "수면시간":5.05, "각성횟수":4.05},
}

# 정책 시나리오별 저감량
POLICY_REDUCTION = {"교통": -9.0, "상권": -5.0, "주거": -3.0}
REGRESSION = {"스트레스": 0.48, "PSQI": 0.20, "수면시간": -0.053}

# GeoJSON에 데이터 병합
def build_geojson(metric):
    features = []
    for f in SEOUL_GEOJSON["features"]:
        name = f["properties"]["name"]
        if name in GU_DATA:
            d = GU_DATA[name]
            f2 = json.loads(json.dumps(f))
            f2["properties"]["metric"] = d.get(metric, 0)
            f2["properties"]["유형"]   = d["유형"]
            f2["properties"]["야간소음"] = d["야간소음"]
            f2["properties"]["스트레스"] = d["스트레스"]
            f2["properties"]["PSQI"]   = d["PSQI"]
            f2["properties"]["수면시간"] = d["수면시간"]
            features.append(f2)
    return {"type":"FeatureCollection","features":features}

TYPE_COLOR = {"교통":"#dc2626","상권":"#d97706","주거":"#16a34a"}
TYPE_COLOR_LIGHT = {"교통":"#fee2e2","상권":"#fef9c3","주거":"#dcfce7"}

# ─────────────────────────────────────────────
# 사이드바
# ─────────────────────────────────────────────
with st.sidebar:
    st.markdown("## ⚙️ 분석 설정")
    st.markdown("---")
    st.markdown("### 📍 자치구 선택")
    gu_list = sorted(GU_DATA.keys())
    selected_gu = st.selectbox("자치구", gu_list, index=gu_list.index("강남구"))

    st.markdown("---")
    st.markdown("### 🔊 정책 시뮬레이션")
    noise_change = st.slider("야간 소음 변화량 (dB)", -15, 10, 0, 1)

    st.markdown("---")
    st.markdown("### 🗺️ 지도 표시 지표")
    map_metric = st.selectbox(
        "지도 색상 기준",
        ["야간소음","스트레스","PSQI","수면시간"],
        index=0
    )

    st.markdown("---")
    st.markdown("""
    <div style='background:rgba(255,255,255,0.12); border-radius:8px; padding:12px; font-size:0.8rem; line-height:1.6;'>
    <b>📋 분석 개요</b><br>
    원자료: CSV 59건<br>
    자치구 분류: 시나리오 배치<br>
    회귀계수: 단순 선형 추정<br>
    <br>
    <b>기관:</b> 서울특별시<br>보건환경연구원<br>
    <b>작성:</b> 2026년 3월
    </div>
    """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 헤더
# ─────────────────────────────────────────────
st.markdown("""
<div class="report-header">
  <h1>🏙️ 서울시 지역 특성별 소음 노출과 건강 영향 분석 시스템</h1>
  <p>상권·교통·주거 시나리오와 서울 자치구 적용 | 보건환경연구원 정책 시뮬레이션 도구</p>
  <span class="badge">📅 2026년 3월</span>
  <span class="badge" style="margin-left:8px">🔬 분석 표본: 59건</span>
  <span class="badge" style="margin-left:8px">🗺️ 서울 25개 자치구</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 탭 구성
# ─────────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "🗺️ 자치구 지도 분석",
    "📊 건강 영향 시뮬레이션",
    "📈 지역 특성 비교",
    "🏛️ 정책 효과 분석",
    "📋 자치구 데이터 현황"
])

# ══════════════════════════════════════════════
# TAB 1: 지도 분석
# ══════════════════════════════════════════════
with tab1:
    col_map, col_info = st.columns([3, 2], gap="large")

    with col_map:
        st.markdown('<div class="section-title">🗺️ 서울 자치구 소음·건강 분포 지도</div>', unsafe_allow_html=True)
        st.caption("▶ 지도의 자치구를 클릭하면 우측에 상세 정보가 표시됩니다")

        geo = build_geojson(map_metric)

        metric_labels = {
            "야간소음": ("야간 평균 소음도", "dB", "Reds"),
            "스트레스": ("평균 스트레스 점수", "점", "Oranges"),
            "PSQI":    ("평균 수면 질 지수(PSQI)", "점", "Blues"),
            "수면시간": ("평균 수면시간", "시간", "Greens"),
        }
        m_label, m_unit, m_color = metric_labels[map_metric]

        # 색상 역전 (수면시간은 낮을수록 나쁨 → 역순)
        reverse = (map_metric == "수면시간")

        fig_map = px.choropleth_mapbox(
            pd.DataFrame([
                {
                    "자치구": name,
                    map_metric: GU_DATA[name][map_metric],
                    "유형": GU_DATA[name]["유형"],
                    "야간소음": GU_DATA[name]["야간소음"],
                    "스트레스": GU_DATA[name]["스트레스"],
                    "PSQI": GU_DATA[name]["PSQI"],
                    "수면시간": GU_DATA[name]["수면시간"],
                }
                for name in GU_DATA
                if name in [f["properties"]["name"] for f in geo["features"]]
            ]),
            geojson=geo,
            locations="자치구",
            featureidkey="properties.name",
            color=map_metric,
            color_continuous_scale=m_color + ("_r" if reverse else ""),
            mapbox_style="carto-positron",
            zoom=10.2,
            center={"lat": 37.5665, "lon": 126.9780},
            opacity=0.75,
            hover_name="자치구",
            hover_data={
                "유형": True,
                "야간소음": ":.1f",
                "스트레스": ":.1f",
                "PSQI": ":.1f",
                "수면시간": ":.2f",
                map_metric: False,
            },
            labels={
                "유형":"지역 특성",
                "야간소음":"야간소음(dB)",
                "스트레스":"스트레스",
                "PSQI":"PSQI",
                "수면시간":"수면시간(h)",
            },
            height=540,
        )
        fig_map.update_layout(
            margin={"r":0,"t":0,"l":0,"b":0},
            coloraxis_colorbar=dict(title=m_unit, thickness=14, len=0.6),
        )
        st.plotly_chart(fig_map, use_container_width=True)

    with col_info:
        st.markdown('<div class="section-title">📍 선택 자치구 상세 현황</div>', unsafe_allow_html=True)

        d = GU_DATA[selected_gu]
        유형 = d["유형"]
        color = TYPE_COLOR[유형]
        bg    = TYPE_COLOR_LIGHT[유형]

        st.markdown(f"""
        <div style='background:{bg}; border:2px solid {color}; border-radius:10px; padding:16px 18px; margin-bottom:14px;'>
          <div style='font-size:1.3rem; font-weight:800; color:{color};'>📍 {selected_gu}</div>
          <div style='font-size:0.85rem; color:#374151; margin-top:4px;'>
            지역 특성: <b>{유형}</b> &nbsp;|&nbsp; 분석 표본: {d['표본수']}건
          </div>
        </div>
        """, unsafe_allow_html=True)

        # 소음 게이지
        night = d["야간소음"]
        who_limit = 45.0
        gauge_pct = min(night / 80 * 100, 100)
        gauge_color = "#dc2626" if night >= 65 else "#d97706" if night >= 55 else "#16a34a"
        st.markdown(f"""
        <div style='background:white; border:1px solid #e2e8f0; border-radius:8px; padding:14px 16px; margin-bottom:12px;'>
          <div style='font-size:0.78rem; color:#64748b; font-weight:600; margin-bottom:6px;'>🔊 야간 평균 소음도</div>
          <div style='font-size:1.8rem; font-weight:800; color:{gauge_color};'>{night:.1f} <span style='font-size:1rem; font-weight:400;'>dB</span></div>
          <div style='background:#e2e8f0; border-radius:6px; height:8px; margin:8px 0;'>
            <div style='background:{gauge_color}; width:{gauge_pct:.0f}%; height:8px; border-radius:6px;'></div>
          </div>
          <div style='font-size:0.75rem; color:#94a3b8;'>WHO 권고 기준: 야간 {who_limit}dB 이하</div>
        </div>
        """, unsafe_allow_html=True)

        # 건강지표 카드
        metrics = [
            ("😰 스트레스 점수", d["스트레스"], "점", 40, "#dc2626"),
            ("💤 수면 질(PSQI)", d["PSQI"], "점", 15, "#7c3aed"),
            ("🛏️ 평균 수면시간", d["수면시간"], "시간", 9, "#0891b2"),
            ("⏰ 야간 각성 횟수", d["각성횟수"], "회", 7, "#d97706"),
        ]
        for label, val, unit, maxv, mc in metrics:
            pct = val / maxv * 100
            st.markdown(f"""
            <div style='background:white; border:1px solid #e2e8f0; border-radius:8px; padding:10px 14px; margin-bottom:8px; display:flex; align-items:center; gap:14px;'>
              <div style='flex:1;'>
                <div style='font-size:0.75rem; color:#64748b;'>{label}</div>
                <div style='font-size:1.25rem; font-weight:700; color:{mc};'>{val:.2f} <span style='font-size:0.8rem; font-weight:400; color:#94a3b8;'>{unit}</span></div>
              </div>
              <div style='width:52px; height:52px; position:relative;'>
                <svg viewBox="0 0 36 36" style='transform:rotate(-90deg);'>
                  <circle cx='18' cy='18' r='15.9' fill='none' stroke='#e2e8f0' stroke-width='3'/>
                  <circle cx='18' cy='18' r='15.9' fill='none' stroke='{mc}' stroke-width='3'
                    stroke-dasharray='{pct:.0f} 100' stroke-linecap='round'/>
                </svg>
              </div>
            </div>
            """, unsafe_allow_html=True)

        # 정책 권고
        st.markdown("---")
        if 유형 == "교통":
            st.markdown("""<div class='danger-box'>⚠️ <b>교통 지역 우선 대응</b><br>
            속도 제한(30km/h) 확대, 저소음 포장재 적용,
            화물차 야간운행 관리, 방음벽·방음창 지원 필요</div>""", unsafe_allow_html=True)
        elif 유형 == "상권":
            st.markdown("""<div class='warn-box'>📢 <b>상권 지역 심야 관리</b><br>
            심야 영업 소음 관리 기준 적용, 배달·오토바이
            저감 대책, 보행친화 가로 조성 권고</div>""", unsafe_allow_html=True)
        else:
            st.markdown("""<div class='success-box'>🏘️ <b>주거 지역 생활소음 관리</b><br>
            공동주택 차음성능 개선 지원, 야간 공사 시간
            제한, 생활소음 민원 집중 관리 권고</div>""", unsafe_allow_html=True)

        st.markdown(f"""
        <div class='info-box' style='margin-top:8px;'>
        ℹ️ 자치구 데이터는 보고서 시나리오 기반 분석 수치입니다.
        {'실측 표본 포함' if d['표본수'] > 0 else '시나리오 추정치 적용'}
        </div>
        """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 2: 건강 영향 시뮬레이션
# ══════════════════════════════════════════════
with tab2:
    d = GU_DATA[selected_gu]
    유형 = d["유형"]

    st.markdown(f'<div class="section-title">📊 {selected_gu} 소음 정책 시뮬레이션</div>', unsafe_allow_html=True)

    base_noise = d["야간소음"]
    new_noise  = base_noise + noise_change
    new_stress = d["스트레스"] + (noise_change * REGRESSION["스트레스"])
    new_psqi   = d["PSQI"]      + (noise_change * REGRESSION["PSQI"])
    new_sleep  = d["수면시간"] - (noise_change * abs(REGRESSION["수면시간"]))
    new_sleep  = max(0, new_sleep)

    # 소음 변화 배너
    arrow = "▼" if noise_change < 0 else "▲" if noise_change > 0 else "─"
    color_arrow = "#16a34a" if noise_change < 0 else "#dc2626" if noise_change > 0 else "#64748b"
    st.markdown(f"""
    <div style='background:linear-gradient(90deg,#1a3a5c,#2563a8); color:white; border-radius:10px;
    padding:18px 24px; margin-bottom:20px; display:flex; align-items:center; gap:20px;'>
      <div style='font-size:2.2rem;'>🔊</div>
      <div>
        <div style='font-size:0.82rem; opacity:0.8;'>야간 소음 변화 시뮬레이션</div>
        <div style='font-size:1.5rem; font-weight:800;'>
          {base_noise:.1f} dB &nbsp;
          <span style='color:#fcd34d;'>{arrow}</span>
          &nbsp; {new_noise:.1f} dB
          &nbsp;<span style='font-size:1rem; font-weight:400; opacity:0.75;'>({noise_change:+.0f} dB)</span>
        </div>
      </div>
      <div style='margin-left:auto; text-align:right; font-size:0.82rem; opacity:0.75;'>
        WHO 권고 기준<br><b style='font-size:1.1rem;'>45 dB 이하</b>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # KPI 비교
    col1, col2, col3 = st.columns(3)
    kpi_items = [
        (col1, "😰 스트레스 점수", d["스트레스"], new_stress, "점", True),
        (col2, "💤 수면 질(PSQI)", d["PSQI"], new_psqi, "점", True),
        (col3, "🛏️ 평균 수면시간", d["수면시간"], new_sleep, "시간", False),
    ]
    for col, label, base, new, unit, higher_is_bad in kpi_items:
        delta = new - base
        if higher_is_bad:
            delta_class = "kpi-delta-neg" if delta > 0 else "kpi-delta-pos" if delta < 0 else ""
        else:
            delta_class = "kpi-delta-pos" if delta > 0 else "kpi-delta-neg" if delta < 0 else ""
        sign = "+" if delta >= 0 else ""
        with col:
            st.markdown(f"""
            <div class='kpi-card'>
              <div class='kpi-label'>{label}</div>
              <div style='display:flex; align-items:baseline; justify-content:center; gap:8px; margin:6px 0;'>
                <div style='color:#94a3b8; font-size:1.1rem; font-weight:600;'>{base:.2f}</div>
                <div style='color:#64748b;'>→</div>
                <div class='kpi-value'>{new:.2f}</div>
              </div>
              <div class='kpi-unit'>{unit}</div>
              <div class='{delta_class}' style='margin-top:4px;'>{sign}{delta:.2f} {unit}</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 민감도 분석 그래프
    col_g1, col_g2 = st.columns(2, gap="large")

    with col_g1:
        st.markdown('<div class="section-title">야간 소음 변화에 따른 건강지표 추이</div>', unsafe_allow_html=True)
        noise_range = np.arange(base_noise - 15, base_noise + 11, 0.5)
        df_trend = pd.DataFrame({
            "야간소음(dB)": noise_range,
            "스트레스": d["스트레스"] + (noise_range - base_noise) * REGRESSION["스트레스"],
            "PSQI": d["PSQI"] + (noise_range - base_noise) * REGRESSION["PSQI"],
            "수면시간": d["수면시간"] - (noise_range - base_noise) * abs(REGRESSION["수면시간"]),
        })
        fig_trend = go.Figure()
        for col_name, color_line, dash in [
            ("스트레스","#dc2626","solid"),
            ("PSQI","#7c3aed","dash"),
            ("수면시간","#0891b2","dot"),
        ]:
            fig_trend.add_trace(go.Scatter(
                x=df_trend["야간소음(dB)"], y=df_trend[col_name],
                mode="lines", name=col_name,
                line=dict(color=color_line, width=2.5, dash=dash)
            ))
        fig_trend.add_vline(x=base_noise, line_dash="dash", line_color="#374151", annotation_text="현재")
        fig_trend.add_vline(x=new_noise,  line_dash="dot",  line_color="#2563a8", annotation_text="시뮬레이션")
        fig_trend.add_vline(x=45, line_color="#16a34a", line_width=1, annotation_text="WHO 기준")
        fig_trend.update_layout(
            height=340, margin=dict(l=10,r=10,t=20,b=10),
            xaxis_title="야간 소음(dB)", yaxis_title="지표값",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
            plot_bgcolor="white", paper_bgcolor="white",
        )
        fig_trend.update_xaxes(showgrid=True, gridcolor="#f1f5f9")
        fig_trend.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
        st.plotly_chart(fig_trend, use_container_width=True)

    with col_g2:
        st.markdown('<div class="section-title">현재 vs 시뮬레이션 건강지표 비교</div>', unsafe_allow_html=True)
        categories = ["스트레스(정규화)", "PSQI(정규화)", "수면시간(역정규화)"]
        # 정규화 (max 기준)
        def norm(val, mx): return val / mx * 100
        fig_radar = go.Figure()
        fig_radar.add_trace(go.Bar(
            name="현재",
            x=["스트레스","PSQI","수면시간"],
            y=[d["스트레스"], d["PSQI"], d["수면시간"]],
            marker_color="#94a3b8",
        ))
        fig_radar.add_trace(go.Bar(
            name="시뮬레이션",
            x=["스트레스","PSQI","수면시간"],
            y=[new_stress, new_psqi, new_sleep],
            marker_color=["#dc2626","#7c3aed","#0891b2"],
        ))
        fig_radar.update_layout(
            barmode="group", height=340,
            margin=dict(l=10,r=10,t=20,b=10),
            legend=dict(orientation="h", yanchor="bottom", y=1.02),
            plot_bgcolor="white", paper_bgcolor="white",
        )
        fig_radar.update_yaxes(showgrid=True, gridcolor="#f1f5f9")
        st.plotly_chart(fig_radar, use_container_width=True)

    # 해석 텍스트
    if noise_change < 0:
        st.markdown(f"""<div class='success-box'>
        ✅ <b>저감 효과 분석:</b> 야간 소음이 {abs(noise_change)}dB 감소할 경우,
        스트레스 점수 <b>{abs(d['스트레스']-new_stress):.2f}점</b> 완화,
        수면 질(PSQI) <b>{abs(d['PSQI']-new_psqi):.2f}점</b> 개선,
        수면시간 <b>{abs(d['수면시간']-new_sleep):.3f}시간</b> 회복이 예상됩니다.
        단순 회귀 추정치이므로 참고용으로 활용하십시오.
        </div>""", unsafe_allow_html=True)
    elif noise_change > 0:
        st.markdown(f"""<div class='danger-box'>
        ⚠️ <b>소음 증가 영향:</b> 야간 소음이 {noise_change}dB 상승할 경우,
        스트레스 점수 <b>{abs(d['스트레스']-new_stress):.2f}점</b> 악화,
        수면 질(PSQI) <b>{abs(d['PSQI']-new_psqi):.2f}점</b> 저하,
        수면시간 <b>{abs(d['수면시간']-new_sleep):.3f}시간</b> 감소가 예상됩니다.
        </div>""", unsafe_allow_html=True)
    else:
        st.markdown("""<div class='info-box'>
        ℹ️ 슬라이더를 조작하여 야간 소음 변화에 따른 건강지표 변화를 시뮬레이션하십시오.
        </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 3: 지역 특성 비교
# ══════════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-title">📈 서울 자치구별 소음·건강지표 비교 분석</div>', unsafe_allow_html=True)

    df_all = pd.DataFrame([
        {"자치구": k, **v} for k, v in GU_DATA.items()
    ])

    col_c1, col_c2 = st.columns(2, gap="large")
    with col_c1:
        st.markdown('<div class="section-title">자치구별 야간 소음도 비교</div>', unsafe_allow_html=True)
        df_sorted = df_all.sort_values("야간소음", ascending=True)
        bar_colors = [TYPE_COLOR[t] for t in df_sorted["유형"]]
        fig_bar = go.Figure(go.Bar(
            x=df_sorted["야간소음"], y=df_sorted["자치구"],
            orientation="h",
            marker_color=bar_colors,
            text=df_sorted["야간소음"].apply(lambda x: f"{x:.1f}"),
            textposition="outside",
        ))
        fig_bar.add_vline(x=45, line_dash="dash", line_color="#16a34a",
                          annotation_text="WHO 기준(45dB)", annotation_position="top right")
        fig_bar.update_layout(
            height=600, margin=dict(l=0,r=40,t=10,b=10),
            xaxis_title="야간 소음(dB)",
            plot_bgcolor="white", paper_bgcolor="white",
        )
        fig_bar.update_xaxes(showgrid=True, gridcolor="#f1f5f9")
        st.plotly_chart(fig_bar, use_container_width=True)

    with col_c2:
        st.markdown('<div class="section-title">야간소음 vs 수면시간 산점도</div>', unsafe_allow_html=True)
        fig_scatter = px.scatter(
            df_all, x="야간소음", y="수면시간",
            color="유형",
            color_discrete_map=TYPE_COLOR,
            size="스트레스",
            hover_name="자치구",
            hover_data={"PSQI":":.1f", "각성횟수":":.1f"},
            labels={"야간소음":"야간 소음(dB)", "수면시간":"평균 수면시간(h)", "유형":"지역 특성"},
            height=300,
        )
        # 회귀선
        x_fit = np.linspace(df_all["야간소음"].min(), df_all["야간소음"].max(), 50)
        m, b = np.polyfit(df_all["야간소음"], df_all["수면시간"], 1)
        fig_scatter.add_trace(go.Scatter(
            x=x_fit, y=m * x_fit + b,
            mode="lines", name="추세선",
            line=dict(color="#374151", dash="dash", width=1.5)
        ))
        fig_scatter.add_hline(y=7, line_dash="dot", line_color="#16a34a",
                              annotation_text="권장 수면(7h)")
        fig_scatter.update_layout(
            margin=dict(l=10,r=10,t=10,b=10),
            plot_bgcolor="white", paper_bgcolor="white",
        )
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.markdown('<div class="section-title">지역 특성별 건강지표 박스플롯</div>', unsafe_allow_html=True)
        metric_sel = st.selectbox("지표 선택", ["스트레스","PSQI","수면시간","각성횟수"])
        fig_box = px.box(
            df_all, x="유형", y=metric_sel,
            color="유형", color_discrete_map=TYPE_COLOR,
            points="all", hover_name="자치구",
            height=260,
            labels={"유형":"지역 특성", metric_sel: metric_sel},
        )
        fig_box.update_layout(
            margin=dict(l=10,r=10,t=10,b=10), showlegend=False,
            plot_bgcolor="white", paper_bgcolor="white",
        )
        st.plotly_chart(fig_box, use_container_width=True)

    # 상관관계 히트맵
    st.markdown('<div class="section-title">소음·건강지표 상관관계 분석</div>', unsafe_allow_html=True)
    corr_cols = ["야간소음","주간소음","스트레스","PSQI","수면시간","각성횟수"]
    corr_df = df_all[corr_cols].corr()
    fig_heat = px.imshow(
        corr_df,
        text_auto=".2f",
        color_continuous_scale="RdBu_r",
        zmin=-1, zmax=1,
        height=380,
    )
    fig_heat.update_layout(margin=dict(l=10,r=10,t=10,b=10))
    st.plotly_chart(fig_heat, use_container_width=True)
    st.markdown("""<div class='info-box'>
    📊 야간 소음과 스트레스(+), PSQI(+), 각성횟수(+)는 강한 양(+)의 상관관계를 보이며,
    수면시간과는 음(-)의 상관관계를 나타냅니다. 단순 회귀 계수: 야간소음 1dB ↑ →
    스트레스 +0.48점, PSQI +0.20점, 수면시간 -0.053시간.
    </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 4: 정책 효과 분석
# ══════════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-title">🏛️ 정책 패키지 적용 후 기대 효과 분석</div>', unsafe_allow_html=True)
    st.markdown("""<div class='info-box'>
    ⚙️ <b>정책 저감 시나리오:</b> 교통지역 -9dB, 상권지역 -5dB, 주거지역 -3dB 적용
    (단순 회귀 추정치 기반 — 참고용 시나리오이며 실제 사후평가가 필요합니다)
    </div>""", unsafe_allow_html=True)

    # 정책 전후 데이터 생성
    policy_rows = []
    for gu, d in GU_DATA.items():
        유형 = d["유형"]
        reduction = POLICY_REDUCTION[유형]
        policy_rows.append({
            "자치구": gu, "유형": 유형,
            "현재_야간소음": d["야간소음"],
            "정책후_야간소음": d["야간소음"] + reduction,
            "현재_스트레스": d["스트레스"],
            "정책후_스트레스": d["스트레스"] + reduction * REGRESSION["스트레스"],
            "현재_수면시간": d["수면시간"],
            "정책후_수면시간": d["수면시간"] - reduction * abs(REGRESSION["수면시간"]),
            "현재_PSQI": d["PSQI"],
            "정책후_PSQI": d["PSQI"] + reduction * REGRESSION["PSQI"],
        })
    df_policy = pd.DataFrame(policy_rows)

    col_p1, col_p2 = st.columns(2, gap="large")
    with col_p1:
        st.markdown('<div class="section-title">정책 전후 야간소음 변화</div>', unsafe_allow_html=True)
        df_ps = df_policy.sort_values("현재_야간소음", ascending=True)
        fig_policy = go.Figure()
        fig_policy.add_trace(go.Bar(
            y=df_ps["자치구"], x=df_ps["현재_야간소음"],
            name="현재", orientation="h", marker_color="#94a3b8"
        ))
        fig_policy.add_trace(go.Bar(
            y=df_ps["자치구"], x=df_ps["정책후_야간소음"],
            name="정책 후", orientation="h",
            marker_color=[TYPE_COLOR[t] for t in df_ps["유형"]]
        ))
        fig_policy.add_vline(x=45, line_dash="dash", line_color="#16a34a",
                             annotation_text="WHO 기준")
        fig_policy.update_layout(
            barmode="overlay", height=600,
            margin=dict(l=0,r=10,t=10,b=10),
            xaxis_title="야간 소음(dB)",
            legend=dict(orientation="h"),
            plot_bgcolor="white", paper_bgcolor="white",
        )
        fig_policy.update_xaxes(showgrid=True, gridcolor="#f1f5f9")
        st.plotly_chart(fig_policy, use_container_width=True)

    with col_p2:
        st.markdown('<div class="section-title">지역 특성별 정책 전후 비교</div>', unsafe_allow_html=True)

        type_summary = []
        for t in ["교통","상권","주거"]:
            sub = df_policy[df_policy["유형"] == t]
            type_summary.append({
                "유형": t,
                "야간소음 현재": sub["현재_야간소음"].mean(),
                "야간소음 개선": sub["정책후_야간소음"].mean(),
                "스트레스 현재": sub["현재_스트레스"].mean(),
                "스트레스 개선": sub["정책후_스트레스"].mean(),
                "수면시간 현재": sub["현재_수면시간"].mean(),
                "수면시간 개선": sub["정책후_수면시간"].mean(),
            })
        df_ts = pd.DataFrame(type_summary)

        fig_comp = go.Figure()
        x_cats = ["교통","상권","주거"]
        for col_name, col_cur, col_aft, bar_color in [
            ("야간소음(dB)", "야간소음 현재", "야간소음 개선", "#94a3b8"),
            ("스트레스", "스트레스 현재", "스트레스 개선", "#fca5a5"),
            ("수면시간(h)", "수면시간 현재", "수면시간 개선", "#6ee7b7"),
        ]:
            pass
        # 멀티지표 비교 테이블
        st.markdown("""
        <table class='data-table' style='margin-bottom:12px;'>
          <thead><tr>
            <th>지역</th><th>야간소음<br>현재→개선</th><th>스트레스<br>현재→개선</th><th>수면시간<br>현재→개선</th>
          </tr></thead>
          <tbody>
        """, unsafe_allow_html=True)
        for _, row in df_ts.iterrows():
            t = row["유형"]
            tag = f"<span class='tag-{'traffic' if t=='교통' else 'commercial' if t=='상권' else 'residential'}'>{t}</span>"
            st.markdown(f"""
            <tr>
              <td>{tag}</td>
              <td>{row['야간소음 현재']:.1f} → <b>{row['야간소음 개선']:.1f}</b> dB</td>
              <td>{row['스트레스 현재']:.1f} → <b>{row['스트레스 개선']:.1f}</b></td>
              <td>{row['수면시간 현재']:.2f} → <b>{row['수면시간 개선']:.2f}</b> h</td>
            </tr>
            """, unsafe_allow_html=True)
        st.markdown("</tbody></table>", unsafe_allow_html=True)

        # 감소량 강조
        for t_name, r in zip(["교통","상권","주거"], POLICY_REDUCTION.values()):
            sub = df_policy[df_policy["유형"] == t_name]
            stress_improve = abs((sub["현재_스트레스"] - sub["정책후_스트레스"]).mean())
            sleep_improve  = abs((sub["정책후_수면시간"] - sub["현재_수면시간"]).mean())
            color_map = {"교통":"danger-box","상권":"warn-box","주거":"success-box"}
            st.markdown(f"""<div class='{color_map[t_name]}' style='margin-bottom:8px;'>
            <b>{t_name} 지역</b> ({r:+.0f}dB 저감 목표):
            스트레스 <b>{stress_improve:.2f}점</b> 완화,
            수면시간 <b>{sleep_improve:.3f}시간</b> 회복 기대
            </div>""", unsafe_allow_html=True)

        # 해외 사례
        st.markdown('<div class="section-title">🌍 해외 정책 성공 사례</div>', unsafe_allow_html=True)
        cases = [
            ("🇪🇸 바르셀로나","슈퍼블록 프로그램","차량 재배치·보행공간 확대","보행자 전용화 1년 후 평균 소음 3.1dB 감소"),
            ("🇫🇷 파리","도심 30km/h 제한","도심 다수 도로 속도 하향","소음 저감을 정책 목적으로 명시"),
            ("🌐 WHO/EEA","건강 기반 기준","야간 45dB 이하 권고","만성 소음의 수면·심혈관 부담 제시"),
        ]
        for flag, policy, detail, effect in cases:
            st.markdown(f"""
            <div style='background:white; border:1px solid #e2e8f0; border-radius:8px;
            padding:10px 14px; margin-bottom:8px; border-left:4px solid #2563a8;'>
              <div style='font-weight:700; font-size:0.9rem;'>{flag} {policy}</div>
              <div style='color:#374151; font-size:0.82rem; margin-top:2px;'>{detail}</div>
              <div style='color:#2563a8; font-size:0.8rem; margin-top:4px;'>→ {effect}</div>
            </div>
            """, unsafe_allow_html=True)


# ══════════════════════════════════════════════
# TAB 5: 자치구 데이터 현황
# ══════════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-title">📋 서울 자치구 소음·건강 데이터 현황표</div>', unsafe_allow_html=True)
    st.markdown("""<div class='info-box' style='margin-bottom:12px;'>
    ℹ️ 자치구 데이터는 원자료(CSV 59건)의 지역 특성 재분류 및 보고서 시나리오를 기반으로 구성되었습니다.
    표본수 0은 시나리오 추정 자치구입니다.
    </div>""", unsafe_allow_html=True)

    # 필터
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        type_filter = st.multiselect("지역 특성 필터", ["교통","상권","주거"], default=["교통","상권","주거"])
    with col_f2:
        noise_filter = st.slider("야간 소음 범위(dB)", 40.0, 75.0, (40.0, 75.0), 0.5)

    df_show = pd.DataFrame([{"자치구": k, **v} for k, v in GU_DATA.items()])
    df_show = df_show[
        (df_show["유형"].isin(type_filter)) &
        (df_show["야간소음"] >= noise_filter[0]) &
        (df_show["야간소음"] <= noise_filter[1])
    ].sort_values("야간소음", ascending=False)

    st.markdown("""
    <table class='data-table'>
    <thead><tr>
      <th>자치구</th><th>지역 특성</th><th>표본수</th>
      <th>주간소음(dB)</th><th>야간소음(dB)</th>
      <th>스트레스</th><th>PSQI</th>
      <th>수면시간(h)</th><th>각성횟수</th>
    </tr></thead><tbody>
    """, unsafe_allow_html=True)

    for _, row in df_show.iterrows():
        t = row["유형"]
        tag_class = "tag-traffic" if t=="교통" else "tag-commercial" if t=="상권" else "tag-residential"
        noise_bar_w = int(row["야간소음"] / 80 * 80)
        noise_c = "#dc2626" if row["야간소음"] >= 65 else "#d97706" if row["야간소음"] >= 55 else "#16a34a"
        st.markdown(f"""<tr>
          <td><b>{row['자치구']}</b></td>
          <td><span class='{tag_class}'>{t}</span></td>
          <td>{int(row['표본수'])}</td>
          <td>{row['주간소음']:.1f}</td>
          <td>
            <div style='display:flex; align-items:center; gap:6px;'>
              <div style='background:#e2e8f0; border-radius:4px; width:60px; height:8px;'>
                <div style='background:{noise_c}; width:{noise_bar_w}%; height:8px; border-radius:4px;'></div>
              </div>
              <span>{row['야간소음']:.1f}</span>
            </div>
          </td>
          <td>{row['스트레스']:.1f}</td>
          <td>{row['PSQI']:.1f}</td>
          <td>{row['수면시간']:.2f}</td>
          <td>{row['각성횟수']:.1f}</td>
        </tr>""", unsafe_allow_html=True)

    st.markdown("</tbody></table>", unsafe_allow_html=True)

    st.markdown(f"<br><div style='color:#64748b; font-size:0.82rem;'>📊 표시 자치구: {len(df_show)}개</div>", unsafe_allow_html=True)

    # 요약 통계
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">지역 특성별 요약 통계</div>', unsafe_allow_html=True)
    col_s1, col_s2, col_s3 = st.columns(3)
    for col_stat, type_name, type_tag in [
        (col_s1, "교통", "tag-traffic"),
        (col_s2, "상권", "tag-commercial"),
        (col_s3, "주거", "tag-residential"),
    ]:
        sub = df_all = pd.DataFrame([{"자치구": k, **v} for k, v in GU_DATA.items()])
        sub = sub[sub["유형"] == type_name]
        with col_stat:
            st.markdown(f"""
            <div style='background:white; border:1px solid #e2e8f0; border-radius:10px; padding:16px;'>
              <div style='margin-bottom:10px;'><span class='{type_tag}'>{type_name} 지역</span>
              <span style='color:#64748b; font-size:0.78rem; margin-left:8px;'>{len(sub)}개 자치구</span></div>
              <table style='width:100%; font-size:0.83rem;'>
                <tr><td style='color:#64748b;'>야간소음 평균</td><td style='font-weight:700; text-align:right;'>{sub['야간소음'].mean():.1f} dB</td></tr>
                <tr><td style='color:#64748b;'>스트레스 평균</td><td style='font-weight:700; text-align:right;'>{sub['스트레스'].mean():.1f} 점</td></tr>
                <tr><td style='color:#64748b;'>수면시간 평균</td><td style='font-weight:700; text-align:right;'>{sub['수면시간'].mean():.2f} h</td></tr>
                <tr><td style='color:#64748b;'>PSQI 평균</td><td style='font-weight:700; text-align:right;'>{sub['PSQI'].mean():.1f} 점</td></tr>
              </table>
            </div>
            """, unsafe_allow_html=True)

# ─────────────────────────────────────────────
# 하단 푸터
# ─────────────────────────────────────────────
st.markdown("<br>", unsafe_allow_html=True)
st.markdown("""
<div style='background:#1a3a5c; color:rgba(255,255,255,0.75); padding:16px 24px;
border-radius:10px; font-size:0.78rem; display:flex; justify-content:space-between;'>
  <div>
    <b style='color:white;'>서울특별시 보건환경연구원</b> | 소음·건강 영향 분석 시스템<br>
    본 시스템은 연구·정책 검토용 분석 도구입니다. 자치구 배치는 시나리오 기반입니다.
  </div>
  <div style='text-align:right;'>
    분석 기준: CSV 59건 | 2026년 3월<br>
    참고: WHO Environmental Noise Guidelines 2018
  </div>
</div>
""", unsafe_allow_html=True)

st.write("""
- 야간 소음은 스트레스 증가와 수면 감소에 직접적인 영향을 미침
- 교통지역에서 건강 영향이 가장 크게 나타남
- 소음 저감 정책은 수면 개선 및 스트레스 완화 효과 기대 가능
""")
