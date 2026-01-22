import streamlit as st
from datetime import datetime, timezone
from supabase import create_client, Client

# ---- Supabase 설정 ----
@st.cache_resource
def get_supabase_client() -> Client:
    # st.secrets에 SUPABASE_URL과 SUPABASE_SERVICE_ROLE_KEY가 설정되어 있어야 합니다.
    url = st.secrets["SUPABASE_URL"]
    key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
    return create_client(url, key)

def save_to_supabase(payload: dict):
    supabase = get_supabase_client()
    row = {
        "student_id": payload["student_id"],
        "answer_1": payload["answers"]["Q1"],
        "answer_2": payload["answers"]["Q2"],
        "answer_3": payload["answers"]["Q3"],
        "feedback_1": payload["feedbacks"]["Q1"],
        "feedback_2": payload["feedbacks"]["Q2"],
        "feedback_3": payload["feedbacks"]["Q3"],
        "guideline_1": payload["guidelines"]["Q1"],
        "guideline_2": payload["guidelines"]["Q2"],
        "guideline_3": payload["guidelines"]["Q3"],
        "model": payload["model"],
    }
    return supabase.table("student_submissions").insert(row).execute()

# ---- 세션 상태 초기화 ----
if "submitted_ok" not in st.session_state:
    st.session_state.submitted_ok = False
if "gpt_feedbacks" not in st.session_state:
    st.session_state.gpt_feedbacks = None
if "gpt_payload" not in st.session_state:
    st.session_state.gpt_payload = None

# ---- 문항 및 채점 기준 설정 ----
GRADING_GUIDELINES = {
    1: "엘니뇨 시기 무역풍 약화로 인해 동태평양 적도 해역의 수온이 평상시보다 높아지는 현상을 정확히 설명해야 함.",
    2: "라니냐 시기 서태평양 기압이 평상시보다 더 낮아져 강수량이 증가하고 홍수 가능성이 커짐을 언급해야 함.",
    3: "엘니뇨와 라니냐가 발생하는 근본 원인인 대기와 해양의 상호 작용(워커 순환의 변화)을 포함하여 기술해야 함."
}

# ---- 메인 UI ----
st.title("🌎 지구과학: 엘니뇨와 라니냐 심화 학습")
st.markdown("엘니뇨와 라니냐의 발생 원리와 영향에 대해 자신의 생각을 서술해 보세요.")

with st.form("ocean_form"):
    student_id = st.text_input("학번", placeholder="예: 20101")
    
    st.markdown("---")
    
    # 문항 1
    QUESTION_1 = "엘니뇨가 발생할 때 무역풍의 변화와 동태평양 적도 해역의 수온 변화를 서술하세요."
    st.markdown("#### [문제 1]")
    st.write(QUESTION_1)
    answer_1 = st.text_area("답안 입력 1", key="ans1", height=120)

    # 문항 2
    QUESTION_2 = "라니냐 시기, 서태평양 적도 주변 해역(인도네시아 등)에서 나타나는 기상 변화와 그 원인을 서술하세요."
    st.markdown("#### [문제 2]")
    st.write(QUESTION_2)
    answer_2 = st.text_area("답안 입력 2", key="ans2", height=120)

    # 문항 3
    QUESTION_3 = "엘니뇨와 라니냐가 단순한 해수온 변화를 넘어 전 지구적 기후에 영향을 주는 이유(대기-해양 상호작용)를 설명하세요."
    st.markdown("#### [문제 3]")
    st.write(QUESTION_3)
    answer_3 = st.text_area("답안 입력 3", key="ans3", height=120)

    answers = [answer_1, answer_2, answer_3]
    submitted = st.form_submit_button("답안 제출하기")

# 제출 처리
if submitted:
    if not student_id.strip():
        st.warning("학번을 먼저 입력해 주세요.")
    elif any(ans.strip() == "" for ans in answers):
        st.warning("모든 문항에 대한 답안을 작성해 주세요.")
    else:
        st.success(f"제출 완료! (학번: {student_id}) 아래 'AI 피드백 확인' 버튼을 눌러주세요.")
        st.session_state.submitted_ok = True
        st.session_state.gpt_feedbacks = None 

# ---- 피드백 및 저장 로직 ----
def normalize_feedback(text: str) -> str:
    if not text: return "X: 피드백 생성 실패"
    first_line = text.strip().splitlines()[0].strip()
    if first_line.startswith("O") and not first_line.startswith("O:"):
        first_line = "O: " + first_line[1:].lstrip(": ").strip()
    elif first_line.startswith("X") and not first_line.startswith("X:"):
        first_line = "X: " + first_line[1:].lstrip(": ").strip()
    if not (first_line.startswith("O:") or first_line.startswith("X:")):
        first_line = "X: " + first_line
    
    parts = first_line.split(":", 1)
    head = parts[0].strip()
    body = parts[1].strip() if len(parts) > 1 else ""
    if len(body) > 200: body = body[:200] + "…"
    return f"{head}: {body}"

if st.button("AI 선생님 피드백 받기", disabled=not st.session_state.submitted_ok):
    try:
        from openai import OpenAI
        client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
    except Exception:
        st.error("API 키 설정 또는 라이브러리를 확인하세요.")
        st.stop()

    feedbacks = []
    with st.spinner("AI 선생님이 지구과학 답안을 분석 중입니다... 🌊"):
        for idx, ans in enumerate(answers, start=1):
            criterion = GRADING_GUIDELINES.get(idx)
            prompt = (
                f"주제: 엘니뇨와 라니냐\n"
                f"문항 {idx}: {criterion}\n"
                f"학생 답안: {ans}\n\n"
                "규칙:\n"
                "1. 'O: ' 또는 'X: '로 시작할 것\n"
                "2. 한 줄로 친절하게 설명할 것 (200자 이내)\n"
            )
            try:
                # 모델명은 환경에 따라 gpt-4o 또는 gpt-3.5-turbo 등으로 변경 가능
                response = client.chat.completions.create(
                    model="gpt-4o", 
                    messages=[
                        {"role": "system", "content": "너는 전문적인 지구과학 교사야."},
                        {"role": "user", "content": prompt}
                    ]
                )
                raw_text = response.choices[0].message.content.strip()
            except Exception as e:
                raw_text = f"X: 오류 발생 ({e})"
            
            feedbacks.append(normalize_feedback(raw_text))

    st.session_state.gpt_feedbacks = feedbacks
    st.session_state.gpt_payload = {
        "student_id": student_id.strip(),
        "answers": {f"Q{i}": a for i, a in enumerate(answers, start=1)},
        "feedbacks": {f"Q{i}": fb for i, fb in enumerate(feedbacks, start=1)},
        "guidelines": {f"Q{k}": v for k, v in GRADING_GUIDELINES.items()},
        "model": "gpt-4o",
        "created_at": datetime.now(timezone.utc).isoformat(),
    }

    # Supabase 저장
    try:
        save_to_supabase(st.session_state.gpt_payload)
        st.toast("데이터베이스 저장 성공!")
    except Exception as e:
        st.error(f"DB 저장 오류: {e}")

# 결과 표시
if st.session_state.gpt_feedbacks:
    st.markdown("---")
    st.subheader("📝 AI 선생님의 맞춤 피드백")
    for i, fb in enumerate(st.session_state.gpt_feedbacks, start=1):
        if fb.startswith("O:"):
            st.success(f"**문항 {i}** | {fb}")
        else:
            st.info(f"**문항 {i}** | {fb}")
