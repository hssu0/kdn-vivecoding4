import streamlit as st
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError
import os

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="KDN 전력IT 업무 메일 도우미",
    page_icon="⚡",
    layout="wide",
)

# ── 공통 CSS ─────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif;
}

/* ── 헤더 ── */
.kdn-header {
    background: linear-gradient(135deg, #6366f1 0%, #06b6d4 100%);
    color: white;
    padding: 1.6rem 2rem;
    border-radius: 16px;
    margin-bottom: 1.4rem;
    box-shadow: 0 4px 24px rgba(99,102,241,0.25);
}
.kdn-header h1 {
    margin: 0;
    font-size: 1.65rem;
    font-weight: 700;
    letter-spacing: -0.5px;
}
.kdn-header p {
    margin: 0.35rem 0 0;
    font-size: 0.9rem;
    opacity: 0.88;
}
.kdn-badge {
    display: inline-block;
    background: rgba(255,255,255,0.22);
    border: 1px solid rgba(255,255,255,0.35);
    border-radius: 20px;
    padding: 0.15rem 0.7rem;
    font-size: 0.75rem;
    font-weight: 600;
    margin-top: 0.6rem;
    letter-spacing: 0.3px;
}

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
    background: linear-gradient(180deg, #f8faff 0%, #eef2ff 100%);
    border-right: 1px solid #e0e7ff;
}

/* ── 사이드바 소개 박스 ── */
.intro-card {
    background: white;
    border-radius: 12px;
    padding: 1rem 1.1rem;
    font-size: 0.85rem;
    color: #374151;
    line-height: 1.7;
    box-shadow: 0 2px 8px rgba(99,102,241,0.08);
    border: 1px solid #e0e7ff;
    margin-bottom: 0.5rem;
}
.intro-card .kdn-title {
    font-weight: 700;
    color: #4f46e5;
    font-size: 0.95rem;
    margin-bottom: 0.4rem;
}
.intro-card .tag {
    display: inline-block;
    background: #eef2ff;
    color: #4f46e5;
    border-radius: 6px;
    padding: 0.1rem 0.5rem;
    font-size: 0.78rem;
    font-weight: 600;
    margin: 0.15rem 0.1rem;
}

/* ── 섹션 라벨 ── */
.section-label {
    font-size: 0.8rem;
    font-weight: 700;
    color: #6366f1;
    text-transform: uppercase;
    letter-spacing: 0.8px;
    margin: 0.8rem 0 0.4rem;
}

/* ── 채팅 영역 배경 ── */
[data-testid="stChatMessageContent"] {
    border-radius: 12px !important;
}

/* ── 빠른 질문 버튼 스타일 (Streamlit 기본 버튼 덮어쓰기) ── */
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: white !important;
    color: #374151 !important;
    border: 1px solid #e0e7ff !important;
    border-radius: 10px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 0.45rem 0.8rem !important;
    transition: all 0.15s !important;
    box-shadow: 0 1px 4px rgba(99,102,241,0.06) !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: #eef2ff !important;
    border-color: #a5b4fc !important;
    color: #4f46e5 !important;
    box-shadow: 0 2px 8px rgba(99,102,241,0.13) !important;
}

/* ── 초기화 버튼 ── */
[data-testid="stSidebar"] [data-testid="stButton"]:last-child > button {
    background: #fef2f2 !important;
    color: #ef4444 !important;
    border-color: #fecaca !important;
}
[data-testid="stSidebar"] [data-testid="stButton"]:last-child > button:hover {
    background: #fee2e2 !important;
    border-color: #fca5a5 !important;
}

