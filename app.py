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

/*
  ★ * 선택자 대신 명시적 타겟만 지정
    → Streamlit이 expander 아이콘에 쓰는 Material Symbols 폰트를 건드리지 않음
*/
html, body, .stApp, .main,
h1, h2, h3, h4, h5, h6, p, label,
input, textarea, button,
[data-testid="stSidebar"],
[data-testid="stMarkdownContainer"],
[data-testid="stChatInput"] textarea {
    font-family: 'Noto Sans KR', sans-serif !important;
}

/* ═══ 전체 배경 그라데이션 ═══ */
.stApp {
    background: linear-gradient(145deg,
        #e8eeff 0%,
        #f0ebff 22%,
        #fde8f5 45%,
        #ddeeff 70%,
        #d8f5ee 100%
    ) fixed !important;
}

/* ═══ 메인 컨테이너 ═══ */
.main .block-container {
    background: transparent !important;
    padding-top: 1.5rem !important;
    max-width: 860px !important;
}

/* ═══ 헤더 ═══ */
.kdn-header {
    background: linear-gradient(135deg, #7c3aed 0%, #4f46e5 45%, #0ea5e9 100%);
    color: white;
    padding: 1.4rem 2rem;
    border-radius: 20px;
    margin-bottom: 1.2rem;
    box-shadow: 0 8px 32px rgba(99,102,241,0.28);
}
.kdn-header h1 {
    margin: 0 0 0.2rem;
    font-size: 1.5rem;
    font-weight: 700;
    letter-spacing: -0.4px;
}
.kdn-header p { margin: 0; font-size: 0.87rem; opacity: 0.85; }
.kdn-pill {
    display: inline-block;
    background: rgba(255,255,255,0.20);
    border: 1px solid rgba(255,255,255,0.35);
    border-radius: 30px;
    padding: 0.15rem 0.7rem;
    font-size: 0.71rem;
    font-weight: 600;
    margin-top: 0.55rem;
}

/* ═══ 사이드바 ═══ */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.80) !important;
    backdrop-filter: blur(14px) !important;
    border-right: 1px solid rgba(200,200,255,0.4) !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1.1rem; }

/* 섹션 라벨 */
.sb-label {
    font-size: 0.7rem;
    font-weight: 700;
    color: #6d28d9;
    text-transform: uppercase;
    letter-spacing: 1.1px;
    margin: 1.1rem 0 0.4rem;
    padding-left: 2px;
}

/* ═══ 발신자 카드 (아바타 없음) ═══ */
.sender-card {
    background: linear-gradient(135deg, #ede9fe 0%, #dbeafe 100%);
    border: 1.5px solid #a78bfa;
    border-radius: 14px;
    padding: 0.85rem 1rem;
    margin-bottom: 0.4rem;
    overflow: hidden;
}
.saved-badge {
    display: inline-block;
    background: #dcfce7;
    color: #16a34a;
    border-radius: 20px;
    padding: 0.08rem 0.5rem;
    font-size: 0.68rem;
    font-weight: 700;
    float: right;
    margin-top: 0.1rem;
}
.sender-name {
    font-size: 0.92rem;
    font-weight: 700;
    color: #3730a3;
    margin-bottom: 0.12rem;
}
.sender-sub { font-size: 0.79rem; color: #5b21b6; }
.sender-contact {
    font-size: 0.74rem;
    color: #6d28d9;
    margin-top: 0.45rem;
    padding-top: 0.4rem;
    border-top: 1px solid rgba(167,139,250,0.35);
    opacity: 0.88;
}

/* ═══ 사이드바 입력 필드 ═══ */
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    background: rgba(255,255,255,0.92) !important;
    border: 1.5px solid rgba(167,139,250,0.38) !important;
    border-radius: 10px !important;
    font-size: 0.83rem !important;
    color: #1f2937 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus {
    border-color: #7c3aed !important;
    box-shadow: 0 0 0 3px rgba(124,58,237,0.13) !important;
}
[data-testid="stSidebar"] label {
    font-size: 0.79rem !important;
    color: #4b5563 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}

/* ═══ 사이드바 버튼 ═══ */
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: rgba(255,255,255,0.88) !important;
    color: #374151 !important;
    border: 1.5px solid rgba(167,139,250,0.30) !important;
    border-radius: 12px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 0.52rem 0.85rem !important;
    transition: all 0.16s ease !important;
    box-shadow: 0 1px 6px rgba(109,40,217,0.06) !important;
    margin-bottom: 3px !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: linear-gradient(135deg, #ede9fe, #dbeafe) !important;
    border-color: #a78bfa !important;
    color: #5b21b6 !important;
    box-shadow: 0 3px 12px rgba(109,40,217,0.14) !important;
    transform: translateX(3px) !important;
}
[data-testid="stSidebar"] button[kind="secondary"] {
    background: rgba(254,226,226,0.72) !important;
    color: #dc2626 !important;
    border-color: rgba(252,165,165,0.5) !important;
}
[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background: #fee2e2 !important;
    border-color: #fca5a5 !important;
    transform: none !important;
}

/* ═══ 채팅 메시지 공통 ═══ */
[data-testid="stChatMessage"] {
    border-radius: 18px !important;
    padding: 1rem 1.3rem !important;
    margin-bottom: 0.7rem !important;
    box-shadow: 0 2px 14px rgba(80,80,180,0.07) !important;
    transition: box-shadow 0.2s !important;
}
[data-testid="stChatMessage"]:hover {
    box-shadow: 0 4px 20px rgba(80,80,180,0.12) !important;
}

/* 사용자 메시지 – 흰색 */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: rgba(255,255,255,0.96) !important;
    border: 1px solid rgba(209,213,219,0.55) !important;
}

/* 어시스턴트 메시지 – 밝은 블루 */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: rgba(214,234,255,0.82) !important;
    border: 1px solid rgba(125,190,255,0.40) !important;
}

