import streamlit as st
import pandas as pd

st.set_page_config(
    page_title="서울시 공영주차장",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 서울시 공영주차장 정보")

uploaded_file = st.file_uploader(
    "CSV 또는 Excel 파일 업로드",
    type=["csv", "xlsx"]
)

if uploaded_file is not None:

    # 파일 읽기
    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # 컬럼명 변경
    df = df.rename(columns={
        "주차장명": "name",
        "주소": "address",
        "자치구": "district",
        "위도": "lat",
        "경도": "lon",
        "기본요금": "basic_fee",
        "추가요금": "extra_fee",
        "주차면수": "capacity"
    })

    # 위도/경도 숫자형 변환
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")
    df = df.dropna(subset=["lat", "lon"])

    # 자치구 선택
    districts = sorted(df["district"].dropna().unique())

    selected = st.sidebar.selectbox(
        "자치구 선택",
        ["전체"] + districts
    )

    if selected != "전체":
        df = df[df["district"] == selected]

    # 주차장 검색
    keyword = st.sidebar.text_input("주차장명 검색")

    if keyword:
        df = df[df["name"].str.contains(keyword, case=False, na=False)]

    st.subheader("📊 요약")

    col1, col2, col3 = st.columns(3)

    col1.metric("주차장 수", len(df))

    if "capacity" in df.columns:
        col2.metric("총 주차면수", int(df["capacity"].sum()))

    if "basic_fee" in df.columns:
        fee = pd.to_numeric(df["basic_fee"], errors="coerce").mean()
        col3.metric("평균 기본요금", f"{fee:,.0f}원")

    st.subheader("🗺️ 주차장 위치")

    st.map(
        df.rename(columns={
            "lat": "latitude",
            "lon": "longitude"
        })
    )

    st.subheader("📋 주차장 목록")

    cols = [
        "district",
        "name",
        "address",
        "basic_fee",
        "extra_fee",
        "capacity"
    ]

    cols = [c for c in cols if c in df.columns]

    st.dataframe(
        df[cols],
        use_container_width=True
    )

else:
    st.info("CSV 또는 Excel 파일을 업로드하세요.")
