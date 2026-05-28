import streamlit as st
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError
import os

st.set_page_config(page_title="KDN 업무 메일 도우미", page_icon="✉️", layout="wide")

# ── CSS ───────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

/* 폰트 – * 제외(Material Icons 보호) */
html, body, .stApp, .main,
h1, h2, h3, h4, h5, h6, p, label,
input, textarea, button,
[data-testid="stSidebar"],
[data-testid="stMarkdownContainer"],
[data-testid="stChatInput"] textarea {
    font-family: 'Noto Sans KR', sans-serif !important;
}

/* ══════════════════════════════════════
   배경 – 파란 계열 그라데이션
   ══════════════════════════════════════ */
.stApp {
    background: linear-gradient(160deg,
        #eff6ff 0%,
        #dbeafe 35%,
        #e0f2fe 65%,
        #f0f9ff 100%
    ) fixed !important;
}

.main .block-container {
    background: transparent !important;
    padding-top: 1.4rem !important;
    max-width: 860px !important;
}

/* ══════════════════════════════════════
   헤더 – 파란 계열
   ══════════════════════════════════════ */
.kdn-header {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 55%, #0ea5e9 100%);
    color: #fff;
    padding: 1.4rem 2rem;
    border-radius: 18px;
    margin-bottom: 1.2rem;
    box-shadow: 0 6px 28px rgba(37,99,235,0.28);
}
.kdn-header h1 { margin: 0 0 0.2rem; font-size: 1.5rem; font-weight: 700; letter-spacing: -0.3px; }
.kdn-header p  { margin: 0; font-size: 0.86rem; opacity: 0.88; }
.kdn-pill {
    display: inline-block;
    background: rgba(255,255,255,0.18);
    border: 1px solid rgba(255,255,255,0.35);
    border-radius: 30px;
    padding: 0.14rem 0.68rem;
    font-size: 0.7rem;
    font-weight: 600;
    margin-top: 0.5rem;
}

/* ══════════════════════════════════════
   사이드바
   ══════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: rgba(255,255,255,0.88) !important;
    backdrop-filter: blur(14px) !important;
    border-right: 1px solid #bfdbfe !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }

.sb-label {
    font-size: 0.69rem;
    font-weight: 700;
    color: #1d4ed8;
    text-transform: uppercase;
    letter-spacing: 1.1px;
    margin: 1rem 0 0.35rem;
    padding-left: 2px;
}

/* ── 프로필 카드 ── */
.profile-card {
    background: #eff6ff;
    border: 1.5px solid #bfdbfe;
    border-radius: 12px;
    padding: 0.8rem 1rem;
    font-size: 0.85rem;
    color: #1e3a5f;
    line-height: 1.65;
}
.profile-empty {
    color: #94a3b8;
    font-size: 0.82rem;
    font-style: italic;
}
.profile-name  { font-weight: 700; color: #1d4ed8; font-size: 0.92rem; }
.profile-sub   { color: #2563eb; font-size: 0.79rem; margin-top: 0.08rem; }
.profile-contact {
    font-size: 0.74rem;
    color: #3b82f6;
    margin-top: 0.4rem;
    padding-top: 0.35rem;
    border-top: 1px solid #bfdbfe;
}

/* ── 사이드바 입력 필드 ── */
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    background: #fff !important;
    border: 1.5px solid #bfdbfe !important;
    border-radius: 9px !important;
    font-size: 0.83rem !important;
    color: #1e3a5f !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.12) !important;
}
[data-testid="stSidebar"] label {
    font-size: 0.78rem !important;
    color: #475569 !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}

/* ── 사이드바 버튼 공통 ── */
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    background: #fff !important;
    color: #1e3a5f !important;
    border: 1.5px solid #bfdbfe !important;
    border-radius: 10px !important;
    font-size: 0.82rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 0.5rem 0.85rem !important;
    transition: all 0.15s ease !important;
    box-shadow: 0 1px 4px rgba(37,99,235,0.06) !important;
    margin-bottom: 3px !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: #eff6ff !important;
    border-color: #93c5fd !important;
    color: #1d4ed8 !important;
    box-shadow: 0 3px 10px rgba(37,99,235,0.13) !important;
    transform: translateX(2px) !important;
}

/* 수정/저장 소형 버튼 */
[data-testid="stSidebar"] [data-testid="stButton"].profile-action > button {
    text-align: center !important;
    padding: 0.3rem 0.6rem !important;
    font-size: 0.75rem !important;
    border-radius: 8px !important;
    transform: none !important;
}

/* 저장 버튼(primary) */
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"] {
    background: #2563eb !important;
    color: #fff !important;
    border-color: #2563eb !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"]:hover {
    background: #1d4ed8 !important;
    border-color: #1d4ed8 !important;
    transform: none !important;
}

