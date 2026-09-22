import pandas as pd
import plotly.express as px
import streamlit as st

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 2 - 분포와 관계",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_movies.csv"


# -----------------------------
# 데이터 불러오기 및 전처리
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 개봉일: YYYYMMDD 형식의 8자리 값을 실제 날짜형으로 변환
    df["openDt"] = pd.to_datetime(
        df["openDt"].astype(str),
        format="%Y%m%d",
        errors="coerce"
    )

    # genre에 |가 있으면 첫 번째 장르만 사용
    # 예: "드라마|전쟁" -> "드라마"
    # "/"는 사용자가 지정한 분리 기호가 아니므로 그대로 둠
    df["main_genre"] = (
        df["genre"]
        .fillna("기타")
        .astype(str)
        .str.split("|", regex=False)
        .str[0]
        .str.strip()
    )

    # 빈 장르값 처리
    df.loc[df["main_genre"].eq(""), "main_genre"] = "기타"

    return df


df = load_data()


# -----------------------------
# 제목
# -----------------------------
st.title("영화 데이터 그래프 도감 2 - 분포와 관계")
st.caption("1년간 박스오피스 10위권에 진입한 영화 중 해당 기간에 개봉한 영화 데이터를 분석합니다.")

st.divider()


# =========================================================
# 그래프 1. 장르별 영화 편수
# =========================================================
st.header("1. 장르별 영화 편수")
st.write("영화의 대표 장르를 기준으로 장르별 영화 편수를 비교합니다.")

genre_counts = (
    df["main_genre"]
    .value_counts()
    .rename_axis("장르")
    .reset_index(name="영화 편수")
)

fig1 = px.pie(
    genre_counts,
    names="장르",
    values="영화 편수",
    hole=0.48,
)

fig1.update_traces(
    textinfo="label+percent",
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value:,}편<br>"
        "비율: %{percent}<extra></extra>"
    ),
)

fig1.update_layout(
    margin=dict(t=30, b=20, l=20, r=20),
    legend_title_text="장르",
)

st.plotly_chart(fig1, use_container_width=True)

st.markdown(
    "**이 그래프로 알 수 있는 것:** "
    "장르별 영화 편수와 전체 영화에서 각 장르가 차지하는 비율을 비교할 수 있다."
)

st.divider()


# =========================================================
# 그래프 2. 장르별 영화 총 관객 트리맵
# =========================================================
st.header("2. 장르별 영화 총 관객 트리맵")
st.write("장르 안에 각 영화를 배치하고, 영화의 총 관객 수가 많을수록 더 큰 칸으로 표시합니다.")

treemap_df = df.copy()

# total_audi를 숫자형으로 변환하고, 결측값은 0으로 처리
treemap_df["total_audi"] = pd.to_numeric(
    treemap_df["total_audi"],
    errors="coerce"
).fillna(0)

fig2 = px.treemap(
    treemap_df,
    path=["main_genre", "movieNm"],
    values="total_audi",
    custom_data=["movieNm", "total_audi"],
)

fig2.update_traces(
    hovertemplate=(
        "<b>%{customdata[0]}</b><br>"
        "총 관객: %{customdata[1]:,.0f}명"
        "<extra></extra>"
    )
)

fig2.update_layout(
    margin=dict(t=30, b=20, l=20, r=20)
)

st.plotly_chart(fig2, use_container_width=True)

st.markdown(
    "**이 그래프로 알 수 있는 것:** "
    "장르별 구성과 각 장르 안에서 총 관객 수가 많은 영화의 상대적인 규모를 한눈에 비교할 수 있다."
)

st.divider()


# =========================================================
# 그래프 3. 총 관객 분포 히스토그램
# =========================================================
st.header("3. 총 관객 분포")
st.write("영화별 총 관객 수가 어느 구간에 많이 분포하는지 확인합니다.")

hist_df = df.copy()
hist_df["total_audi"] = pd.to_numeric(hist_df["total_audi"], errors="coerce")
hist_df = hist_df.dropna(subset=["total_audi"])

fig3 = px.histogram(
    hist_df,
    x="total_audi",
    nbins=20,
    labels={"total_audi": "총 관객 수"},
)

fig3.update_traces(
    hovertemplate="총 관객 구간: %{x}<br>영화 편수: %{y}편<extra></extra>"
)

fig3.update_layout(
    xaxis_title="총 관객 수",
    yaxis_title="영화 편수",
    bargap=0.05,
    margin=dict(t=30, b=20, l=20, r=20),
)

st.plotly_chart(fig3, use_container_width=True)

# 히스토그램에서 영화가 가장 많이 몰린 구간 계산
bin_count = 20
bin_categories = pd.cut(hist_df["total_audi"], bins=bin_count)
most_common_bin = bin_categories.value_counts().idxmax()

