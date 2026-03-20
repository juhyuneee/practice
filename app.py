import streamlit as st

st.title("퍼스널 컬러 진단 (제품 기반)")

# -------------------------
# 제품 데이터
# -------------------------
products = {
    "롬앤 쥬시 래스팅 틴트 07": {"tone": "warm", "chroma": 3, "category": "lip"},
    "롬앤 쥬시 래스팅 틴트 06": {"tone": "warm", "chroma": 2, "category": "lip"},
    "페리페라 잉크 무드 글로이 틴트 03": {"tone": "cool", "chroma": 2, "category": "lip"},
    "페리페라 잉크 벨벳 17": {"tone": "cool", "chroma": 3, "category": "lip"},
    "3CE 누드피치": {"tone": "warm", "chroma": 1, "category": "blusher"},
    "롬앤 베러 댄 치크 피치칩": {"tone": "warm", "chroma": 2, "category": "blusher"},
    "에뛰드 쿠키 블러셔 핑크": {"tone": "cool", "chroma": 3, "category": "blusher"},
}

# -------------------------
# 분석 함수
# -------------------------
def analyze(product_list, weight=1):
    tone_score = 0
    chroma_score = 0
    count = 0

    for p in product_list:
        if p in products:
            data = products[p]
            tone_score += (1 if data["tone"] == "warm" else -1) * weight
            chroma_score += data["chroma"] * weight
            count += weight

    if count == 0:
        return 0, 0

    return tone_score / count, chroma_score / count


def determine_pc(tone, chroma):
    if tone >= 0:
        return "봄 웜톤" if chroma >= 2 else "가을 웜톤"
    else:
        return "겨울 쿨톤" if chroma >= 2 else "여름 쿨톤"


def recommend(tone_type):
    lips = []
    blushers = []

    for name, data in products.items():
        if data["tone"] == tone_type:
            if data["category"] == "lip":
                lips.append(name)
            elif data["category"] == "blusher":
                blushers.append(name)

    return lips[:3], blushers[:3]


# -------------------------
# UI
# -------------------------
product_list = list(products.keys())

st.subheader("잘 맞았던 제품")
good = st.multiselect("3개 선택", product_list)

st.subheader("안 맞았던 제품")
bad = st.multiselect("선택", product_list)

st.subheader("반응 좋았던 제품")
best = st.multiselect("선택", product_list)

if st.button("분석하기"):

    t1, c1 = analyze(good, 1)
    t2, c2 = analyze(best, 2)
    t3, c3 = analyze(bad, -1)

    tone = t1 + t2 + t3
    chroma = c1 + c2 + c3

    result = determine_pc(tone, chroma)
    tone_type = "warm" if tone >= 0 else "cool"

    lips, blushers = recommend(tone_type)

    st.success(f"🎯 결과: {result}")

    st.subheader("💄 립 추천")
    st.write(lips)

    st.subheader("🌸 블러셔 추천")
    st.write(blushers)
