import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timezone
from supabase import create_client, Client

# ---- 1. Supabase 설정 ----
@st.cache_resource
def get_supabase_client() -> Client:
    try:
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_SERVICE_ROLE_KEY"]
        return create_client(url, key)
    except Exception as e:
        st.error("Supabase 설정(secrets)을 확인해주세요.")
        st.stop()

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

def fetch_all_submissions():
    supabase = get_supabase_client()
    # 최신 제출순으로 데이터 가져오기
    response = supabase.table("student_submissions").select("*").order("created_at", descending=True).execute()
    return response.data

# ---- 2. 세션 상태 초기화 ----
if "submitted_ok" not in st.session_state:
    st.session_state.submitted_ok = False
if "gpt_feedbacks" not in st.session_state:
    st.session_state.gpt_feedbacks = None

# ---- 3. 문항 및
