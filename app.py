import streamlit as st
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError
import os

st.set_page_config(page_title="KDN 업무 메일 도우미", page_icon="✉️", layout="wide")

# ─────────────────────────────────────────────────────────────
#  CSS  v2
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

/* 폰트 (Material Icons 보호: * 제외) */
html, body, .stApp, .main,
h1,h2,h3,h4,h5,h6,p,label,
input,textarea,button,
[data-testid="stSidebar"],
[data-testid="stMarkdownContainer"],
[data-testid="stChatInput"] textarea {
    font-family: 'Noto Sans KR', sans-serif !important;
}

/* ═══════════════════════════════════════════
   PAGE
   ═══════════════════════════════════════════ */
.stApp {
    background: #f0f5ff !important;
}
.main .block-container {
    background: transparent !important;
    padding-top: 1.4rem !important;
    max-width: 820px !important;
}

/* ═══════════════════════════════════════════
   HEADER
   ═══════════════════════════════════════════ */
.kdn-header {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 60%, #38bdf8 100%);
    color: #fff;
    padding: 1.3rem 1.8rem;
    border-radius: 16px;
    margin-bottom: 1.1rem;
    box-shadow: 0 4px 20px rgba(37,99,235,0.22);
}
.kdn-header h1 {
    margin: 0 0 0.15rem;
    font-size: 1.42rem;
    font-weight: 700;
    letter-spacing: -0.3px;
}
.kdn-header p  { margin: 0; font-size: 0.84rem; opacity: 0.88; }
.kdn-pill {
    display: inline-block;
    background: rgba(255,255,255,0.16);
    border: 1px solid rgba(255,255,255,0.32);
    border-radius: 99px;
    padding: 0.12rem 0.65rem;
    font-size: 0.69rem;
    font-weight: 600;
    margin-top: 0.5rem;
}

/* ═══════════════════════════════════════════
   SIDEBAR
   ═══════════════════════════════════════════ */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #bfdbfe !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 1rem; }

/* 섹션 라벨 */
.sb-label {
    font-size: 0.67rem;
    font-weight: 700;
    color: #64748b;
    text-transform: uppercase;
    letter-spacing: 1.2px;
    margin: 1.1rem 0 0.4rem;
    padding-left: 2px;
}

/* 프로필 카드 */
.profile-card {
    background: #bfdbfe;
    border: 1px solid #93c5fd;
    border-radius: 10px;
    padding: 0.8rem 0.95rem;
    color: #1e3a5f;
    line-height: 1.6;
    font-size: 0.84rem;
}
.profile-empty { color: #64748b; font-size: 0.81rem; }
.profile-name  { font-weight: 700; color: #1e40af; font-size: 0.9rem; }
.profile-sub   { color: #2563eb; font-size: 0.77rem; margin-top: 0.05rem; }
.profile-contact {
    font-size: 0.72rem; color: #1d4ed8;
    margin-top: 0.38rem; padding-top: 0.33rem;
    border-top: 1px solid #93c5fd;
}

/* 사이드바 입력 */
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    background: #f8fafc !important;
    border: 1px solid #bfdbfe !important;
    border-radius: 8px !important;
    font-size: 0.82rem !important;
    color: #1e293b !important;
    font-family: 'Noto Sans KR', sans-serif !important;
    padding: 0.38rem 0.65rem !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus {
    border-color: #2563eb !important;
    box-shadow: 0 0 0 3px rgba(37,99,235,0.09) !important;
    background: #fff !important;
}
[data-testid="stSidebar"] label {
    font-size: 0.76rem !important;
    color: #64748b !important;
    font-family: 'Noto Sans KR', sans-serif !important;
}

/* ── 사이드바 버튼 기본 ── */
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    font-family: 'Noto Sans KR', sans-serif !important;
    background: #fff !important;
    color: #334155 !important;
    border: 1px solid #e2e8f0 !important;
    border-radius: 8px !important;
    font-size: 0.81rem !important;
    font-weight: 500 !important;
    text-align: left !important;
    padding: 0.48rem 0.8rem !important;
    transition: background 0.13s, border-color 0.13s, color 0.13s !important;
    box-shadow: none !important;
    margin-bottom: 3px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background: #eff6ff !important;
    border-color: #93c5fd !important;
    color: #1d4ed8 !important;
    box-shadow: none !important;
    transform: none !important;
}

/* 저장(primary) */
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"] {
    background: #2563eb !important;
    color: #fff !important;
    border-color: #2563eb !important;
    font-weight: 600 !important;
    text-align: center !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"]:hover {
    background: #1d4ed8 !important;
    border-color: #1d4ed8 !important;
}

/* 수정 버튼 – 작게 */
[data-testid="stSidebar"] [data-key="btn_edit"] > button,
[data-testid="stSidebar"] [data-key="btn_save"] > button {
    text-align: center !important;
    padding: 0.3rem 0.5rem !important;
    font-size: 0.76rem !important;
}

/* 대화 초기화 – 중립 회색 */
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="secondary"] {
    background: #f8fafc !important;
    color: #64748b !important;
    border-color: #e2e8f0 !important;
    text-align: center !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="secondary"]:hover {
    background: #f1f5f9 !important;
    color: #475569 !important;
    border-color: #cbd5e1 !important;
}

