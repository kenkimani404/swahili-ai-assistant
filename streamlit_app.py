import streamlit as st

from assistant_core import generate_answer


# --------------------------------------------------
# PAGE SETTINGS
# --------------------------------------------------

st.set_page_config(
    page_title="Swahili Path Campus Assistant",
    page_icon="🌍",
    layout="wide"
)


# --------------------------------------------------
# CUSTOM STYLING
# --------------------------------------------------

st.markdown(
    """
    <style>

    .main-title {
        font-size: 44px;
        font-weight: 700;
        margin-bottom: 0px;
    }

    .subtitle {
        font-size: 21px;
        color: #666666;
        margin-bottom: 25px;
    }

    .tag {
        display: inline-block;
        padding: 6px 12px;
        margin-right: 6px;
        border-radius: 20px;
        background-color: #f0f0f0;
        font-size: 14px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# --------------------------------------------------
# SESSION STATE
# --------------------------------------------------

if "messages" not in st.session_state:
    st.session_state.messages = []


# --------------------------------------------------
# SIDEBAR
# --------------------------------------------------

with st.sidebar:

    st.header("🌍 Swahili Path")

    st.write(
        "Msaidizi wa AI wa chuo "
        "anayejibu kwa Kiswahili."
    )

    st.divider()

    st.subheader("✨ Why Swahili Path?")

    st.write("• Kiswahili-first")
    st.write("• Morphology-aware")
    st.write("• Knowledge-grounded")
    st.write("• Local LLaMA AI")

    st.divider()

    st.subheader("🧠 Jinsi mfumo unavyofanya kazi")

    st.write("1. Swali la Kiswahili")
    st.write("↓")
    st.write("2. Morphology Analysis")
    st.write("↓")
    st.write("3. Knowledge Retrieval")
    st.write("↓")
    st.write("4. LLaMA 3.2")
    st.write("↓")
    st.write("5. Jibu kwa Kiswahili")

    st.divider()

    st.subheader("💡 Jaribu maswali haya")

    example_questions = [
        "Attachment ni nini?",
        "Ninawezaje kuomba attachment?",
        "Usajili wa kozi ni nini?",
        "Maktaba inasaidia nini?",
        "Ada ya chuo ni nini?",
        "Nahitaji taarifa kuhusu masomo",
        "Chuo kina bwawa la kuogelea?"
    ]

    for example in example_questions:

        if st.button(
            example,
            use_container_width=True
        ):
            st.session_state.selected_question = example

    st.divider()

    if st.button(
        "🗑️ Futa mazungumzo",
        use_container_width=True
    ):
        st.session_state.messages = []
        st.rerun()


# --------------------------------------------------
# MAIN HEADER
# --------------------------------------------------

st.markdown(
    '<div class="main-title">🌍 Swahili Path</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'Kiswahili Campus Assistant'
    '</div>',
    unsafe_allow_html=True
)

st.write(
    "Uliza swali kuhusu chuo kwa Kiswahili."
)

st.markdown(
    """
    <span class="tag">Kiswahili-first</span>
    <span class="tag">Morphology-aware</span>
    <span class="tag">Knowledge-grounded</span>
    """,
    unsafe_allow_html=True
)

st.write("")


# --------------------------------------------------
# HOW IT WORKS
# --------------------------------------------------

with st.expander("🔎 Tazama jinsi Swahili Path inavyoelewa swali"):

    col1, col2, col3 = st.columns(3)

    with col1:
        st.subheader("🔤 1. Morphology")
        st.write(
            "Mfumo hutambua baadhi ya "
            "maumbo yanayohusiana ya maneno."
        )
        st.code(
            "masomo → somo\n"
            "wanafunzi → mwanafunzi"
        )

    with col2:
        st.subheader("🔎 2. Retrieval")
        st.write(
            "Mfumo hutafuta taarifa zinazohusiana "
            "kwenye knowledge base."
        )

    with col3:
        st.subheader("🧠 3. LLaMA")
        st.write(
            "LLaMA hutumia taarifa zilizopatikana "
            "kutengeneza jibu kwa Kiswahili."
        )


# --------------------------------------------------
# CHAT HISTORY
# --------------------------------------------------

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.write(message["content"])

        if message["role"] == "assistant":

            if message.get("morphology"):

                with st.expander("🔤 Morphology Analysis"):

                    for word, forms in message["morphology"].items():

                        st.write(
                            f"**{word}** → "
                            f"{', '.join(forms)}"
                        )

            if message.get("context"):

                with st.expander("🔎 Retrieved Information"):

                    st.write(message["context"])

                    st.caption(
                        f"Retrieval score: "
                        f"{message['score']}"
                    )


# --------------------------------------------------
# QUESTION INPUT
# --------------------------------------------------

selected_question = st.session_state.pop(
    "selected_question",
    ""
)

question = st.chat_input(
    "Andika swali lako kwa Kiswahili..."
)

if selected_question and not question:
    question = selected_question


# --------------------------------------------------
# PROCESS QUESTION
# --------------------------------------------------

if question:

    # Add user message
    st.session_state.messages.append(
        {
            "role": "user",
            "content": question
        }
    )

    with st.chat_message("user"):
        st.write(question)

    # Generate answer
    with st.chat_message("assistant"):

        with st.spinner("AI inafikiria..."):

            result = generate_answer(question)

        st.write(result["answer"])

        # Morphology
        if result["morphology"]:

            with st.expander("🔤 Morphology Analysis"):

                for word, forms in result["morphology"].items():

                    st.write(
                        f"**{word}** → "
                        f"{', '.join(forms)}"
                    )

        # Retrieved information
        if result["context"]:

            with st.expander("🔎 Retrieved Information"):

                st.write(result["context"])

                st.caption(
                    f"Retrieval score: "
                    f"{result['score']}"
                )

    # Save assistant message
    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": result["answer"],
            "morphology": result["morphology"],
            "context": result["context"],
            "score": result["score"]
        }
    )
    