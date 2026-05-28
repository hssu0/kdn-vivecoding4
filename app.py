import streamlit as st
from openai import OpenAI, AuthenticationError, RateLimitError, APIConnectionError
import os, re, html as _html
from datetime import datetime

st.set_page_config(page_title="KDN 업무 메일 도우미", page_icon="✉️", layout="wide")

# ─────────────────────────────────────────────────────────────
#  Supabase 테이블 스키마 (초기 설정 시 SQL 편집기에서 실행)
# ─────────────────────────────────────────────────────────────
# CREATE TABLE IF NOT EXISTS profiles (
#     email TEXT PRIMARY KEY,
#     name  TEXT DEFAULT '', dept  TEXT DEFAULT '',
#     title TEXT DEFAULT '', phone TEXT DEFAULT '',
#     updated_at TIMESTAMPTZ DEFAULT NOW()
# );
# CREATE TABLE IF NOT EXISTS mail_history (
#     id UUID DEFAULT gen_random_uuid() PRIMARY KEY,
#     user_email TEXT NOT NULL,
#     subject TEXT DEFAULT '', content TEXT DEFAULT '',
#     created_at TIMESTAMPTZ DEFAULT NOW()
# );
# ALTER TABLE profiles    ENABLE ROW LEVEL SECURITY;
# ALTER TABLE mail_history ENABLE ROW LEVEL SECURITY;
# CREATE POLICY "anon_all" ON profiles     FOR ALL TO anon USING (true) WITH CHECK (true);
# CREATE POLICY "anon_all" ON mail_history FOR ALL TO anon USING (true) WITH CHECK (true);

# ─────────────────────────────────────────────────────────────
#  CSS  v5
# ─────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;600;700&display=swap');

html, body, .stApp, .main,
h1,h2,h3,h4,h5,h6,p,label,input,textarea,button,
[data-testid="stSidebar"],
[data-testid="stMarkdownContainer"],
[data-testid="stChatInput"] textarea {
    font-family: 'Noto Sans KR', sans-serif !important;
}