/* ═══════════════════════════════════════════
   CHAT  –  아이콘 제거 + 말풍선 정렬
   ═══════════════════════════════════════════ */

/* 1) 아이콘(아바타) 완전 제거 */
[data-testid="stChatMessageAvatar"] {
    display: none !important;
}

/* 2) 메시지 래퍼 – 투명 컨테이너 */
[data-testid="stChatMessage"] {
    background: transparent !important;
    border: none !important;
    box-shadow: none !important;
    padding: 0 !important;
    margin-bottom: 0.55rem !important;
    display: flex !important;
    align-items: flex-start !important;
    gap: 0 !important;
}

/* 3) 공통 말풍선 스타일 */
[data-testid="stChatMessageContent"] {
    border-radius: 14px !important;
    padding: 0.82rem 1.1rem !important;
    line-height: 1.72 !important;
    flex: 0 0 auto !important;   /* ← 핵심: 너비 자동으로 줄어듦 */
    width: auto !important;
    max-width: 76% !important;
    min-width: 80px !important;
    word-break: break-word !important;
    box-shadow: 0 1px 4px rgba(0,0,0,0.06) !important;
}

/* 4) 어시스턴트 – 왼쪽, 파랑 */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) {
    justify-content: flex-start !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"])
  [data-testid="stChatMessageContent"] {
    background: #dbeafe !important;
    border: 1px solid #bfdbfe !important;
    border-radius: 4px 14px 14px 14px !important;
}

/* 5) 사용자 – 오른쪽, 흰색 */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) {
    justify-content: flex-end !important;
}
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"])
  [data-testid="stChatMessageContent"] {
    background: #ffffff !important;
    border: 1px solid #bfdbfe !important;
    border-radius: 14px 4px 14px 14px !important;
}

/* ═══════════════════════════════════════════
   CHAT INPUT
   ═══════════════════════════════════════════ */
[data-testid="stChatInput"] {
    background: #fff !important;
    border-radius: 12px !important;
    border: 1.5px solid #bfdbfe !important;
    box-shadow: 0 2px 12px rgba(37,99,235,0.08) !important;
}
[data-testid="stChatInput"] textarea {
    background: transparent !important;
    border: none !important;
    font-size: 0.9rem !important;
    color: #1e293b !important;
}

/* ═══════════════════════════════════════════
   MISC
   ═══════════════════════════════════════════ */
