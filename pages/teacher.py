import streamlit as st
from supabase import create_client, Client
from datetime import datetime, timezone
import os

# ==================================================
# [Style] 지구과학 테마 CSS 적용 (Terra & Sky)
# ==================================================
def apply_earth_science_style():
    st.markdown("""
    <style>
        /* 1. 전체 배경: 하늘(Blue)에서 대지(Green/Beige)로 이어지는 그라데이션 */
        .stApp {
            background: linear-gradient(180deg, #E0F7FA 0%, #E8F5E9 60%, #F1F8E9 100%);
            background-attachment: fixed;
        }
        
        /* 2. 메인 타이틀 디자인 */
        h1 {
            color: #006064; /* 깊은 바다색 */
            font-family: 'Helvetica Neue', sans-serif;
            font-weight: 700;
            text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
            padding-bottom: 10px;
            border-bottom: 3px solid #00ACC1;
        }
        
        /* 3. 서브헤더 디자인 */
        h3, h4 {
            color: #2E7D32; /* 숲의 초록색 */
            font-weight: 600;
        }

        /* 4. 입력 폼(카드) 스타일 */
        div[data-testid="stForm"] {
            background-color: #FFFFFF;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 4px 15px rgba(0, 100, 100, 0.1); /* 은은한 청록색 그림자 */
            border: 1px solid #B2DFDB;
        }

        /* 5. 텍스트 영역 스타일 */
        .stTextArea textarea {
            background-color: #FAFAFA;
            border: 1px solid #CFD8DC;
            border-radius: 8px;
            font-size: 16px;
        }
        .stTextArea textarea:focus {
            border-color: #00ACC1;
            box-shadow: 0 0 5px rgba(0, 172, 193, 0.5);
        }

        /* 6. 버튼 스타일 */
        div.stButton > button {
            width: 100%;
            border-radius: 8px;
            font-weight: bold;
            transition: transform 0.2s;
        }
        /* 제출 버튼 (파란색) */
        div[data-testid="stForm"] div.stButton > button {
            background-color: #0277BD;
            color: white;
            border: none;
        }
        div[data-testid="stForm"] div.stButton > button:hover {
            background-color: #01579B;
            transform: scale(1.02);
        }
        
        /* 7. 피드백 박스 스타일 */
        .feedback-box-o {
            background-color: #E8F5E9; /* 연한 초록 */
            border-left: 5px solid #2E7D32;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
            color: #1B5E20;
        }
        .feedback-box-x {
            background-color: #FFEBEE; /* 연한 빨강 */
            border-left: 5px solid #C62828;
            padding: 15px;
            border-radius: 5px;
            margin-bottom: 10px;
            color: #B71C1C;
        }
    </style>
    """, unsafe_allow_html=True)

# CSS 적용 함수 호출
apply_earth_science_style()

# ==================================================
# [Logic] Supabase 및 기존 로직
# ==================================================

@st.cache_resource
def get_supabase_client() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

# 세션 상태 초기화
if "submitted_ok" not in st.session_state:
    st.session_state.submitted_ok = False
if "gpt_feedbacks" not in st.session_state:
    st.session_state.gpt_feedbacks = None
if "gpt_payload" not in st.session_state:
    st.session_state.gpt_payload = None

# ── 1. 수업 제목 (아이콘 추가) ──
col1, col2 = st.columns([1, 8])
with col1:
    st.image("https://cdn-icons-png.flaticon.com/512/2909/2909403.png", width=70) # 지구 아이콘
with col2:
    st.title("지구과학 탐구 보고서")
    st.markdown("**주제: 기체 분자 운동과 열에너지의 순환**")

st.markdown("---")

# ── 2~4. 입력 + 제출을 form 안에 묶기 ──
with st.form("submit_form"):
    st.markdown("### 📝 학생 정보 및 답안 작성")
    
    # ── 2. 학번 입력 ──
    student_id = st.text_input("학번", placeholder="예: 20315 (학번과 이름을 정확히 입력하세요)")

    # ── 3-1. 서술형 문제 1 ──
    QUESTION_1 = "기체 입자들의 운동과 온도의 관계를 서술하세요."
    st.markdown(f"#### ☁️ Q1. 대기 과학 기초")
    st.info(QUESTION_1, icon="🌡️")
    answer_1 = st.text_area("답안 1", key="answer1", height=120, placeholder="온도가 높아지면 기체 분자들은...")

    # ── 3-2. 서술형 문제 2 ──
    QUESTION_2 = "보일 법칙에 대해 설명하세요."
    st.markdown(f"#### 🎈 Q2. 기체의 압력과 부피")
    st.info(QUESTION_2, icon="📉")
    answer_2 = st.text_area("답안 2", key="answer2", height=120, placeholder="온도가 일정할 때 압력과 부피는...")

    # ── 3-3. 서술형 문제 3 ──
    QUESTION_3 = "열에너지 이동 3가지 방식(전도·대류·복사)을 설명하세요."
    st.markdown(f"#### 🌋 Q3. 지구 에너지의 순환")
    st.info(QUESTION_3, icon="🔥")
    answer_3 = st.text_area("답안 3", key="answer3", height=120, placeholder="전도는..., 대류는..., 복사는...")

    answers = [answer_1, answer_2, answer_3]

    # ── 4. 전체 제출 버튼 ──
    submitted = st.form_submit_button("🌍 답안 제출하기")

# ── 제출 처리 로직 ──
if submitted:
    if not student_id.strip():
        st.warning("⚠️ 학번을 입력해주세요.")
    elif any(ans.strip() == "" for ans in answers):
        st.warning("⚠️ 모든 문제에 대한 답안을 작성해주세요.")
    else:
        st.success(f"✅ 제출이 완료되었습니다! (학번: {student_id})")
        st.balloons() # 성공 시 풍선 효과
        st.session_state.submitted_ok = True
        st.session_state.gpt_feedbacks = None 

