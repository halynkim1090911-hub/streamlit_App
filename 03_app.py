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

st.write("서울시 공영주차장 CSV 또는 Excel 파일을 업로드하세요.")

uploaded = st.file_uploader(
    "파일 업로드",
    type=["csv", "xlsx"]
)


# -----------------------------
# 파일 읽기 함수
# -----------------------------
def load_data(file):

    if file.name.endswith(".xlsx"):
        return pd.read_excel(file)

    encodings = [
        "utf-8",
        "utf-8-sig",
        "cp949",
        "euc-kr",
        "latin1"
    ]

    for enc in encodings:
        try:
            file.seek(0)
            df = pd.read_csv(file, encoding=enc)
            st.success(f"파일 인코딩 : {enc}")
            return df
        except Exception:
            pass

    st.error("파일을 읽을 수 없습니다.")
    st.stop()


if uploaded is not None:

    df = load_data(uploaded)

    st.success("데이터 불러오기 완료!")

    st.write("### 데이터 미리보기")
    st.dataframe(df.head())

    st.write("### 컬럼명")

    st.write(df.columns.tolist())

    # -----------------------------
    # 컬럼 자동 찾기
    # -----------------------------

    def find_column(candidates):

        for c in candidates:
            if c in df.columns:
                return c

        return None


    col_name = find_column(["주차장명", "주차장 이름"])
    col_gu = find_column(["자치구", "구"])
    col_addr = find_column(["주소"])
    col_lat = find_column(["위도"])
    col_lon = find_column(["경도"])
    col_type = find_column(["주차장종류", "주차장 종류"])
    col_fee = find_column(["기본요금", "요금"])
    col_free = find_column(["무료여부", "무료"])

    # -----------------------------
    # 사이드바
    # -----------------------------

    st.sidebar.header("검색")

    if col_gu:

        gu = st.sidebar.selectbox(
            "자치구",
            ["전체"] + sorted(df[col_gu].dropna().unique())
        )

    else:

        gu = "전체"

    if col_type:

        parking_types = st.sidebar.multiselect(
            "주차장 종류",
            sorted(df[col_type].dropna().unique())
        )

    else:

        parking_types = []

    free_only = st.sidebar.checkbox("무료 주차장만")

    result = df.copy()

    if col_gu and gu != "전체":
        result = result[result[col_gu] == gu]

    if col_type and parking_types:
        result = result[result[col_type].isin(parking_types)]

    if free_only and col_free:

        result = result[
            result[col_free].astype(str).str.contains(
                "무료|Y|가능|TRUE|1",
                case=False,
                na=False
            )
        ]

    # -----------------------------
    # 통계
    # -----------------------------

    st.write("## 통계")

    c1, c2, c3 = st.columns(3)

    c1.metric("주차장 수", len(result))

    if col_free:

        free_count = result[col_free].astype(str).str.contains(
            "무료|Y|가능|TRUE|1",
            case=False,
            na=False
        ).sum()

        c2.metric("무료 주차장", int(free_count))

    if col_fee:

        fee = pd.to_numeric(result[col_fee], errors="coerce")

        c3.metric(
            "평균 기본요금",
            f"{fee.mean():.0f}원"
            if fee.notna().sum() else "-"
        )

    # -----------------------------
    # 그래프
    # -----------------------------

    if col_type:

        st.write("## 주차장 종류")

        chart = (
            result[col_type]
            .value_counts()
            .reset_index()
        )

        chart.columns = ["종류", "개수"]

        fig = px.bar(
            chart,
            x="종류",
            y="개수",
            color="종류"
        )

        st.plotly_chart(fig, use_container_width=True)

    # -----------------------------
    # 무료주차장
    # -----------------------------

    if col_free:

        st.write("## 무료 이용 가능 주차장")

        free = result[
            result[col_free].astype(str).str.contains(
                "무료|Y|가능|TRUE|1",
                case=False,
                na=False
            )
        ]

        st.dataframe(free)

    # -----------------------------
    # 지도
    # -----------------------------

    if col_lat and col_lon:

        st.write("## 지도")

        map_df = result.copy()

        map_df[col_lat] = pd.to_numeric(
            map_df[col_lat],
            errors="coerce"
        )

        map_df[col_lon] = pd.to_numeric(
            map_df[col_lon],
            errors="coerce"
        )

        map_df = map_df.dropna(subset=[col_lat, col_lon])

        if len(map_df):

            layer = pdk.Layer(
                "ScatterplotLayer",
                data=map_df,
                get_position=f'[{col_lon},{col_lat}]',
                get_radius=50,
                get_fill_color=[255, 0, 0, 180],
                pickable=True
            )

            view = pdk.ViewState(
                latitude=map_df[col_lat].mean(),
                longitude=map_df[col_lon].mean(),
                zoom=11
            )

            tooltip = {
                "text": f"{col_name}: {{{col_name}}}"
                if col_name else ""
            }

            deck = pdk.Deck(
                layers=[layer],
                initial_view_state=view,
                tooltip=tooltip
            )

            st.pydeck_chart(deck)

    # -----------------------------
    # 결과
    # -----------------------------

    st.write("## 검색 결과")

    st.dataframe(result)

    csv = result.to_csv(
        index=False,
        encoding="utf-8-sig"
    ).encode("utf-8-sig")

    st.download_button(
        "CSV 다운로드",
        csv,
        "parking_result.csv",
        "text/csv"
    )