/* ── 페이지 배경 ── */
.stApp { background: #f0f5ff !important; }
.main .block-container {
    background: transparent !important;
    padding-top: 1.3rem !important;
    max-width: 820px !important;
}

/* ── 헤더 ── */
.kdn-header {
    background: linear-gradient(135deg, #1d4ed8 0%, #2563eb 60%, #38bdf8 100%);
    color: #fff; padding: 1.2rem 1.8rem; border-radius: 16px;
    margin-bottom: 1rem; box-shadow: 0 4px 20px rgba(37,99,235,.22);
}
.kdn-header h1 { margin:0 0 .15rem; font-size:1.38rem; font-weight:700; letter-spacing:-.3px; }
.kdn-header p  { margin:0; font-size:.83rem; opacity:.88; }
.kdn-pill {
    display:inline-block; background:rgba(255,255,255,.16);
    border:1px solid rgba(255,255,255,.3); border-radius:99px;
    padding:.1rem .6rem; font-size:.69rem; font-weight:600; margin-top:.45rem;
}

/* ── 사이드바 ── */
[data-testid="stSidebar"] {
    background: #ffffff !important;
    border-right: 1px solid #bfdbfe !important;
}
[data-testid="stSidebar"] > div:first-child { padding-top: 0.9rem; }

/* ── 섹션 레이블 ── */
.sb-label {
    font-size:.67rem; font-weight:700; color:#64748b;
    text-transform:uppercase; letter-spacing:1.2px;
    margin:1rem 0 .38rem; padding-left:2px;
}

/* ── 프로필 헤더 행 — 수정/저장 버튼 인라인 정렬 ── */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] {
    align-items: center !important;
    margin: 0.85rem 0 0.42rem !important;
    gap: 4px !important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div {
    padding-top: 0 !important; padding-bottom: 0 !important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
    [data-testid="stVerticalBlock"] { gap: 0 !important; }

/* 수정/저장 버튼 — '내 정보' 텍스트와 동일 크기(0.67rem) */
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
    [data-testid="stButton"] > button {
    font-size: .67rem !important;
    font-weight: 700 !important;
    padding: .13rem .38rem !important;
    min-height: 0 !important;
    line-height: 1.4 !important;
    border-radius: 5px !important;
    letter-spacing: .4px !important;
    margin-bottom: 0 !important;
    text-align: center !important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
    [data-testid="stButton"] > button[kind="primary"],
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
    [data-testid="stButton"] > button[kind="primaryFormSubmit"] {
    background: #2563eb !important; color: #fff !important;
    border-color: #2563eb !important;
}
[data-testid="stSidebar"] [data-testid="stHorizontalBlock"]
    [data-testid="stButton"] > button[kind="primary"]:hover {
    background: #1d4ed8 !important; border-color: #1d4ed8 !important;
}

/* ── 프로필 카드 (로얄블루 그라데이션) ── */
.profile-card {
    background: linear-gradient(135deg, #1e3a8a 0%, #1d4ed8 55%, #2563eb 100%);
    border: 1px solid #1d4ed8; border-radius: 12px;
    padding: .82rem 1rem; color: #e0eaff; line-height: 1.65;
    font-size: .83rem; box-shadow: 0 3px 14px rgba(29,78,216,.28);
}
.profile-empty { color: rgba(255,255,255,.65); font-size:.8rem; font-style:italic; }
.profile-name  { font-weight:700; color:#fff; font-size:.89rem; }
.profile-sub   { color:#bfdbfe; font-size:.76rem; margin-top:.04rem; }
.profile-contact {
    font-size:.71rem; color:#bfdbfe;
    margin-top:.35rem; padding-top:.3rem;
    border-top: 1px solid rgba(255,255,255,.22);
}

/* ── 사이드바 입력 ── */
[data-testid="stSidebar"] [data-testid="stTextInput"] input {
    background:#f8fafc !important; border:1px solid #bfdbfe !important;
    border-radius:7px !important; font-size:.81rem !important;
    color:#1e293b !important; font-family:'Noto Sans KR',sans-serif !important;
    padding:.34rem .6rem !important;
}
[data-testid="stSidebar"] [data-testid="stTextInput"] input:focus {
    border-color:#2563eb !important;
    box-shadow:0 0 0 3px rgba(37,99,235,.09) !important;
    background:#fff !important;
}
[data-testid="stSidebar"] label {
    font-size:.75rem !important; color:#64748b !important;
    font-family:'Noto Sans KR',sans-serif !important;
}

/* ── 사이드바 버튼 기본 ── */
[data-testid="stSidebar"] [data-testid="stButton"] > button {
    font-family:'Noto Sans KR',sans-serif !important;
    background:#fff !important; color:#334155 !important;
    border:1px solid #e2e8f0 !important; border-radius:8px !important;
    font-size:.8rem !important; font-weight:500 !important;
    text-align:left !important; padding:.46rem .78rem !important;
    transition:background .12s,border-color .12s !important;
    box-shadow:none !important; margin-bottom:3px !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button:hover {
    background:#eff6ff !important; border-color:#93c5fd !important; color:#1d4ed8 !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"] {
    background:#2563eb !important; color:#fff !important;
    border-color:#2563eb !important; text-align:center !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="primary"]:hover {
    background:#1d4ed8 !important; border-color:#1d4ed8 !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="secondary"] {
    background:#f8fafc !important; color:#64748b !important;
    border-color:#e2e8f0 !important; text-align:center !important;
}
[data-testid="stSidebar"] [data-testid="stButton"] > button[kind="secondary"]:hover {
    background:#f1f5f9 !important; color:#475569 !important;
}

/* ── Supabase 연동 버튼 (☁) ── */
[data-testid="stSidebar"] [data-key="btn_load"] > button,
[data-testid="stSidebar"] [data-key="btn_db_save"] > button {
    text-align: center !important;
    font-size: .78rem !important;
}

/* ── Expander (메인 & 사이드바 공통) ── */
[data-testid="stExpander"] {
    border:1px solid #bfdbfe !important; border-radius:8px !important;
    margin:.15rem 0 .45rem !important; overflow:hidden !important;
    background:#f8fbff !important;
}
[data-testid="stExpander"] details > summary {
    background:#eef5ff !important; font-size:.8rem !important;
    color:#2563eb !important; font-weight:600 !important;
    padding:.42rem .85rem !important;
    font-family:'Noto Sans KR',sans-serif !important; cursor:pointer !important;
}
[data-testid="stExpander"] details > summary:hover,
[data-testid="stExpander"] details[open] > summary { background:#dbeafe !important; }

/* 사이드바 Expander 세부 */
[data-testid="stSidebar"] [data-testid="stExpander"] {
    margin:.1rem 0 .25rem !important;
}
[data-testid="stSidebar"] [data-testid="stExpander"] details > summary {
    font-size:.74rem !important; padding:.3rem .6rem !important;
}

/* 기록 없음 텍스트 */
.sb-empty {
    font-size:.76rem; color:#94a3b8;
    padding:.25rem .25rem .5rem; font-style:italic;
}
/* Supabase 미설정 안내 */
.sb-hint {
    font-size:.72rem; color:#94a3b8; line-height:1.5;
    padding:.25rem .25rem .4rem;
}

/* ── 채팅 입력창 ── */
[data-testid="stChatInput"] {
    background:#fff !important; border-radius:12px !important;
    border:1.5px solid #bfdbfe !important;
    box-shadow:0 2px 10px rgba(37,99,235,.08) !important;
}
[data-testid="stChatInput"] textarea {
    background:transparent !important; border:none !important;
    font-size:.9rem !important; color:#1e293b !important;
}

@keyframes blink { 0%,100%{opacity:1} 50%{opacity:0} }
hr { border-color:#e2e8f0 !important; }

@media(max-width:768px){
    .main .block-container{max-width:100% !important;padding:.6rem .3rem 2rem !important;}
    .kdn-header{padding:.9rem 1rem;border-radius:12px;margin-bottom:.8rem;}
    .kdn-header h1{font-size:1.05rem;}
}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  Supabase 클라이언트
# ─────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def _get_sb():
    try:
        from supabase import create_client
        url = st.secrets["SUPABASE_URL"]
        key = st.secrets["SUPABASE_KEY"]
        return create_client(url, key)
    except Exception:
        return None

def sb_save_profile(sender: dict) -> bool:
    email = sender.get("email", "").strip()
    if not email:
        return False
    sb = _get_sb()
    if not sb:
        return False
    try:
        sb.table("profiles").upsert({
            "email": email,
            "name":  sender.get("name",  ""),
            "dept":  sender.get("dept",  ""),
            "title": sender.get("title", ""),
            "phone": sender.get("phone", ""),
        }).execute()
        return True
    except Exception:
        return False

def sb_load_data(email: str):
    """(success, message, profile_dict | None, history_list)"""
    sb = _get_sb()
    if not sb:
        return False, "Supabase가 설정되지 않았습니다.", None, []
    email = email.strip()
    if not email:
        return False, "이메일을 입력하세요.", None, []
    try:
        r = sb.table("profiles").select("*").eq("email", email).execute()
        if not r.data:
            return False, "해당 이메일로 저장된 정보가 없습니다.", None, []
        profile = r.data[0]
    except Exception as e:
        return False, f"오류: {e}", None, []

    history = []
    try:
        r2 = (sb.table("mail_history")
              .select("subject,content,created_at")
              .eq("user_email", email)
              .order("created_at", desc=True)
              .limit(20)
              .execute())
        for item in (r2.data or []):
            try:
                dt = datetime.fromisoformat(
                    item["created_at"].replace("Z", "+00:00")
                ).astimezone()
                ts = dt.strftime("%m/%d %H:%M")
            except Exception:
                ts = "–"
            history.append({
                "subject": item.get("subject", "메일 초안"),
                "content": item.get("content", ""),
                "time": ts,
            })
    except Exception:
        pass

    return True, f"프로필과 메일 기록 {len(history)}건을 불러왔습니다.", profile, history

def sb_save_mail(subject: str, content: str):
    email = st.session_state.sender.get("email", "").strip()
    if not email:
        return
    sb = _get_sb()
    if not sb:
        return
    try:
        sb.table("mail_history").insert({
            "user_email": email,
            "subject": subject,
            "content": content,
        }).execute()
    except Exception:
        pass

# ─────────────────────────────────────────────────────────────
#  마크다운 → HTML
# ─────────────────────────────────────────────────────────────
def md_to_html(text: str) -> str:
    t = _html.escape(text)
    t = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', t, flags=re.DOTALL)
    t = re.sub(r'\*([^*\n]+)\*', r'<em>\1</em>', t)
    t = re.sub(
        r'`([^`]+)`',
        r'<code style="background:#eff6ff;padding:.05em .3em;border-radius:4px;font-size:.85em">\1</code>',
        t
    )
    t = re.sub(r'(?m)^-{3,}$',
               '<hr style="border:none;border-top:1px solid #bfdbfe;margin:.5rem 0">', t)
    t = re.sub(r'(?m)^#{1,6} (.+)$', r'<strong>\1</strong>', t)
    blocks = re.split(r'\n{2,}', t)
    parts = []
    for b in blocks:
        b = b.strip()
        if not b:
            continue
        if b.startswith('<hr') or b.startswith('<strong>') or b.startswith('<em>'):
            parts.append(f'<div style="margin:.2rem 0">{b}</div>')
        else:
            parts.append('<p style="margin:0 0 .42rem">' + b.replace('\n', '<br>') + '</p>')
    return ''.join(parts)

# ─────────────────────────────────────────────────────────────
#  말풍선 HTML
# ─────────────────────────────────────────────────────────────
def bubble(role: str, content_html: str, streaming: bool = False) -> str:
    cursor = '<span style="opacity:.5;animation:blink 1s infinite">▌</span>' if streaming else ''
    if role == "user":
        return (
            '<div style="display:flex;justify-content:flex-end;padding:.1rem 0 .55rem">'
            '<div style="background:#ffffff;border:1px solid #bfdbfe;'
            'border-radius:14px 4px 14px 14px;padding:.82rem 1.1rem;'
            'max-width:75%;font-size:.9rem;line-height:1.72;color:#1e293b;'
            'word-break:break-word;box-shadow:0 1px 4px rgba(0,0,0,.05)">'
            f'{content_html}{cursor}</div></div>'
        )
    else:
        return (
            '<div style="display:flex;justify-content:flex-start;padding:.1rem 0 .55rem">'
            '<div style="background:#dbeafe;border:1px solid #bfdbfe;'
            'border-radius:4px 14px 14px 14px;padding:.82rem 1.1rem;'
            'max-width:75%;font-size:.9rem;line-height:1.72;color:#1e293b;'
            'word-break:break-word;box-shadow:0 1px 4px rgba(37,99,235,.08)">'
            f'{content_html}{cursor}</div></div>'
        )

def render_history():
    for msg in st.session_state.messages:
        if msg["role"] == "system":
            continue
        st.markdown(bubble(msg["role"], md_to_html(msg["content"])), unsafe_allow_html=True)
        if msg["role"] == "assistant" and "제목:" in msg["content"]:
            with st.expander("📋 메일 복사하기"):
                st.code(msg["content"], language="text")

# ─────────────────────────────────────────────────────────────
#  메일 기록 저장 (로컬 + Supabase)
# ─────────────────────────────────────────────────────────────
def save_to_history(content: str):
    m = re.search(r'제목:\s*(.+)', content)
    subject = m.group(1).strip() if m else "메일 초안"
    st.session_state.mail_history.insert(0, {
        "subject": subject,
        "content": content,
        "time": datetime.now().strftime("%m/%d %H:%M"),
    })
    sb_save_mail(subject, content)

# ─────────────────────────────────────────────────────────────
#  데이터
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
#  시스템 프롬프트
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

    def v(k, fb=""):
        return sender.get(k,"").strip() or fb

    n  = v("name","[이름]"); d  = v("dept","[부서]")
    tl = v("title","[직급]"); ph = v("phone","[연락처]"); em = v("email","[이메일]")

    return f"""당신은 한전KDN의 전력IT 전문가이자 업무 메일 작성 도우미입니다.

{sender_block}

**대화 방식**
- 메일 유형이 선택되면 필요한 정보를 한 번에 한 가지씩 친절하게 질문하세요.
- 각 답변 후 자연스럽게 다음 질문으로 넘어가세요.
- 모든 정보가 수집되면 "감사합니다! 지금 바로 메일 초안을 작성해 드릴게요. ✉️" 라고 말하고 완성된 메일을 작성하세요.

**메일 유형별 질문 순서**
[시스템 현황 보고] Q1.보고 시스템명 Q2.보고 기간 Q3.운영 현황 Q4.특이사항
[장애 보고] Q1.장애 시스템명 Q2.발생 일시 Q3.증상·영향 Q4.조치 상황
[회의 요청] Q1.안건 Q2.희망 일시 Q3.참석 대상 Q4.장소·방식
[점검 결과] Q1.점검 시스템명 Q2.점검 일시 Q3.결과 Q4.후속 조치
[작업 협조 요청] Q1.작업 내용 Q2.시스템명 Q3.일정 Q4.협조 부서·담당자
[자료 회신 요청] Q1.자료명·내용 Q2.필요 사유 Q3.기한 Q4.회신 방법

**완성 메일 형식 (반드시 준수)**

제목: [내용에 맞는 구체적인 제목]

수신: [수신자명] / [수신자 부서]
발신: {n} / {d}
날짜: [작성일]

안녕하십니까, {d} {n} {tl}입니다.

[본문 — 공식적이고 명확한 한국어 문체]

감사합니다.
{n} 올림

{n} | {d} | {tl} | {ph} | {em}

규칙:
- 서명 한 줄은 마크다운 서식(굵게, 헤딩 등) 없이 일반 텍스트로 작성
- 인사말 고정: "안녕하십니까, {d} {n} {tl}입니다."
- 마무리 고정: "감사합니다.\\n{n} 올림"
- 완성 후 [ ] 항목 교체 안내"""

# ─────────────────────────────────────────────────────────────
#  OpenAI
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

def stream_to_bubble(client, messages, placeholder):
    chunks = []
    stream = client.chat.completions.create(
        model="gpt-4o", messages=messages, max_tokens=2048, stream=True,
    )
    for chunk in stream:
        delta = chunk.choices[0].delta.content
        if delta:
            chunks.append(delta)
            partial = _html.escape("".join(chunks)).replace('\n', '<br>')
            placeholder.markdown(bubble("assistant", partial, streaming=True), unsafe_allow_html=True)
    resp = "".join(chunks)
    placeholder.markdown(bubble("assistant", md_to_html(resp)), unsafe_allow_html=True)
    return resp

# ─────────────────────────────────────────────────────────────
#  세션 상태
# ─────────────────────────────────────────────────────────────
for k, val in {
    "messages":        [],
    "trigger":         None,
    "sender":          {"name":"","dept":"","title":"","phone":"","email":""},
    "editing_profile": False,
    "mail_history":    [],
}.items():
    if k not in st.session_state:
        st.session_state[k] = val

# ─────────────────────────────────────────────────────────────
#  헤더
# ─────────────────────────────────────────────────────────────
st.markdown("""
<div class="kdn-header">
  <h1>✉️ KDN 업무 메일 도우미</h1>
  <p>필요한 정보를 대화로 수집한 후 완성된 메일 초안을 작성해 드립니다</p>
  <span class="kdn-pill">GPT-4o · 한전KDN 바이브코딩 4기</span>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────
#  사이드바
# ─────────────────────────────────────────────────────────────
with st.sidebar:
    s        = st.session_state.sender
    has_info = any(v.strip() for v in s.values())
    sb_ready = _get_sb() is not None

    # ── 내 정보 헤더 (레이블 + 수정/저장 버튼 같은 줄) ──
    lbl_col, btn_col = st.columns([4, 1])
    with lbl_col:
        st.markdown('<div class="sb-label" style="margin:0">👤 내 정보</div>',
                    unsafe_allow_html=True)
    with btn_col:
        if st.session_state.editing_profile:
            if st.button("저장", key="btn_save", type="primary", use_container_width=True):
                saved = sb_save_profile(st.session_state.sender)
                st.session_state.editing_profile = False
                if saved:
                    st.toast("☁ Supabase에 저장되었습니다.", icon="✅")
                st.rerun()
        else:
            if st.button("수정", key="btn_edit", use_container_width=True):
                st.session_state.editing_profile = True
                st.rerun()

    # ── 프로필 카드 / 편집 폼 ──
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
    else:
        st.session_state.sender["name"]  = st.text_input("이름",   value=s["name"],  placeholder="홍길동",         key="inp_name")
        st.session_state.sender["dept"]  = st.text_input("부서",   value=s["dept"],  placeholder="미터링시스템부",  key="inp_dept")
        st.session_state.sender["title"] = st.text_input("직급",   value=s["title"], placeholder="선임",           key="inp_title")
        st.session_state.sender["phone"] = st.text_input("연락처", value=s["phone"], placeholder="010-0000-0000",  key="inp_phone")
        st.session_state.sender["email"] = st.text_input("이메일", value=s["email"], placeholder="hong@kdn.com",   key="inp_email")

    # ── Supabase 불러오기 ──
    if sb_ready:
        with st.expander("☁ 저장된 정보 불러오기"):
            load_em = st.text_input(
                "이메일", placeholder="hong@kdn.com",
                key="inp_load_email", label_visibility="collapsed"
            )
            if st.button("불러오기", key="btn_load", use_container_width=True):
                ok, msg, profile, history = sb_load_data(load_em)
                if ok and profile:
                    st.session_state.sender = {
                        "name":  profile.get("name",  ""),
                        "dept":  profile.get("dept",  ""),
                        "title": profile.get("title", ""),
                        "phone": profile.get("phone", ""),
                        "email": profile.get("email", ""),
                    }
                    st.session_state.mail_history = history
                    st.success(msg)
                    st.rerun()
                else:
                    st.warning(msg)
    else:
        st.markdown(
            '<div class="sb-hint">☁ Supabase 미연동<br>'
            'SUPABASE_URL · SUPABASE_KEY를<br>Secrets에 추가하면 활성화됩니다.</div>',
            unsafe_allow_html=True
        )

    # ── 메일 유형 ──
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

    # ── 메일 기록 ──
    st.divider()
    st.markdown('<div class="sb-label" style="margin-top:.3rem">📁 메일 기록</div>',
                unsafe_allow_html=True)
    if st.session_state.mail_history:
        for item in st.session_state.mail_history[:8]:
            subj = item["subject"]
            label_text = (subj[:13] + "…") if len(subj) > 13 else subj
            with st.expander(f"{item['time']}  {label_text}"):
                st.code(item["content"], language="text")
    else:
        st.markdown('<div class="sb-empty">아직 작성된 메일이 없습니다.</div>',
                    unsafe_allow_html=True)

    st.divider()
    st.caption("AI 답변은 초안 참고용입니다.\n실제 발송 전 내용을 반드시 검토하세요.")

# ─────────────────────────────────────────────────────────────
#  메인 채팅 영역
# ─────────────────────────────────────────────────────────────
client = get_client()
if client is None:
    st.error(
        "⚠️ **OPENAI_API_KEY가 설정되지 않았습니다.**\n\n"
        "Streamlit Cloud → 앱 설정 → **Secrets** 탭:\n"
        "```toml\nOPENAI_API_KEY = \"sk-proj-...\"\n```"
    )
    st.stop()

if not st.session_state.messages:
    welcome = (
        "👋 안녕하세요! **KDN 업무 메일 도우미**입니다.\n\n"
        "왼쪽 사이드바에서 **내 정보**를 먼저 입력하시면 메일 서명이 자동으로 완성됩니다.  \n"
        "이후 **메일 유형**을 선택하면 필요한 정보를 하나씩 여쭤본 뒤 초안을 작성해 드립니다.\n\n"
        "💡 *작성된 메일 초안은 말풍선 아래 📋 버튼으로 바로 복사하실 수 있습니다.*"
    )
    st.markdown(bubble("assistant", md_to_html(welcome)), unsafe_allow_html=True)

render_history()

# ── 버튼 트리거 처리 ──
if st.session_state.trigger:
    user_text = st.session_state.trigger
    st.session_state.trigger = None
    st.session_state.messages.append({"role": "user", "content": user_text})
    st.markdown(bubble("user", md_to_html(user_text)), unsafe_allow_html=True)
    ph = st.empty()
    try:
        resp = stream_to_bubble(client, st.session_state.messages, ph)
        st.session_state.messages.append({"role": "assistant", "content": resp})
        if "제목:" in resp:
            save_to_history(resp)
    except AuthenticationError:
        ph.error("❌ API 키 인증 실패. OPENAI_API_KEY를 확인하세요.")
    except RateLimitError:
        ph.warning("⏳ 요청 한도 초과. 잠시 후 다시 시도해 주세요.")
    except APIConnectionError:
        ph.error("🌐 네트워크 오류. 인터넷 연결을 확인해 주세요.")
    except Exception as e:
        ph.error(f"⚠️ 오류: {str(e)}")
    st.rerun()

# ── 직접 입력 처리 ──
user_input = st.chat_input("답변을 입력하거나 직접 메일을 요청해 보세요...")
if user_input:
    if not st.session_state.messages:
        st.session_state.messages.append(
            {"role": "system", "content": build_system_prompt(st.session_state.sender)}
        )
    st.session_state.messages.append({"role": "user", "content": user_input})
    st.markdown(bubble("user", md_to_html(user_input)), unsafe_allow_html=True)
    ph = st.empty()
    try:
        resp = stream_to_bubble(client, st.session_state.messages, ph)
        st.session_state.messages.append({"role": "assistant", "content": resp})
        if "제목:" in resp:
            save_to_history(resp)
            with st.expander("📋 메일 복사하기", expanded=True):
                st.code(resp, language="text")
    except AuthenticationError:
        ph.error("❌ API 키 인증 실패. OPENAI_API_KEY를 확인하세요.")
    except RateLimitError:
        ph.warning("⏳ 요청 한도 초과. 잠시 후 다시 시도해 주세요.")
    except APIConnectionError:
        ph.error("🌐 네트워크 오류. 인터넷 연결을 확인해 주세요.")
    except Exception as e:
        ph.error(f"⚠️ 오류: {str(e)}")
