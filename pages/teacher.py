import streamlit as st
import pandas as pd
import plotly.express as px  # 그래프 시각화를 위해 추가
from datetime import datetime
from supabase import create_client, Client

# ---- 1. Supabase 설정 (오류 수정: 세션 유지 및 예외 처리 강화) ----
@st.cache_resource
def get_supabase_client() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("Supabase 연결 설정(secrets)을 확인해주세요.")
        st.stop()

def fetch_all_submissions():
    supabase = get_supabase_client()
    # 생성일 기준 내림차순 정렬
    response = supabase.table("student_submissions").select("*").order("created_at", descending=True).execute()
    return response.data

# ---- 2. UI 설정 및 데이터 로드 ----
st.set_page_config(page_title="평가 결과 분석", layout="wide")

st.title("📊 지구과학 학습 데이터 분석 대시보드")

try:
    data = fetch_all_submissions()
    if not data:
        st.info("현재 저장된 데이터가 없습니다. 학생용 화면에서 답안을 먼저 제출해주세요.")
        st.stop()
    
    df = pd.DataFrame(data)

    # ---- 3. 오류 수정 및 데이터 전처리 ----
    # 피드백에서 'O'의 개수를 추출하여 통계 데이터 생성
    for i in range(1, 4):
        col_name = f'feedback_{i}'
        # 'O:'로 시작하면 Pass(정답), 아니면 Fail(보충 필요)로 분류
        df[f'status_{i}'] = df[col_name].apply(lambda x: '정답(O)' if str(x).startswith('O') else '보충(X)')

    # ---- 4. 상단 통계 메트릭 ----
    total_students = len(df)
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("총 제출 인원", f"{total_students}명")
    
    # 각 문항별 정답률 계산
    q1_pass = (df['status_1'] == '정답(O)').sum()
    q2_pass = (df['status_2'] == '정답(O)').sum()
    q3_pass = (df['status_3'] == '