/* ═══ 채팅 입력창 ═══ */
[data-testid="stChatInput"] {
    background: rgba(255,255,255,0.88) !important;
    border-radius: 16px !important;
    box-shadow: 0 4px 20px rgba(99,102,241,0.11) !important;
    border: 1.5px solid rgba(167,139,250,0.38) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    font-size: 0.91rem !important;
}

/* ═══ 웰컴 카드 ═══ */
.welcome-card {
    background: rgba(255,255,255,0.78);
    border: 1px solid rgba(167,139,250,0.22);
    border-radius: 18px;
    padding: 1.4rem 1.8rem;
    color: #374151;
    font-size: 0.9rem;
    line-height: 1.8;
    margin-bottom: 1rem;
    box-shadow: 0 4px 22px rgba(109,40,217,0.07);
}
.welcome-card .w-title {
    font-size: 1.02rem;
    font-weight: 700;
    color: #5b21b6;
    margin-bottom: 0.45rem;
}
.welcome-card .w-tip {
    display: inline-block;
    background: linear-gradient(135deg, #ede9fe, #dbeafe);
    border-radius: 8px;
    padding: 0.22rem 0.65rem;
    font-size: 0.82rem;
    color: #4f46e5;
    margin-top: 0.35rem;
}

hr { border-color: rgba(167,139,250,0.18) !important; }

/* ════════════════════════════════════════
   모바일 반응형 (≤ 768px)
   ════════════════════════════════════════ */
@media (max-width: 768px) {
    .main .block-container {
        max-width: 100% !important;
        padding: 0.7rem 0.5rem 1.8rem !important;
    }
    .kdn-header {
        padding: 1rem 1.1rem;
        border-radius: 14px;
        margin-bottom: 0.85rem;
    }
    .kdn-header h1 { font-size: 1.15rem; }
    .kdn-header p  { font-size: 0.78rem; }
    .kdn-pill      { font-size: 0.65rem; padding: 0.12rem 0.55rem; }

    [data-testid="stChatMessage"] {
        padding: 0.75rem 0.95rem !important;
        border-radius: 14px !important;
        margin-bottom: 0.5rem !important;
    }
    .welcome-card {
        padding: 1rem 1.1rem;
        border-radius: 14px;
        font-size: 0.85rem;
        line-height: 1.7;
    }
    .welcome-card .w-title { font-size: 0.95rem; }
}
</style>
""", unsafe_allow_html=True)

# ── 메일 유형 ─────────────────────────────────────────────────
MAIL_TYPES = [
    ("📊", "시스템 현황 보고",  "시스템 현황 보고 메일을 작성하고 싶습니다."),
    ("🚨", "장애 보고",        "장애 보고 메일을 작성하고 싶습니다."),
    ("📅", "회의 요청",        "회의 요청 메일을 작성하고 싶습니다."),
    ("🔍", "점검 결과",        "점검 결과 보고 메일을 작성하고 싶습니다."),
    ("🤝", "작업 협조 요청",   "작업 협조 요청 메일을 작성하고 싶습니다."),
    ("📨", "자료 회신 요청",   "자료 회신 요청 메일을 작성하고 싶습니다."),
]

# ── 시스템 프롬프트 빌더 ──────────────────────────────────────
def build_system_prompt(sender: dict) -> str:
    mapping = [("name","이름"),("dept","부서"),("title","직급"),
               ("phone","연락처"),("email","이메일")]
    has_any = any(sender.get(k, "").strip() for k, _ in mapping)

    if has_any:
        lines = "\n".join(
            f"  - {lbl}: {sender.get(k,'').strip() or '[미입력]'}"
            for k, lbl in mapping
        )
        sender_block = f"**발신자 정보 (메일 서명·발신란에 그대로 사용)**\n{lines}"
    else:
        sender_block = "**발신자 정보**: 미입력 — 발신자 항목은 모두 [ ] 로 비워 두세요."

    def v(key, fallback=""):
        return sender.get(key, "").strip() or fallback

    return f"""당신은 한전KDN의 전력IT 전문가이자 업무 메일 작성 도우미입니다.

{sender_block}

**대화 방식**
- 메일 유형이 선택되면 필요한 정보를 **한 번에 한 가지씩** 친절하게 질문하세요.
- 각 답변 후 자연스럽게 다음 질문으로 넘어가세요.
- 모든 정보가 수집되면 "감사합니다! 지금 바로 메일 초안을 작성해 드릴게요. ✉️" 라고 말하고 완성된 메일을 작성하세요.

**메일 유형별 필요 정보**

[시스템 현황 보고]
Q1. 어떤 시스템의 현황을 보고하시나요? (예: EMS, SCADA, AMI)
Q2. 보고 기간이 언제인가요?
Q3. 주요 운영 현황을 알려주세요. (가동률, 상태 등)
Q4. 특이사항이나 이슈가 있나요? (없으면 "없음")

[장애 보고]
Q1. 장애가 발생한 시스템명은 무엇인가요?
Q2. 장애 발생 일시는 언제인가요?
Q3. 장애 증상과 영향 범위를 설명해 주세요.
Q4. 현재 조치 상황은 어떻게 되나요?

[회의 요청]
Q1. 회의 목적 또는 안건은 무엇인가요?
Q2. 희망하는 회의 일시가 있으신가요?
Q3. 참석 대상은 누구인가요? (부서 또는 직책)
Q4. 회의 장소 또는 방식은 어떻게 되나요? (온라인/오프라인)

[점검 결과]
Q1. 점검한 시스템명은 무엇인가요?
Q2. 점검 일시는 언제인가요?
Q3. 점검 결과를 간단히 설명해 주세요.
Q4. 후속 조치가 필요한 사항이 있나요? (없으면 "없음")

[작업 협조 요청]
Q1. 협조가 필요한 작업 내용은 무엇인가요?
Q2. 관련 시스템명은 무엇인가요?
Q3. 협조 요청 일정은 언제인가요?
Q4. 협조를 요청할 부서 또는 담당자는 누구인가요?

[자료 회신 요청]
Q1. 요청하는 자료명 또는 내용은 무엇인가요?
Q2. 자료가 필요한 사유는 무엇인가요?
Q3. 회신 기한은 언제인가요?
Q4. 회신 방법은 어떻게 해주시면 되나요?

**메일 완성 형식**
제목: [시스템명/안건] 관련 [메일유형] 건

수신: [수신자명] / [수신자 부서]
발신: {v('name','[이름]')} / {v('dept','[부서]')}
날짜: [작성일]

안녕하십니까, {v('dept','[부서]')}입니다.

[본문 내용]

감사합니다.

{v('name','[이름]')}
{v('dept','[부서]')} | {v('title','[직급]')}
{v('phone','[연락처]')} | {v('email','[이메일]')}

규칙:
- 공식적이고 명확한 한국어 문체 사용
- 수신자 정보는 [수신자명/부서] 형태로 표시
- 메일 완성 후 [ ] 항목을 실제 정보로 교체하라고 안내"""

# ── API ───────────────────────────────────────────────────────
def get_client():
    api_key = None
    try:
        api_key = st.secrets["OPENAI_API_KEY"]
    except Exception:
        api_key = os.environ.get("OPENAI_API_KEY")
    if not api_key:
        return None
    return OpenAI(api_key=api_key)

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
if "sender" not in st.session_state:
    st.session_state.sender = {"name":"","dept":"","title":"","phone":"","email":""}

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

    st.markdown('<div class="sb-label">👤 내 정보</div>', unsafe_allow_html=True)

    s = st.session_state.sender
    has_info = any(v.strip() for v in s.values())

    # 저장된 정보 → 프로필 카드 (아바타 없음)
    if has_info:
        phone_line = f"📞 {s['phone']}" if s["phone"] else ""
        email_line = f"✉ {s['email']}" if s["email"] else ""
        contact = "&nbsp;&nbsp;".join(filter(None, [phone_line, email_line]))
        st.markdown(f"""
<div class="sender-card">
  <span class="saved-badge">✓ 저장됨</span>
  <div class="sender-name">{s['name'] or '–'} · {s['dept'] or '–'}</div>
  <div class="sender-sub">{s['title'] or '–'}</div>
  {f'<div class="sender-contact">{contact}</div>' if contact else ''}
</div>
""", unsafe_allow_html=True)

    with st.expander("✏️ 정보 입력 / 수정", expanded=not has_info):
        st.session_state.sender["name"]  = st.text_input("이름",   value=s["name"],  placeholder="홍길동",          key="inp_name")
        st.session_state.sender["dept"]  = st.text_input("부서",   value=s["dept"],  placeholder="미터링시스템부",   key="inp_dept")
        st.session_state.sender["title"] = st.text_input("직급",   value=s["title"], placeholder="선임",            key="inp_title")
        st.session_state.sender["phone"] = st.text_input("연락처", value=s["phone"], placeholder="010-0000-0000",   key="inp_phone")
        st.session_state.sender["email"] = st.text_input("이메일", value=s["email"], placeholder="hong@kdn.com",    key="inp_email")

    st.markdown('<div class="sb-label">✉️ 메일 유형 선택</div>', unsafe_allow_html=True)

    for icon, label, trigger_msg in MAIL_TYPES:
        if st.button(f"{icon}  {label}", key=f"mail_{label}", use_container_width=True):
            st.session_state.trigger = trigger_msg
            st.session_state.messages = [
                {"role": "system", "content": build_system_prompt(st.session_state.sender)}
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
        "Streamlit Cloud → 앱 설정 → **Secrets** 탭:\n"
        "```toml\nOPENAI_API_KEY = \"sk-proj-...\"\n```"
    )
    st.stop()

# 첫 화면 안내
if not st.session_state.messages:
    st.markdown("""
<div class="welcome-card">
  <div class="w-title">👋 안녕하세요! KDN 업무 메일 도우미입니다.</div>
  왼쪽 사이드바에서 <b>내 정보</b>를 먼저 입력하시면 메일 서명이 자동으로 완성됩니다.<br>
  이후 <b>메일 유형</b>을 선택하면 필요한 정보를 하나씩 여쭤본 뒤 초안을 작성해 드립니다.<br><br>
  <span class="w-tip">💡 내 정보는 새 메일을 작성할 때마다 자동으로 반영됩니다</span>
</div>
""", unsafe_allow_html=True)

# 대화 히스토리
for msg in st.session_state.messages:
    if msg["role"] == "system":
        continue
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 버튼 클릭 → 첫 AI 응답
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
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        except Exception as e:
            st.error(f"⚠️ 오류: {str(e)}")
    st.rerun()

# 직접 입력
user_input = st.chat_input("답변을 입력하거나 직접 메일을 요청해 보세요...")

if user_input:
    if not st.session_state.messages:
        st.session_state.messages.append(
            {"role": "system", "content": build_system_prompt(st.session_state.sender)}
        )
    st.session_state.messages.append({"role": "user", "content": user_input})
    with st.chat_message("user"):
        st.markdown(user_input)
    with st.chat_message("assistant"):
        try:
            response_text = st.write_stream(
                stream_response(client, st.session_state.messages)
            )
            st.session_state.messages.append({"role": "assistant", "content": response_text})
        except AuthenticationError:
            st.error("❌ API 키 인증 실패. OPENAI_API_KEY를 확인하세요.")
        except RateLimitError:
            st.warning("⏳ 요청 한도 초과. 잠시 후 다시 시도해 주세요.")
        except APIConnectionError:
            st.error("🌐 네트워크 오류. 인터넷 연결을 확인해 주세요.")
        except Exception as e:
            st.error(f"⚠️ 오류: {str(e)}")