hr { border-color: #e2e8f0 !important; }

/* ═══════════════════════════════════════════
   모바일 반응형
   ═══════════════════════════════════════════ */
@media (max-width: 768px) {
    .main .block-container {
        max-width: 100% !important;
        padding: 0.6rem 0.3rem 2rem !important;
    }
    .kdn-header { padding: 0.95rem 1.1rem; border-radius: 12px; margin-bottom: 0.8rem; }
    .kdn-header h1 { font-size: 1.08rem; }
    [data-testid="stChatMessageContent"] {
        max-width: 88% !important;
        padding: 0.7rem 0.9rem !important;
    }
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  DATA
# ─────────────────────────────────────────────────────────────
MAIL_TYPES = [
    ("📊", "시스템 현황 보고",  "시스템 현황 보고 메일을 작성하고 싶습니다."),
    ("🚨", "장애 보고",        "장애 보고 메일을 작성하고 싶습니다."),
    ("📅", "회의 요청",        "회의 요청 메일을 작성하고 싶습니다."),
    ("🔍", "점검 결과",        "점검 결과 보고 메일을 작성하고 싶습니다."),
    ("🤝", "작업 협조 요청",   "작업 협조 요청 메일을 작성하고 싶습니다."),
    ("📨", "자료 회신 요청",   "자료 회신 요청 메일을 작성하고 싶습니다."),
]

# ─────────────────────────────────────────────────────────────
#  SYSTEM PROMPT
# ─────────────────────────────────────────────────────────────
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
        return sender.get(key,"").strip() or fb

    name  = v("name",  "[이름]");  dept  = v("dept",  "[부서]")
    title = v("title", "[직급]");  phone = v("phone", "[연락처]")
    email = v("email", "[이메일]")

    return f"""당신은 한전KDN의 전력IT 전문가이자 업무 메일 작성 도우미입니다.

{sender_block}

**대화 방식**
- 메일 유형이 선택되면 필요한 정보를 **한 번에 한 가지씩** 친절하게 질문하세요.
- 각 답변 후 자연스럽게 다음 질문으로 넘어가세요.
- 모든 정보가 수집되면 "감사합니다! 지금 바로 메일 초안을 작성해 드릴게요. ✉️" 라고 말하고 완성된 메일을 작성하세요.

**메일 유형별 필요 정보**

[시스템 현황 보고] Q1.보고 시스템명 Q2.보고 기간 Q3.주요 운영 현황 Q4.특이사항(없으면 "없음")
[장애 보고] Q1.장애 시스템명 Q2.장애 발생 일시 Q3.증상·영향 범위 Q4.현재 조치 상황
[회의 요청] Q1.회의 목적·안건 Q2.희망 일시 Q3.참석 대상 Q4.장소·방식(온/오프라인)
[점검 결과] Q1.점검 시스템명 Q2.점검 일시 Q3.점검 결과 Q4.후속 조치(없으면 "없음")
[작업 협조 요청] Q1.작업 내용 Q2.관련 시스템명 Q3.협조 일정 Q4.협조 부서·담당자
[자료 회신 요청] Q1.요청 자료명·내용 Q2.필요 사유 Q3.회신 기한 Q4.회신 방법

**완성 메일 형식 (반드시 준수)**

제목: [내용에 맞는 구체적인 제목]

수신: [수신자명] / [수신자 부서]
발신: {name} / {dept}
날짜: [작성일]

안녕하십니까, {dept} {name} {title}입니다.

[본문 — 공식적이고 명확한 한국어 문체]

감사합니다.
{name} 올림

---
{name} | {dept} | {title}
{phone} | {email}
---

규칙:
- 인사말 형식 고정: "안녕하십니까, {dept} {name} {title}입니다."
- 마무리 형식 고정: "감사합니다.\\n{name} 올림"
- 수신자는 [수신자명/부서] 유지
- 완성 후 [ ] 항목 교체 안내"""

# ─────────────────────────────────────────────────────────────
#  API
# ─────────────────────────────────────────────────────────────
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

# ─────────────────────────────────────────────────────────────
#  SESSION STATE
# ─────────────────────────────────────────────────────────────
for k, val in {
    "messages": [], "trigger": None,
    "sender": {"name":"","dept":"","title":"","phone":"","email":""},
    "editing_profile": False,
}.items():
    if k not in st.session_state:
        st.session_state[k] = val

# ─────────────────────────────────────────────────────────────
#  HEADER
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="kdn-header">
  <h1>✉️ KDN 업무 메일 도우미</h1>
  <p>필요한 정보를 대화로 수집한 후 완성된 메일 초안을 작성해 드립니다</p>
  <span class="kdn-pill">GPT-4o · 한전KDN 바이브코딩 4기</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  SIDEBAR
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    s        = st.session_state.sender
    has_info = any(v.strip() for v in s.values())

    # 내 정보 헤더 + 수정/저장 버튼
    lbl_col, btn_col = st.columns([3, 1])
    with lbl_col:
        st.markdown('<div class="sb-label">👤 내 정보</div>', unsafe_allow_html=True)
    with btn_col:
        st.markdown('<div style="margin-top:0.5rem"></div>', unsafe_allow_html=True)
        if st.session_state.editing_profile:
            if st.button("저장", key="btn_save", type="primary", use_container_width=True):
                st.session_state.editing_profile = False
                st.rerun()
        else:
            if st.button("수정", key="btn_edit", use_container_width=True):
                st.session_state.editing_profile = True
                st.rerun()

    # 보기 모드
    if not st.session_state.editing_profile:
        if has_info:
            pt = f"📞 {s['phone']}" if s["phone"] else ""
            em = f"✉ {s['email']}"  if s["email"] else ""
            ct = "&nbsp;&nbsp;".join(filter(None, [pt, em]))
            st.markdown(f"""
<div class="profile-card">
  <div class="profile-name">{s['name'] or '–'} · {s['dept'] or '–'}</div>
  <div class="profile-sub">{s['title'] or '–'}</div>
  {f'<div class="profile-contact">{ct}</div>' if ct else ''}
</div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
<div class="profile-card">
  <span class="profile-empty">정보없음 — 수정을 눌러 입력하세요</span>
</div>""", unsafe_allow_html=True)

    # 수정 모드
    else:
        st.session_state.sender["name"]  = st.text_input("이름",   value=s["name"],  placeholder="홍길동",         key="inp_name")
        st.session_state.sender["dept"]  = st.text_input("부서",   value=s["dept"],  placeholder="미터링시스템부",  key="inp_dept")
        st.session_state.sender["title"] = st.text_input("직급",   value=s["title"], placeholder="선임",           key="inp_title")
        st.session_state.sender["phone"] = st.text_input("연락처", value=s["phone"], placeholder="010-0000-0000",  key="inp_phone")
        st.session_state.sender["email"] = st.text_input("이메일", value=s["email"], placeholder="hong@kdn.com",   key="inp_email")

    # 메일 유형
    st.markdown('<div class="sb-label">✉️ 메일 유형</div>', unsafe_allow_html=True)
    for icon, label, trigger_msg in MAIL_TYPES:
        if st.button(f"{icon}  {label}", key=f"mail_{label}", use_container_width=True):
            st.session_state.trigger  = trigger_msg
            st.session_state.messages = [
                {"role": "system", "content": build_system_prompt(st.session_state.sender)}
            ]

    st.markdown("")
    if st.button("↺  대화 초기화", use_container_width=True, type="secondary"):
        st.session_state.messages = []
        st.session_state.trigger  = None
        st.rerun()

    st.divider()
    st.caption("AI 답변은 초안 참고용입니다.\n실제 발송 전 내용을 반드시 검토하세요.")

# ─────────────────────────────────────────────────────────────
#  MAIN
# ─────────────────────────────────────────────────────────────
client = get_client()
if client is None:
    st.error(
        "⚠️ **OPENAI_API_KEY가 설정되지 않았습니다.**\n\n"
        "Streamlit Cloud → 앱 설정 → **Secrets** 탭:\n"
        "```toml\nOPENAI_API_KEY = \"sk-proj-...\"\n```"
    )
    st.stop()

# 첫 화면 웰컴 – 어시스턴트 버블
if not st.session_state.messages:
    with st.chat_message("assistant"):
        st.markdown(
            "👋 안녕하세요! **KDN 업무 메일 도우미**입니다.\n\n"
            "왼쪽 사이드바에서 **내 정보**를 먼저 입력하시면 메일 서명이 자동으로 완성됩니다.  \n"
            "이후 **메일 유형**을 선택하면 필요한 정보를 하나씩 여쭤본 뒤 초안을 작성해 드립니다.\n\n"
            "💡 *내 정보는 새 메일을 작성할 때마다 자동으로 반영됩니다.*"
        )

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
            resp = st.write_stream(stream_response(client, st.session_state.messages))
            st.session_state.messages.append({"role": "assistant", "content": resp})
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
            resp = st.write_stream(stream_response(client, st.session_state.messages))
            st.session_state.messages.append({"role": "assistant", "content": resp})
        except AuthenticationError:
            st.error("❌ API 키 인증 실패. OPENAI_API_KEY를 확인하세요.")
        except RateLimitError:
            st.warning("⏳ 요청 한도 초과. 잠시 후 다시 시도해 주세요.")
        except APIConnectionError:
            st.error("🌐 네트워크 오류. 인터넷 연결을 확인해 주세요.")
        except Exception as e:
            st.error(f"⚠️ 오류: {str(e)}")