# 총 관객 수가 가장 많은 영화
max_row = hist_df.loc[hist_df["total_audi"].idxmax()]

st.markdown(
    f"**이 그래프로 알 수 있는 것:** "
    f"가장 많은 영화가 몰린 총 관객 구간은 약 "
    f"**{most_common_bin.left:,.0f}명 ~ {most_common_bin.right:,.0f}명**이고, "
    f"총 관객이 가장 많은 영화는 **{max_row['movieNm']}** "
    f"({max_row['total_audi']:,.0f}명)이다."
)

st.divider()


# =========================================================
# 그래프 4. 개봉일 스크린수와 총 관객의 관계
# =========================================================
st.header("4. 개봉일 스크린수와 총 관객의 관계")
st.write("개봉일 스크린 수와 영화의 최종 총 관객 수 사이의 관계를 장르별로 비교합니다.")

scatter_df = df.copy()
scatter_df["first_scrn"] = pd.to_numeric(scatter_df["first_scrn"], errors="coerce")
scatter_df["total_audi"] = pd.to_numeric(scatter_df["total_audi"], errors="coerce")
scatter_df = scatter_df.dropna(subset=["first_scrn", "total_audi"])

fig4 = px.scatter(
    scatter_df,
    x="first_scrn",
    y="total_audi",
    color="main_genre",
    hover_name="movieNm",
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객",
        "main_genre": "장르",
    },
)

fig4.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig4.update_layout(
    margin=dict(t=30, b=20, l=20, r=20)
)

st.plotly_chart(fig4, use_container_width=True)

st.markdown(
    "**이 그래프로 알 수 있는 것:** "
    "개봉일에 확보한 스크린 수와 최종 총 관객 수의 관계를 살펴보고, "
    "장르별로 분포 차이가 있는지도 비교할 수 있다."
)

st.divider()


# =========================================================
# 그래프 5. 장르별 총 관객 박스플롯
# =========================================================
st.header("5. 장르별 총 관객 분포")
st.write("영화가 10편 이상인 장르만 골라 장르별 총 관객 분포와 이상치를 비교합니다.")

box_df = df.copy()
box_df["total_audi"] = pd.to_numeric(box_df["total_audi"], errors="coerce")
box_df = box_df.dropna(subset=["total_audi"])

genre_movie_counts = box_df["main_genre"].value_counts()
valid_genres = genre_movie_counts[genre_movie_counts >= 10].index
box_df = box_df[box_df["main_genre"].isin(valid_genres)].copy()

fig5 = px.box(
    box_df,
    x="main_genre",
    y="total_audi",
    points="outliers",
    hover_name="movieNm",
    labels={
        "main_genre": "장르",
        "total_audi": "총 관객",
    },
)

fig5.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "장르: %{x}<br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig5.update_layout(
    xaxis_title="장르",
    yaxis_title="총 관객",
    margin=dict(t=30, b=20, l=20, r=20),
)

st.plotly_chart(fig5, use_container_width=True)

st.markdown(
    "**이 그래프로 알 수 있는 것:** "
    "영화 수가 충분히 많은 장르끼리 총 관객의 중앙값, 분포 범위, "
    "그리고 다른 영화보다 유난히 관객 수가 큰 이상치를 비교할 수 있다."
)

st.divider()


# =========================================================
# 그래프 6. 개봉일 스크린수 × 총 관객 버블 그래프
# =========================================================
st.header("6. 개봉일 스크린수와 총 관객의 버블 그래프")
st.write("네 번째 그래프에 첫 주 관객 수를 점 크기로 추가해 세 변수의 관계를 함께 봅니다.")

bubble_df = df.copy()
bubble_df["first_scrn"] = pd.to_numeric(bubble_df["first_scrn"], errors="coerce")
bubble_df["total_audi"] = pd.to_numeric(bubble_df["total_audi"], errors="coerce")
bubble_df["first_week_audi"] = pd.to_numeric(
    bubble_df["first_week_audi"],
    errors="coerce"
)
bubble_df = bubble_df.dropna(
    subset=["first_scrn", "total_audi", "first_week_audi"]
)

fig6 = px.scatter(
    bubble_df,
    x="first_scrn",
    y="total_audi",
    size="first_week_audi",
    color="main_genre",
    hover_name="movieNm",
    size_max=45,
    labels={
        "first_scrn": "개봉일 스크린수",
        "total_audi": "총 관객",
        "first_week_audi": "첫 주 관객",
        "main_genre": "장르",
    },
)

fig6.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉일 스크린수: %{x:,.0f}개<br>"
        "총 관객: %{y:,.0f}명"
        "<extra></extra>"
    )
)

