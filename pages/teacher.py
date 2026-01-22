import streamlit as st
import pandas as pd
from supabase import create_client, Client

# ---- Supabase 설정 (기존 코드와 동일) ----
@st.cache_resource
def get_supabase_client() -> Client:
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
    return create_client(url, key)

def fetch_all_submissions():
    supabase = get_supabase_client()
    # 최신순으로 데이터 가져오기
    response = supabase.table("student_submissions").select("*").order("created_at", descending=True).execute()
    return response.data

# ---- 메인 UI ----
st.set_page_config(page_title="평가 관리자 대시보드", layout="wide")

st.title("🎓 지구과학 학습 평가 관리자")
st.markdown("학생들의 제출 답안과 AI 피드백 결과를 모니터링합니다.")

# 데이터 불러오기
try:
    data = fetch_all_submissions()
    if not data:
        st.info("아직 제출된 답안이 없습니다.")
        st.stop()
    
    df = pd.DataFrame(data)
    
    # ---- 대시보드 통계 ----
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("총 제출 인원", f"{len(df)}명")
    with col2:
        # 'O:'로 시작하는 피드백이 정답으로 간주하여 통계 (예시)
        correct_q1 = df['feedback_1'].str.startswith("O:").sum()
        st.metric("문항 1 정답률", f"{(correct_q1/len(df)*100):.1f}%")
    with col3:
        latest_submit = pd.to_datetime(df['created_at']).max().strftime('%m/%d %H:%M')
        st.metric("최근 업데이트", latest_submit)

    st.divider()

    # ---- 학생별 상세 조회 ----
    st.subheader("📋 학생별 제출 답안 상세 내역")
    
    # 검색 및 필터링
    search_id = st.text_input("학번으로 검색", placeholder="검색할 학번을 입력하세요.")
    if search_id:
        display_df = df[df['student_id'].astype(str).str.contains(search_id)]
    else:
        display_df = df

    # 데이터 테이블 표시
    for index, row in display_df.iterrows():
        with st.expander(f"📌 학번: {row['student_id']} | 제출시간: {row['created_at'][:16]}"):
            c1, c2 = st.columns([1, 1])
            
            with c1:
                st.markdown("**[학생 답안]**")
                st.info(f"**Q1:** {row['answer_1']}")
                st.info(f"**Q2:** {row['answer_2']}")
                st.info(f"**Q3:** {row['answer_3']}")
            
            with c2:
                st.markdown("**[AI 피드백]**")
                def show_feedback(fb):
                    if fb.startswith("O:"): st.success(fb)
                    else: st.warning(fb)
                
                show_feedback(row['feedback_1'])
                show_feedback(row['feedback_2'])
                show_feedback(row['feedback_3'])
                
            if st.button(f"{row['student_id']} 데이터 삭제", key=f"del_{index}"):
                # 삭제 기능 (필요시 활성화)
                # supabase.table("student_submissions").delete().eq("id", row['id']).execute()
                st.error("삭제 권한이 없습니다. (DB 직접 제어 필요)")

    # ---- 데이터 다운로드 ----
    st.divider()
    csv = display_df.to_csv(index=False).encode('utf-8-sig')
    st.download_button(
        label="📥 전체 결과 Excel(CSV) 다운로드",
        data=csv,
        file_name=f"earth_science_results_{datetime.now().strftime('%Y%m%d')}.csv",
        mime='text/csv',
    )

except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