/* ── 채팅 입력창 ── */
[data-testid="stChatInput"] textarea {
    border-radius: 12px !important;
    border: 1.5px solid #e0e7ff !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}
[data-testid="stChatInput"] textarea:focus {
    border-color: #6366f1 !important;
    box-shadow: 0 0 0 3px rgba(99,102,241,0.12) !important;
}

/* ── 안내 박스 ── */
.welcome-box {
    background: linear-gradient(135deg, #f0f9ff 0%, #f5f3ff 100%);
    border: 1px solid #c7d2fe;
    border-radius: 14px;
    padding: 1.3rem 1.6rem;
    margin-bottom: 1rem;
    color: #374151;
    font-size: 0.9rem;
    line-height: 1.75;
}
.welcome-box strong { color: #4f46e5; }
</style>
""", unsafe_allow_html=True)

# ── 상수 ─────────────────────────────────────────────────────
SYSTEM_PROMPT = """당신은 한전KDN의 전력IT 전문가이자 업무 메일 작성 도우미입니다.

역할:
- 신입사원이 업무 메일을 작성하도록 친절하게 도와줍니다.
- 전력IT 용어(EMS, SCADA, DAS, AMI, MOS, RTU, FEP, DR, VPP, DERMS 등)를 쉽고 정확하게 설명합니다.
- 공식적이면서도 명확한 한국어 메일 문체를 사용합니다.

메일 작성 요청 시:
1. 수신자, 발신자, 목적에 맞는 제목(Subject)을 제안합니다.
2. 인사말 → 본문 → 마무리 인사 → 서명 순으로 구성합니다.
3. KDN 내부 공문 스타일(존댓말, 구체적 일정/수치 포함)을 따릅니다.
4. 메일 초안 완성 후 수정이 필요한 항목을 안내합니다.

항상 친절하고 실용적인 답변을 제공하세요."""

QUICK_QUESTIONS = [
    ("⚡ EMS 운영 보고", "EMS(에너지관리시스템) 운영 보고 메일을 작성해 주세요."),
    ("📡 SCADA 개요 설명", "SCADA 시스템의 역할과 구조를 설명해 주세요."),
    ("📊 AMI 현황 보고", "AMI 스마트미터 현황 보고 메일을 작성해 주세요."),
    ("🔧 RTU 장애 통보", "RTU 통신 장애 발생 상황을 관련 부서에 알리는 메일을 작성해 주세요."),
    ("🤝 회의 요청", "전력IT 시스템 개선 논의를 위한 회의 요청 메일을 작성해 주세요."),
    ("📋 DAS 점검 결과", "DAS 정기점검 결과 보고 메일 초안을 작성해 주세요."),
    ("🔌 FEP 구성 설명", "FEP(프론트엔드 프로세서)의 구성을 그룹사에 설명하는 메일을 작성해 주세요."),
    ("💡 MOS 협조 요청", "MOS 운영 관련 작업 협조 요청 메일을 작성해 주세요."),
]

# ── API 클라이언트 초기화 ─────────────────────────────────────
def get_client():
    api_key = None
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

# ── 스트리밍 제너레이터 ───────────────────────────────────────
def stream_response(client, messages):
    stream = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        max_tokens=2048,
        stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta

# ── 세션 상태 초기화 ──────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# ── 헤더 ─────────────────────────────────────────────────────
st.markdown("""
<div class="kdn-header">
  <h1>⚡ KDN 전력IT 업무 메일 도우미</h1>
  <p>전력IT 전문 AI가 업무 메일 작성을 도와드립니다</p>
  <span class="kdn-badge">Powered by GPT-4o · 한전KDN</span>
</div>
""", unsafe_allow_html=True)

# ── 사이드바 ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="section-label">🏢 한전KDN 소개</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="intro-card">
  <div class="kdn-title">한전KDN</div>
  전력IT 전문 기업으로 전력계통 운영에 필요한 핵심 시스템을 개발·운영합니다.<br><br>
  <span class="tag">EMS</span>
  <span class="tag">SCADA</span>
  <span class="tag">AMI</span>
  <span class="tag">DAS</span>
  <span class="tag">FEP</span>
  <span class="tag">RTU</span>
  <span class="tag">MOS</span>
  <span class="tag">DR</span>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="section-label">💬 빠른 메일 작성</div>', unsafe_allow_html=True)

    for label, question in QUICK_QUESTIONS:
        if st.button(label, key=f"quick_{label}", use_container_width=True):
            st.session_state.pending_question = question

    st.markdown("")
    if st.button("🗑️ 대화 초기화", use_container_width=True):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

    st.caption("GPT-4o · OpenAI · 한전KDN 바이브코딩 4기")

# ── 메인 채팅 영역 ────────────────────────────────────────────
client = get_client()

if client is None:
    st.error(
        "⚠️ **OPENAI_API_KEY가 설정되지 않았습니다.**\n\n"
        "Streamlit Cloud → 앱 설정 → **Secrets** 탭에 아래 내용을 입력하세요:\n"
        "```toml\n"
        'OPENAI_API_KEY = "sk-proj-..."\n'
        "```"
    )
    st.stop()

# 첫 방문 안내
if not st.session_state.messages:
    st.markdown("""
<div class="welcome-box">
👋 안녕하세요! <strong>KDN 전력IT 업무 메일 도우미</strong>입니다.<br>
왼쪽 버튼으로 빠르게 메일 초안을 요청하거나, 아래 입력창에 직접 질문해 보세요.<br><br>
예시: <em>"RTU 장애 발생을 운영팀장에게 보고하는 메일 작성해줘"</em>
</div>
""", unsafe_allow_html=True)

# 대화 히스토리 표시
for msg in st.session_state.messages:
    if msg["role"] != "system":
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

# 빠른 질문 버튼 처리
if st.session_state.pending_question:
    user_input = st.session_state.pending_question
    st.session_state.pending_question = None
else:
    user_input = st.chat_input("메일 초안 작성을 요청해 보세요...")

if user_input:
    # 시스템 메시지가 없으면 추가
    if not st.session_state.messages:
        st.session_state.messages.append({"role": "system", "content": SYSTEM_PROMPT})

    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            response_text = st.write_stream(
                stream_response(client, st.session_state.messages)
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )

        except AuthenticationError:
            st.error("❌ API 키 인증 실패. Secrets의 OPENAI_API_KEY를 확인하세요.")
        except RateLimitError:
            st.warning("⏳ 요청 한도 초과. 잠시 후 다시 시도해 주세요.")
        except APIConnectionError:
            st.error("🌐 네트워크 오류. 인터넷 연결을 확인해 주세요.")
        except Exception as e:
            st.error(f"⚠️ 오류: {str(e)}")
