import streamlit as st
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError
import os

# ── 페이지 설정 ──────────────────────────────────────────────
st.set_page_config(
    page_title="KDN 업무 메일 도우미",
    page_icon="✉️",
    layout="wide",
)

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

*, html, body, [class*="css"] {
    font-family: 'Noto Sans KR', sans-serif !important;
}

/* ═══ 전체 배경 그라데이션 ═══ */
.stApp {
    background: linear-gradient(145deg,
        #e0e7ff 0%,
        #ede9fe 25%,
        #fce7f3 50%,
        #dbeafe 75%,
        #d1fae5 100%
    ) fixed !important;
}

/* ═══ 메인 컨테이너 ═══ */
.main .block-container {
    background: transparent !important;
    padding-top: 1.5rem !important;
    max-width: 860px !important;
}

/* ═══ 헤더 카드 ═══ */
.kdn-header {
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 45%, #0ea5e9 100%);
    color: white;
    padding: 1.5rem 2rem;
    border-radius: 20px;
    margin-bottom: 1.2rem;
    box-shadow: 0 8px 32px rgba(99,102,241,0.30);
}
.kdn-header h1 {
    margin: 0 0 0.25rem;
    font-size: 1.55rem;
    font-weight: 700;
    letter-spacing: -0.4px;
}
.kdn-header p {
    margin: 0;
    font-size: 0.88rem;
    opacity: 0.85;
}
.kdn-pill {
    display: inline-block;
    background: rgba(255,255,255,0.20);
    border: 1px solid rgba(255,255,255,0.35);
    border-radius: 30px;
    padding: 0.18rem 0.75rem;
    font-size: 0.72rem;
    font-weight: 600;
    margin-top: 0.6rem;
}

/* ═══ 사이드바 ═══ */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.75) !important;
    backdrop-filter: blur(12px) !important;
    border-right: 1px solid rgba(255,255,255,0.6) !important;
}
[data-testid="stSidebar"] > div:first-child {
    padding-top: 1.2rem;
}

/* 사이드바 섹션 라벨 */
.sb-label {
    font-size: 0.72rem;
    font-weight: 700;
    color: #6d28d9;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin: 1rem 0 0.5rem;
    padding-left: 2px;
}

/* 메일 유형 버튼 */
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: rgba(255,255,255,0.85) !important;
    color: #374151 !important;
    border: 1.5px solid rgba(167,139,250,0.3) !important;
    border-radius: 12px !important;
    font-size: 0.83rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 0.55rem 0.9rem !important;
    transition: all 0.18s ease !important;
    box-shadow: 0 2px 8px rgba(109,40,217,0.06) !important;
    margin-bottom: 2px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #ede9fe, #dbeafe) !important;
    border-color: #a78bfa !important;
    color: #5b21b6 !important;
    box-shadow: 0 4px 14px rgba(109,40,217,0.15) !important;
    transform: translateX(2px) !important;
}

/* 초기화 버튼 (마지막) */
[data-testid="stSidebar"] button[kind="secondary"] {
    background: rgba(254,226,226,0.7) !important;
    color: #dc2626 !important;
    border-color: rgba(252,165,165,0.5) !important;
}
[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background: #fee2e2 !important;
    border-color: #fca5a5 !important;
    transform: none !important;
}

/* ═══ 채팅 메시지 버블 ═══ */
[data-testid="stChatMessage"] {
    background: rgba(255,255,255,0.80) !important;
    backdrop-filter: blur(8px) !important;
    border-radius: 18px !important;
    padding: 1rem 1.3rem !important;
    margin-bottom: 0.75rem !important;
    box-shadow: 0 2px 16px rgba(99,102,241,0.08) !important;
    border: 1px solid rgba(255,255,255,0.9) !important;
    transition: box-shadow 0.2s !important;
}
[data-testid="stChatMessage"]:hover {
    box-shadow: 0 4px 20px rgba(99,102,241,0.13) !important;
}

/* 유저 메시지 – 보라빛 틴트 */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: linear-gradient(135deg,
        rgba(237,233,254,0.90) 0%,
        rgba(219,234,254,0.90) 100%) !important;
    border-color: rgba(167,139,250,0.35) !important;
}

/* ═══ 채팅 입력창 ═══ */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.85) !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.12) !important;
    border: 1.5px solid rgba(167,139,250,0.4) !important;
    backdrop-filter: blur(8px) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    font-size: 0.92rem !important;
}