# ==================================================
# Step 2 – GPT API 기반 서술형 채점 + 피드백
# ==================================================

# Supabase 저장 함수
def save_to_supabase(payload: dict):
    supabase = get_supabase_client()
    if not supabase:
        raise ValueError("Supabase 클라이언트 연결 실패")

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

# 채점 기준
GRADING_GUIDELINES = {
    1: "기체 입자의 운동은 온도와 비례 관계임을 언급하고, 입자 충돌·속도 증가 예를 기술한다.",
    2: "일정한 온도에서, 기체의 압력과 부피가 서로 반비례한다.",
    3: "전도는 입자 간 직접 충돌, 대류는 유체의 순환, 복사는 전자기파를 통한 열 이동 방식이다.",
}

def normalize_feedback(text: str) -> str:
    if not text: return "X: 피드백 생성 실패"
    first_line = text.strip().splitlines()[0].strip()
    if first_line.startswith("O") and not first_line.startswith("O:"):
        first_line = "O: " + first_line[1:].lstrip(": ").strip()
    if first_line.startswith("X") and not first_line.startswith("X:"):
        first_line = "X: " + first_line[1:].lstrip(": ").strip()
    if not (first_line.startswith("O:") or first_line.startswith("X:")):
        first_line = "X: " + first_line
    head, body = first_line.split(":", 1)
    body = body.strip()
    if len(body) > 200: body = body[:200] + "…"
    return f"{head.strip()}: {body}"

# ── GPT 피드백 버튼 (스타일링 적용) ──
if st.session_state.submitted_ok:
    st.markdown("### 🤖 AI 선생님의 분석")
    
    # 버튼을 중앙 정렬 느낌으로 배치하거나, 강조
    if st.button("✨ GPT 피드백 및 채점 결과 확인하기", type="primary", disabled=st.session_state.gpt_feedbacks is not None):
        
        # 유효성 검사
        if "student_id" not in globals() or "answers" not in globals():
             # 리런 시 변수 소실 방지용 (session_state 활용 권장하나 기존 구조 유지)
            st.error("데이터가 초기화되었습니다. 다시 제출해주세요.")
            st.stop()

        try:
            from openai import OpenAI
            client = OpenAI(api_key=st.secrets["OPENAI_API_KEY"])
        except Exception:
            st.error("OpenAI 설정을 확인해주세요.")
            st.stop()

        feedbacks = []
        progress_bar = st.progress(0)
        status_text = st.empty()

        for idx, ans in enumerate(answers, start=1):
            status_text.text(f"문항 {idx} 채점 중... 🔭")
            criterion = GRADING_GUIDELINES.get(idx, "채점 기준 없음")
            prompt = (
                f"문항 번호: {idx}\n채점 기준: {criterion}\n학생 답안: {ans}\n\n"
                "출력 규칙:\n- 반드시 한 줄 출력\n- 형식: 'O: ...' 또는 'X: ...'\n- 학생에게 말하듯 친절하게, 200자 이내"
            )
            try:
                # 모델명은 사용자의 코드(gpt-5-mini) 유지, 필요시 gpt-4o-mini로 변경
                response = client.chat.completions.create(
                    model="gpt-4o-mini", # 범용적인 모델로 잠시 변경 (오류 방지)
                    messages=[
                        {"role": "system", "content": "너는 친절하고 정확한 지구과학 교사다."},
                        {"role": "user", "content": prompt},
                    ],
                    max_completion_tokens=500,
                )
                raw_text = response.choices[0].message.content.strip()
            except Exception as e:
                raw_text = f"API 오류: {e}"
            
            feedbacks.append(normalize_feedback(raw_text))
            progress_bar.progress(idx / 3)

        status_text.text("채점 완료! 결과를 저장합니다... 💾")
        st.session_state.gpt_feedbacks = feedbacks
        
        # Supabase 저장용 Payload
        st.session_state.gpt_payload = {
            "student_id": student_id.strip(),
            "answers": {f"Q{i}": a for i, a in enumerate(answers, start=1)},
            "feedbacks": {f"Q{i}": fb for i, fb in enumerate(feedbacks, start=1)},
            "guidelines": {f"Q{k}": v for k, v in GRADING_GUIDELINES.items()},
            "model": "gpt-4o-mini",
            "created_at": datetime.now(timezone.utc).isoformat(),
        }

        try:
            res = save_to_supabase(st.session_state.gpt_payload)
            # st.toast("DB 저장 완료!") # 알림 메시지
        except Exception as e:
            st.error(f"저장 오류 (Secrets 확인 필요): {e}")
            
        progress_bar.empty()
        status_text.empty()
        st.rerun() # 화면 갱신하여 결과 표시

# ── 4. 결과 표시 (커스텀 디자인) ──
if st.session_state.gpt_feedbacks:
    st.markdown("---")
    st.subheader("📊 채점 결과 리포트")

    for i, fb in enumerate(st.session_state.gpt_feedbacks, start=1):
        # O/X 파싱
        is_correct = fb.startswith("O:")
        content = fb.split(":", 1)[1].strip()
        
        # 지구과학 스타일 아이콘
        icon = "✅" if is_correct else "⚠️"
        style_class = "feedback-box-o" if is_correct else "feedback-box-x"
        
        # HTML/CSS를 이용한 커스텀 박스 렌더링
        st.markdown(f"""
        <div class="{style_class}">
            <strong>{icon} 문항 {i} 피드백</strong><br>
            {content}
        </div>
        """, unsafe_allow_html=True)

    st.success("모든 과정이 완료되었습니다. 수고하셨습니다! 🌍")
