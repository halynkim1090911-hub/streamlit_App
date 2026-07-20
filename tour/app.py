import random
import urllib.parse
import streamlit as st

# -----------------------------------------------------------------------------
# 1.페이지 기본 설정
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="랜덤 국내 여행 뽑기",
    page_icon="🎲",
    layout="centered",
    initial_sidebar_state="expanded",
)

# -----------------------------------------------------------------------------
# 2. Mock Data (테스트용 샘플 데이터)
# -----------------------------------------------------------------------------
SAMPLE_TRAVEL_DATA = [
    {
        "id": 1,
        "name": "경복궁",
        "region": "서울",
        "theme": "문화/역사",
        "desc": "조선 시대 최고의 궁궐에서 느끼는 한복 스냅샷과 고즈넉한 산책!",
        "image": "https://images.unsplash.com/photo-1538485399081-7191377e8241?w=800",
    },
    {
        "id": 2,
        "name": "북촌한옥마을",
        "region": "서울",
        "theme": "문화/역사",
        "desc": "수백 년의 역사를 간직한 한옥 골목길에서 인생샷 남기기.",
        "image": "https://images.unsplash.com/photo-1548115184-bc6544d06a58?w=800",
    },
    {
        "id": 3,
        "name": "성산일출봉",
        "region": "제주",
        "theme": "자연/힐링",
        "desc": "바다 위로 솟아오른 유네스코 세계자연유산, 웅장한 오름 전망!",
        "image": "https://images.unsplash.com/photo-1540959733332-eab4deabeeaf?w=800",
    },
    {
        "id": 4,
        "name": "협재해수욕장",
        "region": "제주",
        "theme": "자연/힐링",
        "desc": "에메랄드빛 바다와 에메랄드빛 해변, 비양도를 바라보며 힐링.",
        "image": "https://images.unsplash.com/photo-1507525428034-b723cf961d3e?w=800",
    },
    {
        "id": 5,
        "name": "해운대 해수욕장",
        "region": "부산",
        "theme": "액티비티",
        "desc": "화려한 도시와 바다가 공존하는 부산 대표 핫플레이스!",
        "image": "https://images.unsplash.com/photo-1506744038136-46273834b3fb?w=800",
    },
    {
        "id": 6,
        "name": "감천문화마을",
        "region": "부산",
        "theme": "문화/역사",
        "desc": "알록달록 산자락 마을, 어린왕자 동상과의 특별한 추억.",
        "image": "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800",
    },
    {
        "id": 7,
        "name": "강릉 안목해변 카페거리",
        "region": "강원",
        "theme": "맛집/카페",
        "desc": "동해 바다 향기를 느끼며 한 잔의 커피 여유를 선사하는 길.",
        "image": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=800",
    },
    {
        "id": 8,
        "name": "설악산 국립공원",
        "region": "강원",
        "theme": "자연/힐링",
        "desc": "케이블카 타고 즐기는 단풍과 웅장한 기암괴석의 절경.",
        "image": "https://images.unsplash.com/photo-1464822759023-fed622ff2c3b?w=800",
    },
    {
        "id": 9,
        "name": "여수 돌산공원 & 케이블카",
        "region": "전남",
        "theme": "액티비티",
        "desc": "여수 밤바다의 화려한 야경을 한눈에 담을 수 있는 스팟.",
        "image": "https://images.unsplash.com/photo-1519501025264-65ba15a82390?w=800",
    },
    {
        "id": 10,
        "name": "경주 첨성대 & 황리단길",
        "region": "경북",
        "theme": "맛집/카페",
        "desc": "신라 시대 유적과 감성적인 카페/소품샵이 아우러진 이색거리.",
        "image": "https://images.unsplash.com/photo-1534447677768-be436bb09401?w=800",
    },
    {
        "id": 11,
        "name": "전주 한옥마을",
        "region": "전북",
        "theme": "맛집/카페",
        "desc": "맛있는 먹거리와 한옥 특유의 고즈넉함이 넘쳐나는 먹방 여행지.",
        "image": "https://images.unsplash.com/photo-1555396273-367ea4eb4db5?w=800",
    },
    {
        "id": 12,
        "name": "남이섬",
        "region": "경기",
        "theme": "자연/힐링",
        "desc": "메타세쿼이아 길을 걸으며 일상의 스트레스를 날려버리는 섬 여행.",
        "image": "https://images.unsplash.com/photo-1448375240586-882707db888b?w=800",
    },
]

