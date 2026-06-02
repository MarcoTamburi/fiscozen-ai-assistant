import streamlit as st
from customer import CustomerRepository
from knowledge import KnowledgeBase
from chat import ChatSession

st.set_page_config(
    page_title="Fiscozen AI Assistant",
    page_icon="🟢",
    layout="centered",
)

# ── stile minimale ────────────────────────────────────────────────────────────
st.markdown("""
<style>
.escalation-box {
    background: #fff8e1;
    border-left: 4px solid #f9a825;
    padding: 12px 16px;
    border-radius: 6px;
    margin-top: 4px;
    font-size: 0.95rem;
}
.profile-box {
    background: #f0faf5;
    border-left: 4px solid #1D9E75;
    padding: 10px 14px;
    border-radius: 6px;
    font-size: 0.9rem;
}
</style>
""", unsafe_allow_html=True)


# ── caricamento risorse (cached) ──────────────────────────────────────────────
@st.cache_resource
def load_resources():
    kb = KnowledgeBase(data_dir="data")
    repo = CustomerRepository(excel_path="data/customer_data.xlsx")
    return kb, repo


kb, repo = load_resources()


# ── sidebar: selezione cliente ────────────────────────────────────────────────
with st.sidebar:
    st.image("https://www.fiscozen.it/favicon.ico", width=32)
    st.title("Fiscozen AI")
    st.caption("Assistente fiscale interno · demo")

    names = repo.get_display_names()
    selected = st.selectbox("Cliente loggato", options=names)
    customer = repo.get_by_name(selected)

    if customer:
        st.markdown(f"""
<div class="profile-box">
<b>{customer.full_name}</b><br>
Regime: {customer.regime}<br>
Cassa: {customer.cassa}<br>
Commercialista: {customer.commercialista}<br>
Fatturato 2026: {customer.fatturato_2026}k€
{f"<br>⚠️ Margine limite: <b>{customer.soglia_rimanente:.1f}k€</b>" if customer.is_forfettario else ""}
</div>
""", unsafe_allow_html=True)

    if st.button("🔄 Nuova conversazione"):
        st.session_state.pop("session", None)
        st.session_state.pop("messages", None)
        st.rerun()


# ── sessione chat ─────────────────────────────────────────────────────────────
if "session" not in st.session_state or st.session_state.get("current_customer") != selected:
    st.session_state.session = ChatSession(customer=customer, kb=kb)
    st.session_state.messages = []
    st.session_state.current_customer = selected

session: ChatSession = st.session_state.session


# ── area messaggi ─────────────────────────────────────────────────────────────
st.markdown(f"### Ciao, {customer.nome}! Come posso aiutarti?")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        if msg.get("escalation"):
            st.markdown(
                f'<div class="escalation-box">⚠️ {msg["content"]}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.write(msg["content"])


# ── input ─────────────────────────────────────────────────────────────────────
if prompt := st.chat_input("Scrivi la tua domanda..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner(""):
            response, is_escalation = session.send(prompt)

        if is_escalation:
            st.markdown(
                f'<div class="escalation-box">⚠️ {response}</div>',
                unsafe_allow_html=True,
            )
        else:
            st.write(response)

    st.session_state.messages.append({
        "role": "assistant",
        "content": response,
        "escalation": is_escalation,
    })