fig6.update_layout(
    margin=dict(t=30, b=20, l=20, r=20)
)

st.plotly_chart(fig6, use_container_width=True)

st.markdown(
    "**이 그래프로 알 수 있는 것:** "
    "개봉일 스크린 수와 최종 총 관객의 관계에 더해, "
    "첫 주 관객이 많았던 영화가 최종 흥행에서도 어떤 위치에 놓이는지 함께 볼 수 있다."
)

st.divider()


# =========================================================
# 그래프 7. 제작 국가 → 장르 선버스트
# =========================================================
st.header("7. 제작 국가와 장르 구성")
st.write("제작 국가에서 장르로 내려가는 구조를 영화 편수를 기준으로 확인합니다.")

sunburst_df = df.copy()
sunburst_df["nation"] = sunburst_df["nation"].fillna("기타").astype(str).str.strip()
sunburst_df.loc[sunburst_df["nation"].eq(""), "nation"] = "기타"

sunburst_df["movie_count"] = 1

fig7 = px.sunburst(
    sunburst_df,
    path=["nation", "main_genre"],
    values="movie_count",
)

fig7.update_traces(
    hovertemplate=(
        "<b>%{label}</b><br>"
        "영화 편수: %{value}편"
        "<extra></extra>"
    )
)

fig7.update_layout(
    margin=dict(t=30, b=20, l=20, r=20)
)

st.plotly_chart(fig7, use_container_width=True)

st.markdown(
    "**이 그래프로 알 수 있는 것:** "
    "제작 국가별 영화 편수와 각 국가 안에서 어떤 장르의 영화가 많이 포함되어 있는지 확인할 수 있다."
)

st.divider()


# =========================================================
# 그래프 8. 첫 주 관객과 10위권 유지 기간의 관계
# =========================================================
st.header("8. 개봉 첫 주 관객이 많을수록 10위권에 더 오래 머무는가?")
st.write(
    "개봉 첫 주 관객 수와 박스오피스 10위권에 머문 날수 사이의 관계를 살펴봅니다."
)

relation_df = df.copy()

relation_df["first_week_audi"] = pd.to_numeric(
    relation_df["first_week_audi"],
    errors="coerce"
)

relation_df["days_in_top10"] = pd.to_numeric(
    relation_df["days_in_top10"],
    errors="coerce"
)

relation_df = relation_df.dropna(
    subset=["first_week_audi", "days_in_top10"]
)

fig8 = px.scatter(
    relation_df,
    x="first_week_audi",
    y="days_in_top10",
    hover_name="movieNm",
    labels={
        "first_week_audi": "개봉 첫 주 관객",
        "days_in_top10": "10위권에 머문 날수",
    },
)

fig8.update_traces(
    hovertemplate=(
        "<b>%{hovertext}</b><br>"
        "개봉 첫 주 관객: %{x:,.0f}명<br>"
        "10위권에 머문 날수: %{y:,.0f}일"
        "<extra></extra>"
    )
)

fig8.update_layout(
    xaxis_title="개봉 첫 주 관객",
    yaxis_title="10위권에 머문 날수",
    margin=dict(t=30, b=20, l=20, r=20),
)

st.plotly_chart(fig8, use_container_width=True)

# 두 변수의 상관계수를 계산해 설명 문구를 데이터에 맞게 자동 생성
correlation = relation_df["first_week_audi"].corr(
    relation_df["days_in_top10"]
)

if pd.isna(correlation):
    relation_text = "두 변수 사이의 관계를 뚜렷하게 판단하기 어렵다"
elif correlation >= 0.7:
    relation_text = "개봉 첫 주 관객이 많을수록 10위권에 오래 머무는 강한 양의 관계가 나타난다"
elif correlation >= 0.4:
    relation_text = "개봉 첫 주 관객이 많을수록 10위권에 오래 머무는 경향이 비교적 뚜렷하게 나타난다"
elif correlation >= 0.2:
    relation_text = "개봉 첫 주 관객이 많을수록 10위권에 오래 머무는 약한 경향이 나타난다"
elif correlation > -0.2:
    relation_text = "개봉 첫 주 관객과 10위권 유지 기간 사이의 뚜렷한 관계는 크지 않다"
else:
    relation_text = "개봉 첫 주 관객과 10위권 유지 기간 사이에 반대 방향의 경향이 나타난다"

st.markdown(
    f"**이 그래프로 알 수 있는 것:** "
    f"{relation_text}. "
    f"(상관계수: {correlation:.2f})"
)

st.divider()


# =========================================================
# 다음 그래프 추가 구역
# =========================================================
st.header("9. 다음 그래프")
st.info("새로운 질문을 정한 뒤 그 질문에 맞는 그래프를 이 구역부터 계속 추가할 수 있습니다.")