/* ═══ 웰컴 카드 ═══ */
.welcome-card {
    background: rgba(255,255,255,0.75);
    backdrop-filter: blur(10px);
    border: 1px solid rgba(167,139,250,0.25);
    border-radius: 18px;
    padding: 1.4rem 1.8rem;
    color: #374151;
    font-size: 0.9rem;
    line-height: 1.8;
    margin-bottom: 1rem;
    box-shadow: 0 4px 24px rgba(109,40,217,0.08);
}
.welcome-card .w-title {
    font-size: 1.05rem;
    font-weight: 700;
    color: #5b21b6;
    margin-bottom: 0.5rem;
}
.welcome-card .w-tip {
    display: inline-block;
    background: linear-gradient(135deg, #ede9fe, #dbeafe);
    border-radius: 8px;
    padding: 0.25rem 0.7rem;
    font-size: 0.83rem;
    color: #4f46e5;
    margin-top: 0.4rem;
}

/* ═══ 소개 카드 ═══ */
.intro-card {
    background: rgba(255,255,255,0.75);
    border-radius: 12px;
    padding: 0.9rem 1rem;
    font-size: 0.83rem;
    color: #4b5563;
    line-height: 1.7;
    border: 1px solid rgba(167,139,250,0.2);
    margin-bottom: 0.5rem;
}
.intro-card b { color: #5b21b6; }
.sys-tag {
    display: inline-block;
    background: linear-gradient(135deg, #ede9fe, #dbeafe);
    color: #4f46e5;
    border-radius: 6px;
    padding: 0.08rem 0.45rem;
    font-size: 0.76rem;
    font-weight: 600;
    margin: 0.12rem 0.08rem;
}

/* divider */
hr { border-color: rgba(167,139,250,0.2) !important; }
</style>
""", unsafe_allow_html=True)

# ── 상수: 시스템 프롬프트 ─────────────────────────────────────
SYSTEM_PROMPT = """당신은 한전KDN의 전력IT 전문가이자 업무 메일 작성 도우미입니다.

**대화 방식**
- 사용자가 메일 유형을 선택하면, 메일 작성에 필요한 정보를 **한 번에 한 가지씩** 친절하게 질문하세요.
- 각 답변을 받은 후 자연스럽게 다음 질문으로 넘어가세요.
- 모든 필요 정보가 수집되면 "감사합니다! 지금 바로 메일 초안을 작성해 드릴게요. ✉️" 라고 말하고 완성된 메일을 작성하세요.
- 중간에 사용자가 직접 입력한 정보는 그대로 활용하세요.

**메일 유형별 필요 정보 (순서대로 질문)**

[시스템 현황 보고]
Q1. 어떤 시스템의 현황을 보고하시나요? (예: EMS, SCADA, AMI 등)
Q2. 보고 기간이 언제인가요? (예: 2025년 5월)
Q3. 주요 운영 현황을 알려주세요. (예: 정상 운영, 가동률 99.5% 등)
Q4. 특이사항이나 이슈가 있다면 알려주세요. (없으면 "없음" 이라고 답해주세요)

[장애 보고]
Q1. 장애가 발생한 시스템명은 무엇인가요?
Q2. 장애 발생 일시는 언제인가요? (예: 2025년 5월 28일 14:30)
Q3. 장애 증상과 영향 범위를 설명해 주세요.
Q4. 현재 조치 상황은 어떻게 되나요? (복구 완료 여부 포함)

[회의 요청]
Q1. 회의 목적 또는 안건은 무엇인가요?
Q2. 희망하는 회의 일시가 있으신가요?
Q3. 회의 참석 대상은 누구인가요? (부서명 또는 직책)
Q4. 회의 장소 또는 방식은 어떻게 되나요? (온라인/오프라인, 장소명 등)

[점검 결과]
Q1. 점검한 시스템명은 무엇인가요?
Q2. 점검 일시는 언제인가요?
Q3. 점검 결과를 간단히 설명해 주세요. (예: 정상, 이상 발견 등)
Q4. 후속 조치가 필요한 사항이 있나요? (없으면 "없음")

[작업 협조 요청]
Q1. 협조가 필요한 작업 내용은 무엇인가요?
Q2. 관련 시스템명은 무엇인가요?
Q3. 협조 요청 일정은 언제인가요?
Q4. 협조를 요청할 부서 또는 담당자는 누구인가요?

[자료 회신 요청]
Q1. 요청하는 자료의 이름 또는 내용은 무엇인가요?
Q2. 해당 자료가 필요한 사유는 무엇인가요?
Q3. 회신 기한은 언제인가요?
Q4. 회신 방법은 어떻게 해주시면 되나요? (예: 이메일 첨부, 공문 등)

**메일 완성 형식**
```
제목: [시스템명/안건] 관련 [메일유형] 건

수신: [수신자명] / [부서명]
발신: [발신자명] / [부서명]
날짜: [작성일]

안녕하십니까, [발신자 부서]입니다.

[본문 내용]

감사합니다.

[발신자명]
[부서명] | [연락처]
```
- 수신자 정보는 [수신자명/부서]로 표시합니다.
- 공식적이고 명확한 한국어 문체를 사용합니다.
- 메일 완성 후 "[ ] 부분을 실제 정보로 교체해 주세요." 안내를 추가하세요."""

# ── 메일 유형 버튼 ───────────────────────────────────────────
MAIL_TYPES = [
    ("📊", "시스템 현황 보고",  "시스템 현황 보고 메일을 작성하고 싶습니다."),
    ("🚨", "장애 보고",        "장애 보고 메일을 작성하고 싶습니다."),
    ("📅", "회의 요청",        "회의 요청 메일을 작성하고 싶습니다."),
    ("🔍", "점검 결과",        "점검 결과 보고 메일을 작성하고 싶습니다."),
    ("🤝", "작업 협조 요청",   "작업 협조 요청 메일을 작성하고 싶습니다."),
    ("📨", "자료 회신 요청",   "자료 회신 요청 메일을 작성하고 싶습니다."),
]

# ── API 클라이언트 ────────────────────────────────────────────
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

# ── 세션 상태 ─────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "trigger" not in st.session_state:
    st.session_state.trigger = None

# ── 헤더 ─────────────────────────────────────────────────────
st.markdown("""
<div class="kdn-header">
  <h1>✉️ KDN 업무 메일 도우미</h1>
  <p>필요한 정보를 대화로 수집한 후 완성된 메일 초안을 작성해 드립니다</p>
  <span class="kdn-pill">GPT-4o · 한전KDN 바이브코딩 4기</span>
</div>
""", unsafe_allow_html=True)

# ── 사이드바 ──────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sb-label">🏢 한전KDN</div>', unsafe_allow_html=True)
    st.markdown("""
<div class="intro-card">
<b>한전KDN</b> 전력IT 전문 기업<br>
<span class="sys-tag">EMS</span><span class="sys-tag">SCADA</span>
<span class="sys-tag">AMI</span><span class="sys-tag">DAS</span>
<span class="sys-tag">RTU</span><span class="sys-tag">FEP</span>
<span class="sys-tag">MOS</span><span class="sys-tag">DR</span>
</div>
""", unsafe_allow_html=True)

    st.markdown('<div class="sb-label">✉️ 메일 유형 선택</div>', unsafe_allow_html=True)

    for icon, label, trigger_msg in MAIL_TYPES:
        if st.button(f"{icon}  {label}", key=f"mail_{label}", use_container_width=True):
            st.session_state.trigger = trigger_msg
            # 새 메일 유형 선택 시 대화 초기화 후 시작
            st.session_state.messages = [
                {"role": "system", "content": SYSTEM_PROMPT}
            ]

    st.markdown("")
    if st.button("🗑️ 대화 초기화", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.trigger = None
        st.rerun()

    st.divider()
    st.caption("AI 답변은 초안 참고용입니다.\n실제 발송 전 내용을 반드시 검토하세요.")

# ── 메인 영역 ─────────────────────────────────────────────────
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

# 첫 화면 안내 카드
if not st.session_state.messages:
    st.markdown("""
<div class="welcome-card">
  <div class="w-title">👋 안녕하세요! KDN 업무 메일 도우미입니다.</div>
  왼쪽 사이드바에서 <b>메일 유형</b>을 선택하면 필요한 정보를 하나씩 물어본 뒤<br>
  완성된 메일 초안을 작성해 드립니다.<br><br>
  또는 아래 입력창에 직접 요청하셔도 됩니다.<br>
  <span class="w-tip">예시: "EMS 시스템 장애가 발생했는데 보고 메일을 작성해줘"</span>
</div>
""", unsafe_allow_html=True)

# 대화 히스토리 표시
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── 메일 유형 버튼 클릭 → 첫 메시지 처리 ─────────────────────
if st.session_state.trigger:
    user_text = st.session_state.trigger
    st.session_state.trigger = None

    st.session_state.messages.append({"role": "user", "content": user_text})
    with st.chat_message("user"):
        st.markdown(user_text)

    with st.chat_message("assistant"):
        try:
            response_text = st.write_stream(
                stream_response(client, st.session_state.messages)
            )
            st.session_state.messages.append(
                {"role": "assistant", "content": response_text}
            )
        except Exception as e:
            st.error(f"⚠️ 오류: {str(e)}")
    st.rerun()

# ── 사용자 직접 입력 ──────────────────────────────────────────
user_input = st.chat_input("답변을 입력하거나 직접 메일을 요청해 보세요...")

if user_input:
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
