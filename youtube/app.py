import streamlit as st
from googleapiclient.discovery import build
import pandas as pd
import plotly.express as px
from wordcloud import WordCloud
import matplotlib.pyplot as plt
import re
import os
import requests

# 페이지 설정
st.set_page_config(page_title="유튜브 댓글 분석기", layout="wide")
st.title("📊 유튜브 댓글 분석기 & 시각화 도구")

# 사이드바 설정 영역
st.sidebar.header("🔧 설정 및 입력")
api_key = st.sidebar.text_input("YouTube API Key를 입력하세요", type="password")
video_url = st.sidebar.text_input("유튜브 영상 링크를 입력하세요", placeholder="https://www.youtube.com/watch?v=...")
max_results = st.sidebar.slider("분석할 댓글 개수 설정", min_value=20, max_value=500, value=100, step=20)

# 한글 폰트 다운로드 함수 (스트림릿 클라우드 한글 깨짐 방지)
@st.cache_data
def load_font():
    font_url = "https://github.com/google/fonts/raw/main/ofl/nanumgothic/NanumGothic-Regular.ttf"
    font_path = "NanumGothic.ttf"
    if not os.path.exists(font_path):
        response = requests.get(font_url)
        with open(font_path, "wb") as f:
            f.write(response.content)
    return font_path

font_path = load_font()

# 유튜브 영상 ID 추출 함수
def extract_video_id(url):
    pattern = r'(?:v=|\/v\/|youtu\.be\/|\/embed\/)([a-zA-Z0-9_-]{11})'
    match = re.search(pattern, url)
    return match.group(1) if match else None

# 유튜브 댓글 수집 함수
def get_youtube_comments(api_key, video_id, max_results):
    youtube = build("youtube", "v3", developerKey=api_key)
    comments = []
    
    try:
        request = youtube.commentThreads().list(
            part="snippet",
            videoId=video_id,
            maxResults=min(max_results, 100),
            textFormat="plainText"
        )
        
        while request and len(comments) < max_results:
            response = request.execute()
            for item in response.get("items", []):
                snippet = item["snippet"]["topLevelComment"]["snippet"]
                comments.append({
                    "author": snippet["authorDisplayName"],
                    "published_at": pd.to_datetime(snippet["publishedAt"]),
                    "text": snippet["textDisplay"],
                    "like_count": snippet["likeCount"]
                })
                if len(comments) >= max_results:
                    break
            
            if "nextPageToken" in response and len(comments) < max_results:
                request = youtube.commentThreads().list_next(request, response)
            else:
                break
                
        return pd.DataFrame(comments)
    except Exception as e:
        st.error(f"⚠️ 데이터를 가져오는 중 에러가 발생했습니다: {e}")
        return None

# 실행 버튼 클릭 시
if st.sidebar.button("🚀 댓글 분석 시작"):
    if not api_key:
        st.sidebar.warning("API Key를 입력해주세요.")
    elif not video_url:
        st.sidebar.warning("유튜브 링크를 입력해주세요.")
    else:
        video_id = extract_video_id(video_url)
        if not video_id:
            st.sidebar.error("올바른 유튜브 URL 형식이 아닙니다.")
        else:
            # 1. 영상 표시 영역
            st.subheader("📺 분석 대상 영상")
            try:
                st.video(video_url)
            except Exception:
                st.info("영상을 화면에 불러올 수 없습니다. 링크를 확인해주세요.")

            st.divider()

            # 2. 데이터 수집 및 분석 시작
            with st.spinner("유튜브에서 댓글을 열심히 긁어오는 중입니다..."):
                df = get_youtube_comments(api_key, video_id, max_results)
                
            if df is not None and not df.empty:
                st.success(f"총 {len(df)}개의 댓글을 성공적으로 분석했습니다!")
                
                # 시간대 한국 기준(KST)으로 변환
                df['published_at'] = df['published_at'].dt.tz_convert('Asia/Seoul')
                
                # 2단 레이아웃 구성
                col1, col2 = st.columns(2)
                
                with col1:
                    st.subheader("📈 시간대별 댓글 작성 추이")
                    # 시간 단위(h)로 묶어서 시계열 트렌드 생성
                    df_trend = df.set_index('published_at').resample('h').size().reset_index(name='count')
                    fig_trend = px.line(df_trend, x='published_at', y='count', 
                                       title="시간당 댓글 작성 빈도",
                                       labels={'published_at': '작성 시간 (KST)', 'count': '댓글 수'})
                    st.plotly_chart(fig_trend, use_container_width=True)
                    
                with col2:
                    st.subheader("❤️ 댓글 반응도 (인기 댓글 목록)")
                    # 좋아요 수가 많은 상위 5개 댓글 추출
                    df_likes = df.nlargest(5, 'like_count')[['author', 'like_count', 'text']]
                    st.dataframe(df_likes, use_container_width=True, hide_index=True)
                    
                    # 좋아요 분포도 시각화
                    fig_likes = px.histogram(df, x='like_count', title="댓글당 좋아요 수 분포",
                                             labels={'like_count': '좋아요 수', 'count': '댓글 수'})
                    st.plotly_chart(fig_likes, use_container_width=True)
                
                st.divider()
                
                # 3. 워드 클라우드 영역
                st.subheader("🔤 댓글 워드 클라우드")
                
                # 텍스트 전처리 (한글, 영어, 공백만 유지)
                text_combined = " ".join(df['text'].values)
                text_combined = re.sub(r'[^가-힣a-zA-Z\s]', '', text_combined)
                
                if text_combined.strip():
                    wordcloud = WordCloud(
                        width=900, 
                        height=450, 
                        background_color='white',
                        font_path=font_path  # 다운로드한 나눔고딕 폰트 적용
                    ).generate(text_combined)
                    
                    fig_wc, ax = plt.subplots(figsize=(10, 5))
                    ax.imshow(wordcloud, interpolation='bilinear')
                    ax.axis('off')
                    st.pyplot(fig_wc)
                else:
                    st.info("워드클라우드를 생성할 의미 있는 텍스트 데이터가 부족합니다.")
            else:
                st.warning("댓글을 가져오지 못했습니다. 영상 설정(댓글 차단 등)이나 API 제한을 확인하세요.")
