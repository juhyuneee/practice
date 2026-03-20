from flask import Flask, request, render_template_string

app = Flask(__name__)

# -------------------------
# 제품 데이터 (확장 가능)
# -------------------------
products = {
    # 립
    "롬앤 쥬시 래스팅 틴트 07": {"tone": "warm", "chroma": 3, "category": "lip", "status": "판매중"},
    "롬앤 쥬시 래스팅 틴트 06": {"tone": "warm", "chroma": 2, "category": "lip", "status": "판매중"},
    "페리페라 잉크 무드 글로이 틴트 03": {"tone": "cool", "chroma": 2, "category": "lip", "status": "판매중"},
    "페리페라 잉크 벨벳 17": {"tone": "cool", "chroma": 3, "category": "lip", "status": "판매중"},

    # 블러셔
    "3CE 누드피치": {"tone": "warm", "chroma": 1, "category": "blusher", "status": "판매중"},
    "롬앤 베러 댄 치크 피치칩": {"tone": "warm", "chroma": 2, "category": "blusher", "status": "판매중"},
    "에뛰드 러블리 쿠키 블러셔 핑크": {"tone": "cool", "chroma": 3, "category": "blusher", "status": "판매중"},

    # 섀도우
    "클리오 프로 아이 팔레트 02": {"tone": "warm", "chroma": 2, "category": "shadow", "status": "판매중"},
    "롬앤 드라이로즈": {"tone": "cool", "chroma": 1, "category": "shadow", "status": "판매중"},
}

# -------------------------
# 분석 함수
# -------------------------
def analyze(product_list, weight=1):
    tone_score = 0
    chroma_score = 0
    count = 0

    for p in product_list:
        if p and p in products:
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


# -------------------------
# 추천 로직
# -------------------------
def recommend_set(tone_type):
    lips = []
    blushers = []

    for name, data in products.items():
        if data["status"] != "판매중":
            continue
        if data["tone"] == tone_type:
            if data["category"] == "lip":
                lips.append(name)
            elif data["category"] == "blusher":
                blushers.append(name)

    return lips[:3], blushers[:3]


# -------------------------
# UI
# -------------------------
HTML = """
<h2>퍼스널 컬러 진단 (제품 기반)</h2>

<form method="post">

<h3>잘 맞았던 제품</h3>
<select name="good1"><option value="">선택</option>{% for p in products %}<option>{{p}}</option>{% endfor %}</select><br>
<select name="good2"><option value="">선택</option>{% for p in products %}<option>{{p}}</option>{% endfor %}</select><br>
<select name="good3"><option value="">선택</option>{% for p in products %}<option>{{p}}</option>{% endfor %}</select><br>

<h3>안 맞았던 제품 (선택)</h3>
<select name="bad1"><option value="">선택</option>{% for p in products %}<option>{{p}}</option>{% endfor %}</select><br>

<h3>반응 좋았던 제품 (선택)</h3>
<select name="best1"><option value="">선택</option>{% for p in products %}<option>{{p}}</option>{% endfor %}</select><br><br>

<button type="submit">분석하기</button>
</form>

{% if result %}
<hr>
<h2>🎯 결과: {{ result }}</h2>

<h3>💄 립 추천</h3>
<ul>{% for l in lips %}<li>{{l}}</li>{% endfor %}</ul>

<h3>🌸 블러셔 추천 (립과 조합)</h3>
<ul>{% for b in blushers %}<li>{{b}}</li>{% endfor %}</ul>
{% endif %}
"""

# -------------------------
# 라우트
# -------------------------
@app.route("/", methods=["GET", "POST"])
def home():
    result = None
    lips = []
    blushers = []

    if request.method == "POST":
        good = [request.form.get("good1"), request.form.get("good2"), request.form.get("good3")]
        bad = [request.form.get("bad1")]
        best = [request.form.get("best1")]

        t1, c1 = analyze(good, 1)
        t2, c2 = analyze(best, 2)
        t3, c3 = analyze(bad, -1)

        tone = t1 + t2 + t3
        chroma = c1 + c2 + c3

        result = determine_pc(tone, chroma)
        tone_type = "warm" if tone >= 0 else "cool"

        lips, blushers = recommend_set(tone_type)

    return render_template_string(HTML, products=products.keys(), result=result, lips=lips, blushers=blushers)


if __name__ == "__main__":
    app.run(debug=True)