# -----------------------------------------------------------------------------
# 3. 사이드바 (필터 설정)
# -----------------------------------------------------------------------------
st.sidebar.header("🎯 여행지 필터 설정")

# 지역 필터
regions = ["전국"] + sorted(
    list(set([item["region"] for item in SAMPLE_TRAVEL_DATA]))
)
selected_region = st.sidebar.selectbox("📍 지역을 선택하세요", regions)

# 테마 필터
themes = ["전체"] + sorted(
    list(set([item["theme"] for item in SAMPLE_TRAVEL_DATA]))
)
selected_theme = st.sidebar.selectbox("🎨 테마를 선택하세요", themes)

st.sidebar.markdown("---")
st.sidebar.caption("💡 Tip: 원하시는 지역과 테마를 고른 뒤 메인 화면의 버튼을 눌러보세요!")

# -----------------------------------------------------------------------------
# 4. 메인 화면 UI
# -----------------------------------------------------------------------------
st.title("🎲 이번 주말 어디 가? 랜덤 국내 여행 뽑기")
st.write("어디로 떠날지 고민이신가요? 버튼 한 번으로 당신만의 여행지를 결정해보세요!")

st.markdown("---")


# -----------------------------------------------------------------------------
# 5. 핵심 로직: 랜덤 추출 함수
# -----------------------------------------------------------------------------
def get_filtered_data(region, theme):
    filtered = SAMPLE_TRAVEL_DATA
    if region != "전국":
        filtered = [item for item in filtered if item["region"] == region]
    if theme != "전체":
        filtered = [item for item in filtered if item["theme"] == theme]
    return filtered


# Session state 초기화
if "selected_spot" not in st.session_state:
    st.session_state.selected_spot = None

# 조건에 맞는 데이터 수집
available_spots = get_filtered_data(selected_region, selected_theme)

col1, col2 = st.columns([2, 1])

with col1:
    pick_button = st.button("🎲 여행지 뽑기!", use_container_width=True, type="primary")

with col2:
    if st.session_state.selected_spot is not None:
        re_pick = st.button("🔄 다시 뽑기", use_container_width=True)
        if re_pick:
            pick_button = True


# -----------------------------------------------------------------------------
# 6. 결과 출력 처리
# -----------------------------------------------------------------------------
if pick_button:
    if not available_spots:
        st.warning("⚠️ 선택하신 조건에 해당하는 여행지가 없습니다. 다른 필터를 선택해주세요!")
        st.session_state.selected_spot = None
    else:
        # 풍선 애니메이션 효과
        st.balloons()
        # 랜덤으로 1곳 추출하여 session_state에 저장
        st.session_state.selected_spot = random.choice(available_spots)

# 결과 카드 렌더링
if st.session_state.selected_spot:
    spot = st.session_state.selected_spot

    st.markdown("### 🎉 추천 여행지 결과!")

    # 여행지 카드 레이아웃
    with st.container(border=True):
        st.image(spot["image"], use_column_width=True)
        st.subheader(spot["name"])

        # 태그 표시
        st.markdown(f"**위치:** `{spot['region']}` | **테마:** `{spot['theme']}`")
        st.write(spot["desc"])

        st.markdown("---")

        # 지도 연결 URL 생성
        encoded_name = urllib.parse.quote(spot["name"])
        kakao_map_url = f"https://map.kakao.com/link/search/{encoded_name}"
        naver_map_url = f"https://map.naver.com/v5/search/{encoded_name}"

        # 지도 링크 버튼
        btn_col1, btn_col2 = st.columns(2)
        with btn_col1:
            st.link_button("🟡 카카오맵에서 보기", kakao_map_url, use_container_width=True)
        with btn_col2:
            st.link_button("🟢 네이버지도에서 보기", naver_map_url, use_container_width=True)

        st.markdown("---")

        # 7. 공유용 텍스트 생성
        share_text = f"✨ [이번 주말 어디 가?] 추천 여행지!\n- 장소: {spot['name']} ({spot['region']})\n- 테마: {spot['theme']}\n- 소개: {spot['desc']}"

        st.markdown("**📱 친구에게 공유하기 (아래 텍스트를 복사하세요):**")
        st.code(share_text, language="text")
