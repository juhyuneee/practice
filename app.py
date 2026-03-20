import streamlit as st

st.set_page_config(page_title="퍼스널 컬러 추천", layout="centered")

st.title("💄 퍼스널 컬러 기반 화장품 추천")

# -------------------------
# 제품 데이터 (국내 구매 가능 / 단종 제외)
# -------------------------
products = {
    # 립
    "롬앤 쥬시 래스팅 틴트 07 쥬쥬브": {"tone": "warm", "chroma": 3, "category": "lip"},
    "롬앤 쥬시 래스팅 틴트 06 피그피그": {"tone": "cool", "chroma": 2, "category": "lip"},
    "페리페라 잉크 무드 글로이 틴트 03 맘찍로즈": {"tone": "cool", "chroma": 2, "category": "lip"},
    "페리페라 잉크 벨벳 17 로즈누드": {"tone": "cool", "chroma": 3, "category": "lip"},

    # 블러셔
    "롬앤 베러 댄 치크 피치칩": {"tone": "warm", "chroma": 2, "category": "blusher"},
    "3CE 무드 레시피 블러셔 누드피치": {"tone": "warm", "chroma": 1, "category": "blusher"},
    "에뛰드 러블리 쿠키 블러셔 핑크": {"tone": "cool", "chroma": 3, "category": "blusher"},

    # 섀도우
    "클리오 프로 아이 팔레트 02 브라운슈": {"tone": "warm", "chroma": 2, "category": "shadow"},
    "롬앤 베러 댄 아이즈 드라이로즈": {"tone": "cool", "chroma": 1, "category": "shadow"},
}

product_list = list(products.keys())

# -------------------------
# 분석 함수
# -------------------------
def analyze(lst, weight):
    tone_score = 0
    chroma_score = 0
    count = 0

    for p in lst:
        if p in products:
            tone_score += (1 if products[p]["tone"] == "warm" else -1) * weight
            chroma_score += products[p]["chroma"] * weight
            count += abs(weight)

    if count == 0:
        return 0, 0

    return tone_score / count, chroma_score / count


def get_personal_color(tone, chroma):
    if tone >= 0:
        return "봄 웜톤 🌸" if chroma >= 2 else "가을 웜톤 🍂"
    else:
        return "겨울 쿨톤 ❄️" if chroma >= 2 else "여름 쿨톤 🌊"


def recommend_products(tone_type):
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
# UI (key 추가로 충돌 방지)
# -------------------------
st.subheader("1️⃣ 잘 맞았던 제품 (최대 3개)")
good = st.multiselect("잘 맞았던 제품 선택", product_list, max_selections=3, key="good")

st.subheader("2️⃣ 안 맞았던 제품 (선택)")
bad = st.multiselect("안 맞았던 제품 선택", product_list, max_selections=3, key="bad")

st.subheader("3️⃣ 반응 좋았던 제품 (선택)")
best = st.multiselect("반응 좋았던 제품 선택", product_list, max_selections=3, key="best")


# -------------------------
# 실행
# -------------------------
if st.button("🔍 퍼스널 컬러 분석"):

    if len(good) == 0:
        st.warning("👉 최소 1개 이상의 '잘 맞았던 제품'을 선택해주세요")
    else:
        t1, c1 = analyze(good, 1)
        t2, c2 = analyze(best, 2)
        t3, c3 = analyze(bad, -1)

        tone = t1 + t2 + t3
        chroma = c1 + c2 + c3

        result = get_personal_color(tone, chroma)
        tone_type = "warm" if tone >= 0 else "cool"

        st.success(f"🎯 당신의 퍼스널 컬러: {result}")

        lips, blushers = recommend_products(tone_type)

        st.subheader("💄 추천 립")
        for l in lips:
            st.write("✔️", l)

        st.subheader("🌸 추천 블러셔 (립과 조합)")
        for b in blushers:
            st.write("✔️", b)

        st.info(f"""
        📊 분석 결과  
        - 톤 점수: {round(tone,2)}  
        - 채도 점수: {round(chroma,2)}  

        👉 선택한 제품들의 색감 기반으로 분석되었습니다.
        """)
