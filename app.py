import streamlit as st
import random

# -------------------------
# 페이지 설정
# -------------------------
st.set_page_config(page_title="퍼스널 컬러 추천", layout="centered")

# -------------------------
# CSS (화사한 UI)
# -------------------------
st.markdown("""
<style>
.stApp {
    background: linear-gradient(135deg, #fff0f5, #f0f8ff);
}
.block-container {
    padding-top: 2rem;
}
h1 {
    color: #ff4b6e;
}
div[data-testid="stButton"] > button {
    background-color: #ff4b6e;
    color: white;
    border-radius: 10px;
    height: 3em;
}
</style>
""", unsafe_allow_html=True)

st.title("💄 퍼스널 컬러 추천 서비스")

# -------------------------
# 데이터 생성 (100개 이상)
# -------------------------
brands = ["롬앤", "페리페라", "에뛰드", "3CE", "클리오"]
categories = ["lip", "blusher", "shadow"]

products = {}

for i in range(120):
    name = f"{random.choice(brands)} 제품{i}"
    products[name] = {
        "tone": random.choice(["warm", "cool"]),
        "chroma": random.randint(1, 3),
        "category": random.choice(categories)
    }

product_list = list(products.keys())

# -------------------------
# 분석 함수
# -------------------------
def analyze(lst, weight):
    tone_score, chroma_score, count = 0, 0, 0
    for p in lst:
        if p in products:
            tone_score += (1 if products[p]["tone"] == "warm" else -1) * weight
            chroma_score += products[p]["chroma"] * weight
            count += abs(weight)
    if count == 0:
        return 0, 0
    return tone_score / count, chroma_score / count

def get_pc(tone, chroma):
    if tone >= 0:
        return "봄 웜톤 🌸" if chroma >= 2 else "가을 웜톤 🍂"
    else:
        return "겨울 쿨톤 ❄️" if chroma >= 2 else "여름 쿨톤 🌊"

def recommend(tone_type):
    lips, blushers = [], []
    for name, data in products.items():
        if data["tone"] == tone_type:
            if data["category"] == "lip":
                lips.append(name)
            elif data["category"] == "blusher":
                blushers.append(name)
    return lips[:10], blushers[:10]

# -------------------------
# UI
# -------------------------
st.subheader("💡 사용해본 제품 선택")

col1, col2, col3 = st.columns(3)

with col1:
    good = st.multiselect("👍 잘 맞았던", product_list, max_selections=3, key="good")

with col2:
    bad = st.multiselect("👎 안 맞았던", product_list, max_selections=3, key="bad")

with col3:
    best = st.multiselect("🔥 반응 좋았던", product_list, max_selections=3, key="best")

# -------------------------
# 실행
# -------------------------
if st.button("✨ 퍼스널 컬러 분석하기"):

    if len(good) == 0:
        st.warning("최소 1개는 선택해주세요!")
    else:
        t1, c1 = analyze(good, 1)
        t2, c2 = analyze(best, 2)
        t3, c3 = analyze(bad, -1)

        tone = t1 + t2 + t3
        chroma = c1 + c2 + c3

        result = get_pc(tone, chroma)
        tone_type = "warm" if tone >= 0 else "cool"

        st.success(f"🎯 당신의 퍼스널 컬러: {result}")

        lips, blushers = recommend(tone_type)

        st.subheader("💄 추천 립")
        st.write(lips)

        st.subheader("🌸 추천 블러셔 (조합 추천)")
        st.write(blushers)

        st.info(f"톤 점수: {round(tone,2)} / 채도 점수: {round(chroma,2)}")
