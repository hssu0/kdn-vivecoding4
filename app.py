import streamlit as st
import anthropic
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
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;600;700&display=swap');

html, body, [class*="css"] { font-family: 'Noto Sans KR', sans-serif; }

.kdn-header {
    background: linear-gradient(135deg, #1B2A4A 0%, #3D6FE0 100%);
    color: white;
    padding: 1.4rem 2rem;
    border-radius: 12px;
    margin-bottom: 1.2rem;
}
.kdn-header h1 { margin: 0; font-size: 1.6rem; font-weight: 700; }
.kdn-header p  { margin: 0.3rem 0 0; font-size: 0.9rem; opacity: 0.85; }

.intro-box {
    background: #f0f4ff;
    border-left: 4px solid #3D6FE0;
    padding: 0.9rem 1.2rem;
    border-radius: 8px;
    font-size: 0.88rem;
    color: #1B2A4A;
    margin-bottom: 1rem;
}

[data-testid="stSidebar"] { background-color: #f7f9fd; }
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
    ("📡 SCADA 개요", "SCADA 시스템의 역할과 구조를 설명해 주세요."),
    ("📊 AMI 보고서 메일", "AMI 스마트미터 현황 보고 메일을 작성해 주세요."),
    ("🔧 RTU 장애 메일", "RTU 통신 장애 발생 상황을 관련 부서에 알리는 메일을 작성해 주세요."),
    ("🤝 회의 요청 메일", "전력IT 시스템 개선 논의를 위한 회의 요청 메일을 작성해 주세요."),
    ("📋 DAS 점검 결과", "DAS 정기점검 결과 보고 메일 초안을 작성해 주세요."),
    ("🔌 FEP 구성 설명", "FEP(프론트엔드 프로세서)의 구성을 그룹사 부서에 설명하는 메일을 작성해 주세요."),
    ("💡 MOS 작업 요청", "MOS 운영 관련 작업 협조 요청 메일을 작성해 주세요."),
]

# ── API 클라이언트 초기화 ─────────────────────────────────────
def get_client():
    api_key = None
    try:
        api_key = st.secrets["ANTHROPIC_API_KEY"]
    except Exception:
        api_key = os.environ.get("ANTHROPIC_API_KEY")
    if not api_key:
        return None
    return anthropic.Anthropic(api_key=api_key)

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
</div>
""", unsafe_allow_html=True)

# ── 사이드바 ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 🏢 KDN 소개")
    st.markdown("""
<div class="intro-box">
<b>한전KDN</b>은 전력IT 전문 기업으로,<br>
전력계통 운영에 필요한 SCADA, EMS, AMI, DAS 등<br>
핵심 시스템을 개발·운영합니다.<br><br>
• 주요 사업: 전력IT 시스템 구축·운영<br>
• 계열: 한국전력공사 자회사
</div>
""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 💬 자주 묻는 질문")

    for label, question in QUICK_QUESTIONS:
        if st.button(label, key=f"quick_{label}", use_container_width=True):
            st.session_state.pending_question = question

    st.divider()
    if st.button("🗑️ 대화 초기화", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.pending_question = None
        st.rerun()

    st.caption("Claude claude-sonnet-4-6 · Anthropic")

# ── 메인 채팅 영역 ────────────────────────────────────────────
client = get_client()

if client is None:
    st.error(
        "⚠️ **API 키가 설정되지 않았습니다.**\n\n"
        "다음 중 하나의 방법으로 설정하세요:\n"
        "1. `.streamlit/secrets.toml` 파일에 `ANTHROPIC_API_KEY = \"sk-...\"` 추가\n"
        "2. 환경변수 `ANTHROPIC_API_KEY` 설정\n"
        "3. Streamlit Cloud 배포 시 Secrets 설정 메뉴 이용"
    )
    st.stop()

# 대화 히스토리 표시
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 빠른 질문 버튼 클릭 처리
if st.session_state.pending_question:
    user_input = st.session_state.pending_question
    st.session_state.pending_question = None
else:
    user_input = st.chat_input("메일 초안 작성을 요청해 보세요...")

if user_input:
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)

    with st.chat_message("assistant"):
        try:
            with client.messages.stream(
                model="claude-sonnet-4-6",
                max_tokens=2048,
                system=SYSTEM_PROMPT,
                messages=st.session_state.messages,
            ) as stream:
                response_text = st.write_stream(
                    (chunk.text for chunk in stream.text_stream)
                )

            st.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )

        except anthropic.AuthenticationError:
            st.error("❌ API 키 인증에 실패했습니다. 키를 확인해 주세요.")
        except anthropic.RateLimitError:
            st.warning("⏳ 요청이 너무 많습니다. 잠시 후 다시 시도해 주세요.")
        except anthropic.APIConnectionError:
            st.error("🌐 네트워크 연결 오류입니다. 인터넷 연결을 확인해 주세요.")
        except Exception as e:
            st.error(f"⚠️ 오류가 발생했습니다: {str(e)}\n\n잠시 후 다시 시도해 주세요.")
