import streamlit as st
import pandas as pd
import pydeck as pdk
import plotly.express as px

st.set_page_config(
    page_title="서울시 공영주차장 정보",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 서울시 공영주차장 정보 서비스")

st.markdown("""
CSV 파일을 업로드하면
- 자치구별 검색
- 주차장 종류 검색
- 무료주차장 확인
- 요금 조회
- 지도 시각화
를 제공합니다.
""")

uploaded = st.file_uploader(
    "서울시 공영주차장 CSV 업로드",
    type=["csv"]
)

if uploaded is not None:

import pandas as pd

try:
    df = pd.read_csv(uploaded, encoding="utf-8")
except UnicodeDecodeError:
    try:
        uploaded.seek(0)
        df = pd.read_csv(uploaded, encoding="cp949")
    except UnicodeDecodeError:
        uploaded.seek(0)
        df = pd.read_csv(uploaded, encoding="euc-kr")

    st.success("데이터 업로드 완료")

    st.write("데이터 미리보기")

    st.dataframe(df.head())

    #######################################
    # 컬럼명
    #######################################

    # 예시 컬럼
    # 주차장명
    # 주소
    # 자치구
    # 위도
    # 경도
    # 주차장종류
    # 기본요금
    # 무료여부

    #######################################
    # 사이드바
    #######################################

    st.sidebar.header("검색 조건")

    gu = st.sidebar.selectbox(
        "자치구 선택",
        ["전체"] + sorted(df["자치구"].dropna().unique().tolist())
    )

    parking_type = st.sidebar.multiselect(
        "주차장 종류",
        sorted(df["주차장종류"].dropna().unique())
    )

    free_only = st.sidebar.checkbox("무료 이용 가능")

    #######################################
    # 필터링
    #######################################

    result = df.copy()

    if gu != "전체":
        result = result[result["자치구"] == gu]

    if len(parking_type) > 0:
        result = result[result["주차장종류"].isin(parking_type)]

    if free_only:
        result = result[result["무료여부"] == "무료"]

    #######################################
    # 통계
    #######################################

    col1, col2, col3 = st.columns(3)

    col1.metric("주차장 수", len(result))

    col2.metric(
        "무료 주차장",
        len(result[result["무료여부"] == "무료"])
    )

    col3.metric(
        "평균 기본요금",
        f"{result['기본요금'].mean():.0f}원"
    )

    #######################################
    # 그래프
    #######################################

    st.subheader("주차장 종류별 현황")

    fig = px.bar(
        result["주차장종류"].value_counts().reset_index(),
        x="index",
        y="주차장종류",
        labels={
            "index":"주차장 종류",
            "주차장종류":"개수"
        }
    )

    st.plotly_chart(fig, use_container_width=True)

    #######################################
    # 무료 주차장
    #######################################

    st.subheader("무료 이용 가능한 주차장")

    free = result[result["무료여부"] == "무료"]

    if len(free):

        st.dataframe(
            free[
                [
                    "주차장명",
                    "자치구",
                    "주소",
                    "주차장종류"
                ]
            ]
        )

    else:

        st.info("무료 주차장이 없습니다.")

    #######################################
    # 지도
    #######################################

    st.subheader("주차장 위치")

    layer = pdk.Layer(
        "ScatterplotLayer",
        data=result,
        get_position='[경도, 위도]',
        get_radius=50,
        get_fill_color=[255,0,0,180],
        pickable=True
    )

    view = pdk.ViewState(
        latitude=result["위도"].mean(),
        longitude=result["경도"].mean(),
        zoom=11
    )

    deck = pdk.Deck(
        layers=[layer],
        initial_view_state=view,
        tooltip={
            "text":"""
주차장명 : {주차장명}

주소 : {주소}

요금 : {기본요금}원

종류 : {주차장종류}
"""
        }
    )

    st.pydeck_chart(deck)

    #######################################
    # 상세 데이터
    #######################################

    st.subheader("검색 결과")

    st.dataframe(result)

    #######################################
    # 다운로드
    #######################################

    csv = result.to_csv(index=False).encode("utf-8-sig")

    st.download_button(
        "검색 결과 다운로드",
        csv,
        "parking.csv",
        "text/csv"
    )

else:

    st.info("서울시 공영주차장 CSV를 업로드하세요.")