/* 대화 초기화 버튼 */
[data-testid="stSidebar"] button[kind="secondary"] {
    background: #fff0f0 !important;
    color: #dc2626 !important;
    border-color: #fecaca !important;
}
[data-testid="stSidebar"] button[kind="secondary"]:hover {
    background: #fee2e2 !important;
    border-color: #fca5a5 !important;
    transform: none !important;
}

/* ══════════════════════════════════════
   채팅 메시지
   ══════════════════════════════════════ */
[data-testid="stChatMessage"] {
    border-radius: 16px !important;
    padding: 0.95rem 1.25rem !important;
    margin-bottom: 0.65rem !important;
    box-shadow: 0 1px 8px rgba(37,99,235,0.07) !important;
    transition: box-shadow 0.18s !important;
}
[data-testid="stChatMessage"]:hover {
    box-shadow: 0 3px 16px rgba(37,99,235,0.11) !important;
}

/* 사용자 – 흰색 */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    background: #ffffff !important;
    border: 1px solid #e2e8f0 !important;
}

/* 어시스턴트 – solid 밝은 파란색 */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    background: #dbeafe !important;
    border: 1px solid #bfdbfe !important;
}

/* ══════════════════════════════════════
   채팅 입력창
   ══════════════════════════════════════ */
[data-testid="stChatInput"] {
    background: #fff !important;
    border-radius: 14px !important;
    box-shadow: 0 3px 16px rgba(37,99,235,0.10) !important;
    border: 1.5px solid #bfdbfe !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    font-size: 0.91rem !important;
}

/* ══════════════════════════════════════
   웰컴 카드
   ══════════════════════════════════════ */
