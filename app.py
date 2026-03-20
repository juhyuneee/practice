from flask import Flask, request, render_template_string
import numpy as np

app = Flask(__name__)

# -------------------------
# 제품 데이터 (국내 구매 가능 + 단종 제외)
# -------------------------
products = {
    "롬앤 쥬시 래스팅 틴트 07": {"tone": "warm", "chroma": "high", "value": "mid", "category": "lip", "status": "판매중"},
    "페리페라 잉크 무드 글로이 틴트 03": {"tone": "cool", "chroma": "mid", "value": "high", "category": "lip", "status": "판매중"},
    "3CE 무드 레시피 블러셔 누드피치": {"tone": "warm", "chroma": "low", "value": "mid", "category": "blusher", "status": "판매중"},
    "롬앤 베러 댄 아이즈 드라이로즈": {"tone": "cool", "chroma": "low", "value": "mid", "category": "shadow", "status": "판매중"},
    "클리오 프로 아이 팔레트 02": {"tone": "warm", "chroma": "mid", "value": "mid", "category": "shadow", "status": "판매중"},
    "에뛰드 하트팝 블러셔 핑크": {"tone": "cool", "chroma": "high", "value": "high", "category": "blusher", "status": "판매중"},
}

# -------------------------
# 점수 변환
# -------------------------
tone_map = {"warm": 1, "cool": -1}
chroma_map = {"low": 1, "mid": 2, "high": 3}
value_map = {"low": 1, "mid": 2, "high": 3}


def analyze(products_list, weight=1):
    tone_score, chroma_score, value_score = 0, 0, 0
    count = 0

    for p in products_list:
        if p in products:
            data = products[p]
            tone_score += tone_map[data["tone"]] * weight
            chroma_score += chroma_map[data["chroma"]] * weight
            value_score += value_map[data["value"]] * weight
            count += weight

    if count == 0:
        return 0, 0, 0

    return tone_score / count, chroma_score / count, value_score / count


def determine_personal_color(tone, chroma):
    if tone > 0:
        if chroma >= 2:
            return "봄 웜톤"
        else:
            return "가을 웜톤"
    else:
        if chroma >= 2:
            return "겨울 쿨톤"
        else:
            return "여름 쿨톤"


def recommend_products(tone):
    result = []
    for name, data in products.items():
        if data["status"] == "판매중" and data["tone"] == tone:
            result.append(name)
    return result[:3]


# -------------------------
# 웹 UI
# -------------------------
HTML = """
<h2>퍼스널 컬러 진단 (제품 기반)</h2>

<form method="post">
<h3>잘 맞았던 제품 (3개)</h3>
<input name="good1"><br>
<input name="good2"><br>
<input name="good3"><br>

<h3>안 맞았던 제품 (선택)</h3>
<input name="bad1"><br>

<h3>반응 좋았던 제품 (선택)</h3>
<input name="best1"><br><br>

<button type="submit">분석하기</button>
</form>

{% if result %}
<hr>
<h2>결과: {{ result }}</h2>

<h3>추천 제품</h3>
<ul>
{% for r in recs %}
<li>{{ r }}</li>
{% endfor %}
</ul>
{% endif %}
"""


@app.route("/", methods=["GET", "POST"])
def home():
    if request.method == "POST":
        good = [request.form.get(f"good{i}") for i in range(1, 4)]
        bad = [request.form.get("bad1")]
        best = [request.form.get("best1")]

        t1, c1, v1 = analyze(good, weight=1)
        t2, c2, v2 = analyze(best, weight=2)
        t3, c3, v3 = analyze(bad, weight=-1)

        tone = t1 + t2 + t3
        chroma = c1 + c2 + c3

        result = determine_personal_color(tone, chroma)
        tone_type = "warm" if tone > 0 else "cool"

        recs = recommend_products(tone_type)

        return render_template_string(HTML, result=result, recs=recs)

    return render_template_string(HTML)


if __name__ == "__main__":
    app.run(debug=True)
