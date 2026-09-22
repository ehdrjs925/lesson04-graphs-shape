import streamlit as st
import pandas as pd
import plotly.express as px

# -----------------------------
# 기본 설정
# -----------------------------
st.set_page_config(
    page_title="영화 데이터 그래프 도감 1 - 시간",
    page_icon="🎬",
    layout="wide",
)

DATA_URL = "https://raw.githubusercontent.com/greatsong/modudata/main/data/kobis_daily.csv"


# -----------------------------
# 데이터 불러오기 / 전처리
# -----------------------------
@st.cache_data
def load_data():
    df = pd.read_csv(DATA_URL, encoding="utf-8-sig")

    # 날짜: 20250901 같은 8자리 값을 실제 날짜형으로 변환
    df["날짜"] = pd.to_datetime(
        df["날짜"].astype(str),
        format="%Y%m%d",
        errors="coerce",
    )

    # 숫자형 열 정리
    numeric_cols = ["순위", "일관객", "누적관객", "스크린수", "상영횟수"]
    for col in numeric_cols:
        df[col] = pd.to_numeric(df[col], errors="coerce")

    # 날짜 변환에 실패한 행이 있다면 제외
    df = df.dropna(subset=["날짜"]).copy()

    return df


try:
    df = load_data()
except Exception as e:
    st.error("데이터를 불러오는 중 오류가 발생했습니다.")
    st.exception(e)
    st.stop()


# -----------------------------
# 제목 / 데이터 안내
# -----------------------------
st.title("🎬 영화 데이터 그래프 도감 1 - 시간")
st.caption(
    "1년치 일별 박스오피스 TOP 10 데이터를 이용해 "
    "영화 관객의 시간에 따른 변화를 살펴봅니다."
)

with st.expander("데이터 정보 보기"):
    st.write(
        f"- 데이터 기간: **{df['날짜'].min():%Y-%m-%d} ~ {df['날짜'].max():%Y-%m-%d}**"
    )
    st.write(f"- 전체 기록 수: **{len(df):,}개**")
    st.write(f"- 영화 수: **{df['영화명'].nunique():,}편**")
    st.write(
        "- 열: 날짜 · 순위 · 영화코드 · 영화명 · 일관객 · 누적관객 · "
        "스크린수 · 상영횟수"
    )

st.divider()


# =========================================================
# 그래프 1
# =========================================================
st.header("그래프 1. 영화별 날짜에 따른 일관객 변화")

movie_names = sorted(df["영화명"].dropna().unique())

selected_movie = st.selectbox(
    "영화를 선택하세요.",
    movie_names,
)

movie_df = (
    df.loc[df["영화명"] == selected_movie, ["날짜", "일관객"]]
    .sort_values("날짜")
    .copy()
)

fig1 = px.line(
    movie_df,
    x="날짜",
    y="일관객",
    markers=True,
    title=f"{selected_movie} - 날짜별 일관객 변화",
)

fig1.update_traces(
    hovertemplate="<b>%{x|%Y-%m-%d}</b><br>일관객: %{y:,.0f}명<extra></extra>"
)

fig1.update_layout(
    xaxis_title="날짜",
    yaxis_title="일관객(명)",
    hovermode="x unified",
)

fig1.update_yaxes(tickformat=",")

st.plotly_chart(fig1, use_container_width=True)

st.markdown(
    "**이 그래프로 알 수 있는 것:** "
    "선택한 영화가 일별 박스오피스 TOP 10에 기록된 기간 동안 "
    "일관객 수가 시간에 따라 어떻게 변했는지 확인할 수 있습니다."
)

st.caption(
    "※ 이 데이터는 매일 박스오피스 10위권 기록만 포함하므로, "
    "선택한 영화가 10위 밖이었던 날짜는 그래프에 나타나지 않습니다."
)

st.divider()


# =========================================================
# 앞으로 추가할 그래프 구역
# =========================================================
st.header("다음 그래프 구역")
st.info(
    "앞으로 그래프 2, 그래프 3, 그래프 4 등을 이 아래에 "
    "서로 구분된 구역으로 계속 추가할 수 있습니다."
)

# 예시 구조
# st.divider()
# st.header("그래프 2. 제목")
# ...
# st.plotly_chart(fig2, use_container_width=True)
# st.markdown("**이 그래프로 알 수 있는 것:** ...")