.welcome-card {
    background: #fff;
    border: 1px solid #bfdbfe;
    border-radius: 16px;
    padding: 1.3rem 1.7rem;
    color: #334155;
    font-size: 0.9rem;
    line-height: 1.8;
    margin-bottom: 1rem;
    box-shadow: 0 3px 18px rgba(37,99,235,0.07);
}
.welcome-card .w-title { font-size: 1rem; font-weight: 700; color: #1d4ed8; margin-bottom: 0.4rem; }
.welcome-card .w-tip {
    display: inline-block;
    background: #eff6ff;
    border: 1px solid #bfdbfe;
    border-radius: 8px;
    padding: 0.2rem 0.65rem;
    font-size: 0.81rem;
    color: #1d4ed8;
    margin-top: 0.3rem;
}

hr { border-color: #bfdbfe !important; }

/* ══════════════════════════════════════
   모바일 반응형
   ══════════════════════════════════════ */
@media (max-width: 768px) {
    .main .block-container {
        max-width: 100% !important;
        padding: 0.7rem 0.4rem 1.8rem !important;
    }
    .kdn-header { padding: 1rem 1.1rem; border-radius: 13px; margin-bottom: 0.8rem; }
    .kdn-header h1 { font-size: 1.12rem; }
    .kdn-header p  { font-size: 0.77rem; }
    [data-testid="stChatMessage"] {
        padding: 0.7rem 0.9rem !important;
        border-radius: 12px !important;
        margin-bottom: 0.45rem !important;
    }
    .welcome-card { padding: 1rem 1.1rem; border-radius: 13px; font-size: 0.84rem; }
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

# ── 시스템 프롬프트 ───────────────────────────────────────────
def build_system_prompt(sender: dict) -> str:
    mapping = [("name","이름"),("dept","부서"),("title","직급"),
               ("phone","연락처"),("email","이메일")]
    has_any = any(sender.get(k,"").strip() for k, _ in mapping)

    if has_any:
        lines = "\n".join(
            f"  - {lbl}: {sender.get(k,'').strip() or '[미입력]'}"
            for k, lbl in mapping
        )
        sender_block = f"**발신자 정보 (메일에 그대로 사용)**\n{lines}"
    else:
        sender_block = "**발신자 정보**: 미입력 — 발신자 항목은 모두 [ ] 형태로 비워 두세요."

    def v(key, fb=""):
        return sender.get(key, "").strip() or fb

    name  = v("name",  "[이름]")
    dept  = v("dept",  "[부서]")
    title = v("title", "[직급]")
    phone = v("phone", "[연락처]")
    email = v("email", "[이메일]")

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

**완성 메일 형식 (반드시 이 형식을 따르세요)**

제목: [내용에 맞는 적절한 제목]

수신: [수신자명] / [수신자 부서]
발신: {name} / {dept}
날짜: [작성일]

안녕하십니까, {dept} {name} {title}입니다.

[본문 내용 — 구체적이고 공식적인 한국어 문체]

감사합니다.
{name} 올림

---
서명
{name} | {dept} | {title}
{phone} | {email}
---

규칙:
- 제목은 내용을 잘 반영하는 구체적인 문장으로 작성
- 인사말은 반드시 "안녕하십니까, {dept} {name} {title}입니다."
- 마무리는 반드시 "감사합니다.\\n{name} 올림"
- 수신자 정보는 [수신자명/부서] 형태 유지
- 메일 완성 후 [ ] 항목 교체 안내"""

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
        model="gpt-4o", messages=messages, max_tokens=2048, stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            yield delta

# ── 세션 상태 초기화 ──────────────────────────────────────────
defaults = {
    "messages": [],
    "trigger": None,
    "sender": {"name":"","dept":"","title":"","phone":"","email":""},
    "editing_profile": False,
}
for k, val in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = val

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

    # ── 내 정보 헤더 행 (라벨 + 수정/저장 버튼) ──────────────
    s = st.session_state.sender
    has_info = any(v.strip() for v in s.values())

    lbl_col, btn_col = st.columns([3, 1])
    with lbl_col:
        st.markdown('<div class="sb-label">👤 내 정보</div>', unsafe_allow_html=True)
    with btn_col:
        st.markdown('<div style="margin-top:0.55rem"></div>', unsafe_allow_html=True)
        if st.session_state.editing_profile:
            if st.button("저장", key="btn_save", type="primary", use_container_width=True):
                st.session_state.editing_profile = False
                st.rerun()
        else:
            if st.button("수정", key="btn_edit", use_container_width=True):
                st.session_state.editing_profile = True
                st.rerun()

    # ── 프로필 카드 (보기 모드) ───────────────────────────────
    if not st.session_state.editing_profile:
        if has_info:
            phone_txt = f"📞 {s['phone']}" if s["phone"] else ""
            email_txt = f"✉ {s['email']}"  if s["email"] else ""
            contact   = "&nbsp;&nbsp;".join(filter(None, [phone_txt, email_txt]))
            st.markdown(f"""
<div class="profile-card">
  <div class="profile-name">{s['name'] or '–'} · {s['dept'] or '–'}</div>
  <div class="profile-sub">{s['title'] or '–'}</div>
  {f'<div class="profile-contact">{contact}</div>' if contact else ''}
</div>
""", unsafe_allow_html=True)
        else:
            st.markdown("""
<div class="profile-card">
  <span class="profile-empty">정보없음 — 수정 버튼을 눌러 입력하세요</span>
</div>
""", unsafe_allow_html=True)

    # ── 입력 폼 (수정 모드) ───────────────────────────────────
    else:
        st.session_state.sender["name"]  = st.text_input("이름",   value=s["name"],  placeholder="홍길동",         key="inp_name")
        st.session_state.sender["dept"]  = st.text_input("부서",   value=s["dept"],  placeholder="미터링시스템부",  key="inp_dept")
        st.session_state.sender["title"] = st.text_input("직급",   value=s["title"], placeholder="선임",           key="inp_title")
        st.session_state.sender["phone"] = st.text_input("연락처", value=s["phone"], placeholder="010-0000-0000",  key="inp_phone")
        st.session_state.sender["email"] = st.text_input("이메일", value=s["email"], placeholder="hong@kdn.com",   key="inp_email")

    # ── 메일 유형 ─────────────────────────────────────────────
    st.markdown('<div class="sb-label">✉️ 메일 유형 선택</div>', unsafe_allow_html=True)

    for icon, label, trigger_msg in MAIL_TYPES:
        if st.button(f"{icon}  {label}", key=f"mail_{label}", use_container_width=True):
            st.session_state.trigger  = trigger_msg
            st.session_state.messages = [
                {"role": "system", "content": build_system_prompt(st.session_state.sender)}
            ]

    st.markdown("")
    if st.button("🗑️ 대화 초기화", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.trigger  = None
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

# 첫 화면
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
