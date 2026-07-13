import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

st.set_page_config(
    page_title="서울시 공영주차장",
    page_icon="🅿️",
    layout="wide"
)

st.title("🅿️ 서울시 공영주차장 정보 서비스")

st.markdown("""
CSV 또는 Excel 파일을 업로드하세요.

필수 컬럼 예시

- 자치구
- 주차장명
- 주소
- 위도
- 경도
- 기본요금
- 추가요금
- 주차면수
""")

uploaded_file = st.file_uploader(
    "데이터 업로드",
    type=["csv", "xlsx"]
)

if uploaded_file:

    if uploaded_file.name.endswith(".csv"):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    # 컬럼명 변경(필요 시 수정)
    df = df.rename(columns={
        "주차장명":"name",
        "주소":"address",
        "자치구":"district",
        "위도":"lat",
        "경도":"lon",
        "기본요금":"basic_fee",
        "추가요금":"extra_fee",
        "주차면수":"capacity"
    })

    st.success(f"{len(df)}개의 데이터를 불러왔습니다.")

    # 숫자형 변환
    df["lat"] = pd.to_numeric(df["lat"], errors="coerce")
    df["lon"] = pd.to_numeric(df["lon"], errors="coerce")

    df = df.dropna(subset=["lat","lon"])

    #########################################
    # Sidebar
    #########################################

    st.sidebar.header("검색 조건")

    districts = sorted(df["district"].dropna().unique())

    selected = st.sidebar.selectbox(
        "자치구 선택",
        ["전체"] + districts
    )

    keyword = st.sidebar.text_input("주차장명 검색")

    #########################################
    # Filtering
    #########################################

    filtered = df.copy()

    if selected != "전체":
        filtered = filtered[
            filtered["district"] == selected
        ]

    if keyword:
        filtered = filtered[
            filtered["name"].str.contains(
                keyword,
                case=False,
                na=False
            )
        ]

    #########################################
    # Summary
    #########################################

    c1,c2,c3 = st.columns(3)

    c1.metric("주차장 수", len(filtered))

    if "capacity" in filtered.columns:
        c2.metric(
            "총 주차면수",
            int(filtered["capacity"].sum())
        )

    if "basic_fee" in filtered.columns:
        avg_fee = filtered["basic_fee"].astype(float).mean()
        c3.metric(
            "평균 기본요금",
            f"{avg_fee:,.0f}원"
        )

    #########################################
    # Map
    #########################################

    st.subheader("🗺️ 주차장 위치")

    center = [
        filtered["lat"].mean(),
        filtered["lon"].mean()
    ]

    m = folium.Map(
        location=center,
        zoom_start=12
    )

    for _, row in filtered.iterrows():

        popup = f"""
        <b>{row['name']}</b><br>

        주소 : {row.get('address','')}<br>

        기본요금 : {row.get('basic_fee','-')}원<br>

        추가요금 : {row.get('extra_fee','-')}원<br>

        주차면수 : {row.get('capacity','-')}
        """

        folium.Marker(
            location=[row["lat"],row["lon"]],
            popup=popup,
            tooltip=row["name"],
            icon=folium.Icon(
                color="blue",
                icon="info-sign"
            )
        ).add_to(m)

    st_folium(
        m,
        width=1200,
        height=600
    )

    #########################################
    # Data Table
    #########################################

    st.subheader("📋 주차장 정보")

    show_cols = [
        "district",
        "name",
        "address",
        "basic_fee",
        "extra_fee",
        "capacity"
    ]

    show_cols = [
        c for c in show_cols if c in filtered.columns
    ]

    st.dataframe(
        filtered[show_cols],
        use_container_width=True
    )

else:

    st.info("좌측에서 CSV 또는 Excel 파일을 업로드하세요.")
