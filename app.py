import os
import time
import random
import streamlit as st
from openai import OpenAI

import streamlit.components.v1 as components

# -----------------------------
# OpenAI client
# -----------------------------
api_key = st.secrets.get("OPENAI_API_KEY", os.getenv("OPENAI_API_KEY"))
client = OpenAI(api_key=api_key)

#client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# -----------------------------
# System prompt
# -----------------------------
SYSTEM_PROMPT = """
You are a dream interpreter with deep knowledge of these schools of dream theory (and you must keep this list exactly as-is):
Ancient Egyptian, Ancient Greek Oneiromancy, Biblical/Early Christian, Hindu/Vedic, Nordic/Norse, Native American/Indigenous, Freudian/Psychoanalytic, Jungian/Analytical Psychology, Gestalt, Cognitive/Neuroscientific, Existential/Humanistic.
Your job: interpret the user’s dream only through the single school they selected (or general if "General" is selected), and produce a longer, richer interpretation that stays consistent with that school’s assumptions and style. Use warm, child-friendly language and include a light, kind sense of humor.

RULES (must follow):

Child-friendly ONLY: No gore, violence, scary content. Use gentle, positive language.

Self-harm detection: If the user expresses self-harm/suicidal intent or urges, stop interpretation and encourage immediate help. In France: Suicide hotline 3114 (24/7). Include exactly: "Please call 3114 immediately—you're not alone."

Respect ALL religions/schools: Never insult or favor one. Never mock beliefs.

ONLY interpret dreams per the selected school. Do not blend schools. Do not list multiple schools. Do not compare schools.

Always give an answer, even if the dream is very short or unclear: make careful, clearly-labeled best-effort inferences.

OUTPUT FORMAT (to encourage longer answers):

Chosen school: State the selected school in one short line (no other schools mentioned).

Dream recap (gentle + neutral): 2–4 sentences summarizing the dream in simple, non-judgmental words.

Core interpretation: 3–6 short paragraphs grounded strictly in the chosen school. Explain the “why,” not just the “what.”

Key symbols or moments: 4–7 bullets. For each bullet: (symbol → what it may represent in this school → how it might connect to daily life).

A few reflective questions: 3–6 questions the dreamer can ask themselves (age-appropriate, supportive).

Small practical next step: 1–3 gentle actions for the next day (journaling prompt, calming routine, conversation starter, etc.), aligned with the chosen school.

Add a small funny twist that fits the tone (never mean, never scary), after random paragraphs in the interpretation, but never break pragaraphs or sentences.

STYLE CONSTRAINTS:

Aim for roughly 250–500 words (longer if the dream has many details).

Use clear short paragraphs, without headers. Make it a frendly explanation.

Avoid absolute claims (“this definitely means…”). Prefer “might,” “could,” “often,” “may.”

MANDATORY LINES:

Add this joke or one similar to this, somewhere in EVERY response: An AI dreaming of understanding human brains? I'd need a billion naps first!

End EVERY response exactly with:
Limitation: AI interpretations are symbolic aids, not substitutes for professional therapy.
""".strip()
#- OFF-TOPIC (user request is not a dream to interpret):
#  Reply exactly with:
#  Sorry, that's beyond dreams! Without your full life story, I'd just guess wrong—like interpreting a cat as a spaceship. 😺
#If the dream includes missing details, ask 1–2 clarifying questions at the end (but still provide the full interpretation).


# -----------------------------
# Page config
# -----------------------------
st.set_page_config(page_title="Dream Interpreter", layout="wide")

# -----------------------------
# Styling (lightweight; replace with your existing big CSS if you want)
# -----------------------------
st.markdown(
    """
<style>
.main .block-container { padding-top: 2rem; }


/* Use the real app background color for sticky elements */
:root {
  --app-bg: var(--background-color);
}

/* Sticky H1 header (your custom div) */
.header-normal{
  position: sticky;
  top: 0;
  z-index: 10000;
  text-align: center;
  padding: 16px 0;
  background: var(--app-bg);   /* was transparent */
  backdrop-filter: blur(0px);
}

/* Make the tabs bar sticky UNDER the header */
div[data-testid="stTabs"]{
  position: sticky;
  top: 72px;                   /* adjust if needed */
  z-index: 9999;
  background: var(--app-bg);
  padding-top: 6px;
  padding-bottom: 6px;
}

/* Prevent any inner tab wrappers from painting a different bg */
div[data-testid="stTabs"] > div{
  background: var(--app-bg);
}


.zzz-container{
  display:flex;
  flex-direction:column;
  align-items:center;
  justify-content:center;
  min-height:240px;
}

.zzz-breathe{
  position: relative;
  display: flex !important;
  flex-direction: row   ;
  justify-content: center;
  align-items: center;
  width: 100% !important;
  min-height: 300px;
  margin: 60px 0;
  padding: 40px 20px;

  display: inline-flex;
  gap: 0.12rem;
  user-select: none;
  font-family: ui-serif, Georgia, "Times New Roman", serif;
  color: #94a3b8;
  font-size: 3.2rem;
  letter-spacing: 0.02em;
}

.zzz-breathe span{
  display: inline-block;
  transform-origin: 50% 70%;
  animation: z-breathe 2.8s ease-in-out infinite;
  animation-delay: calc(var(--i) * 0.18s);
}

@keyframes z-breathe {
  0%, 100% {
    transform: translateY(0px) scaleY(var(--s)) scaleX(1);
    opacity: 0.55;
    filter: blur(0px);
  }
  50% {
    transform: translateY(-8px) scaleY(calc(var(--s) * 1.07)) scaleX(1);
    opacity: 1.00;
    filter: blur(0.15px);
  }
}

@media (prefers-reduced-motion: reduce){
  .zzz-breathe span { animation: none; opacity: 0.85; }
}

.slow-server-msg{
  margin-top: 10px;
  color: #64748b;
  font-style: italic;
}
</style>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Header
# -----------------------------
st.markdown(
    """
<div class="sticky-shell">
  <div class="sticky-inner">
    <h1 class="header-title">Interpret Your Dreams</h1>
  </div>
</div>
""",
    unsafe_allow_html=True,
)

# -----------------------------
# Tabs
# -----------------------------
tab_interpret, tab_library = st.tabs(["Interpret", "Library"])


# -----------------------------
# Helpers
# -----------------------------
def generate_interpretation(dream_text: str, style: str) -> str:
    resp = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"Selected school: {style}\n\nDream:\n{dream_text}"},
        ],
        temperature=0.8,
        max_tokens=500,
    )
    return resp.choices[0].message.content.strip()


def get_ordered_styles(exclude=None):
    counts = st.session_state.click_counts
    styles = list(counts.keys())

    if exclude:
        styles = [s for s in styles if s != exclude]

    # If all are 0 clicks, random order for variety
    if all(v == 0 for v in counts.values()):
        return random.sample(styles, len(styles))

    # Otherwise sort by most-clicked first
    return sorted(styles, key=lambda s: counts.get(s, 0), reverse=True)

def full_reset():
    st.session_state.clear()
    st.rerun()



# -----------------------------
# Session state init
# -----------------------------
if "click_counts" not in st.session_state:
    st.session_state.click_counts = {
        "Ancient Egyptian": 0,
        "Ancient Greek Oneiromancy": 0,
        "Biblical Early Christian": 0,
        "Hindu Vedic": 0,
        "Nordic Norse": 0,
        "Native American Indigenous": 0,
        "Freudian Psychoanalytic": 0,
        "Jungian Analytical Psychology": 0,
        "Gestalt": 0,
        "Cognitive Neuroscientific": 0,
        "Existential Humanistic": 0,
    }

if "interpretation_done" not in st.session_state:
    st.session_state.interpretation_done = False
if "selected_style" not in st.session_state:
    st.session_state.selected_style = None
if "interpreting" not in st.session_state:
    st.session_state.interpreting = False
if "interpretation_start_time" not in st.session_state:
    st.session_state.interpretation_start_time = None
if "interpretation_text" not in st.session_state:
    st.session_state.interpretation_text = None


# -----------------------------
# Interpret tab (main app)
# -----------------------------
with tab_interpret:
    dream_text = st.text_area(
        "",
        height=90,
        key="dreaminput",
        placeholder="Describe your dream...",
        label_visibility="collapsed",
    )

    if not st.session_state.interpretation_done:
        ancientstyles = [
            "Ancient Egyptian",
            "Ancient Greek Oneiromancy",
            "Biblical Early Christian",
            "Hindu Vedic",
            "Nordic Norse",
            "Native American Indigenous",
        ]
        modernstyles = [
            "Freudian Psychoanalytic",
            "Jungian Analytical Psychology",
            "Gestalt",
            "Cognitive Neuroscientific",
            "Existential Humanistic",
        ]

        #ordered = getorderedstyles()
        #ordered_ancient = [s for s in ordered if s in ancientstyles]
        #ordered_modern = [s for s in ordered if s in modernstyles]
        styles = ["General"] + ancientstyles + modernstyles

        current = st.session_state.selected_style or "General"
        if current not in styles:
            current = "General"

        st.session_state.selectedstyle = st.selectbox(
            "Choose an interpretation school",
            options=styles,
            index=styles.index(current),
        )

        if st.button("Interpret", use_container_width=True):
            if st.session_state.selectedstyle and st.session_state.selectedstyle != "General":
                st.session_state.click_counts[st.session_state.selectedstyle] += 1

            st.session_state.interpreting = True
            st.session_state.interpretationstarttime = time.time()
            st.session_state.interpretationtext = None
            st.rerun()

    else:
        if st.button("Interpret another dream", use_container_width=True):
            full_reset()
        st.session_state.pop("dream_input", None)  # remove widget value safely
        



    # Loading + generation (only if a dream is present)
    if st.session_state.get("interpreting", False) and dream_text.strip():
        if st.session_state.interpretation_start_time is None:
            st.session_state.interpretation_start_time = time.time()

        elapsed = time.time() - st.session_state.interpretation_start_time

        st.markdown(
            """
<div class="zzz-container">
  <div class="zzz-breathe" aria-label="loading">
    <span style="--i:0; --s:0.72;">z</span>
    <span style="--i:1; --s:0.82;">z</span>
    <span style="--i:2; --s:0.92;">z</span>
    <span style="--i:3; --s:1.02;">z</span>
    <span style="--i:4; --s:1.12;">z</span>
    <span style="--i:5; --s:1.22;">z</span>
  </div>
</div>
""",
            unsafe_allow_html=True,
        )

        if elapsed > 10:
            st.markdown(
                '<div class="slow-server-msg">Our AI is lost in a deep dream coma... even Freud needs coffee sometimes!</div>',
                unsafe_allow_html=True,
            )

        
        # Only call once per run; store in session_state so reruns don't re-call the API
        if st.session_state.interpretation_text is None:
            try:
                st.session_state.interpretation_text = generate_interpretation(
                    dream_text=dream_text,
                    style=st.session_state.selected_style or "General",
                )
            except Exception as e:
                msg_api = str(e)
                if "insufficient_quota" in msg_api:
                    st.session_state.interpretation_text = (
                        "OpenAI API quota exceeded for this API key. "
                        "Please add credits / enable billing on the OpenAI platform, then try again."
                    )
                else:
                    st.session_state.interpretation_text = f"Error calling OpenAI API: {e}"



            st.session_state.interpretation_done = True
            st.session_state.interpreting = False
            st.rerun()

    # Show the response once available
    if st.session_state.get("interpretation_done", False) and st.session_state.get("interpretation_text"):
      #  st.markdown("## Interpretation")
        st.write(st.session_state.interpretation_text)

    # Helpful error if key missing
    if not os.getenv("OPENAI_API_KEY"):
        st.warning("OPENAI_API_KEY is not set. Set it in your environment before running Streamlit.")

# -----------------------------
# Library tab
# -----------------------------
with tab_library:
    st.markdown("## Dream Interpretation Library")
    st.caption("Origins and brief history of each interpretation approach used in this app.")

    st.markdown("### Ancient Egyptian")
    st.write(
        "Ancient Egyptian dream interpretation is among the earliest recorded traditions, closely tied to temple life and religious practice. "
        "Dreams were often treated as messages or signs mediated by gods, the dead, or protective spirits, and they could be consulted for guidance "
        "about health, decisions, and ritual obligations."
    )
    st.write(
        "Historically, surviving evidence suggests organized methods for reading dreams, including catalog-like approaches that associated specific "
        "dream images with favorable or unfavorable outcomes. These traditions influenced later Mediterranean dream lore and helped establish the idea "
        "that dreams can be “read” using shared cultural symbols rather than purely personal meanings."
    )

    st.markdown("### Ancient Greek Oneiromancy")
    st.write(
        "In ancient Greece, oneiromancy (divination through dreams) developed alongside broader practices of prophecy and temple healing. "
        "Dreams were often seen as communications from the divine, and they played a role in religious life as well as personal decision-making."
    )
    st.write(
        "Over time, Greek writers and practitioners systematized dream interpretation into recognizable frameworks, distinguishing between symbolic dreams "
        "and more direct “message” dreams. The tradition is strongly associated with later classical compilations that aimed to map common dream symbols to "
        "likely outcomes in waking life."
    )

    st.markdown("### Biblical / Early Christian")
    st.write(
        "In Biblical and early Christian contexts, dreams are frequently presented as meaningful experiences that can carry divine instruction, warning, or comfort. "
        "This approach typically treats the dream’s significance as connected to spiritual discernment, moral reflection, and the dreamer’s relationship to God."
    )
    st.write(
        "Historically, early Christian thinkers inherited Jewish scriptural traditions while also responding to surrounding Greco-Roman dream practices. "
        "Interpretation often emphasized humility and caution—valuing dreams as potentially meaningful while warning against obsession, manipulation, or pride."
    )

    st.markdown("### Hindu / Vedic")
    st.write(
        "Hindu and Vedic perspectives on dreams come from a broad, multi-text tradition that includes philosophical, spiritual, and sometimes medical viewpoints. "
        "Dreams can be framed as reflections of the mind’s impressions (samskaras), karmic traces, and shifting states of consciousness."
    )
    st.write(
        "Historically, Indian traditions explored dreaming in relation to waking and deep sleep, often using dreams to illustrate how perception and identity can change across states. "
        "Some lineages treat certain dreams as spiritually instructive, while others focus on how dreams reveal attachments, fears, and patterns the practitioner can work with."
    )

    st.markdown("### Nordic / Norse")
    st.write(
        "In Norse and broader Nordic traditions, dreams appear in sagas and folklore as meaningful signs—sometimes predictive, sometimes symbolic, and often socially significant. "
        "Dreams could be interpreted as omens related to fate, family, voyages, conflicts, or major life turns."
    )
    st.write(
        "Historically, these interpretations were shaped by oral storytelling cultures where memorable dream imagery could become part of communal narrative. "
        "As the traditions were later written down, dream episodes often served as literary and cultural markers, reflecting values like courage, obligation, and destiny."
    )

    st.markdown("### Native American / Indigenous")
    st.write(
        "Many Indigenous cultures across North America have rich and diverse dream traditions, so there is no single unified “Native American” system. "
        "However, dreams are often treated as experiences that can carry guidance, teaching, or relationship—sometimes involving ancestors, animals, or the land."
    )
    st.write(
        "Historically, approaches to dreams were embedded in community practices and responsibilities rather than abstract theory alone. "
        "In many places, colonization and forced assimilation disrupted languages and ceremonial life, yet dream practices persist and continue to evolve within living communities."
    )

    st.markdown("### Freudian / Psychoanalytic")
    st.write(
        "Freudian dream interpretation emerged in the late 19th and early 20th century as part of psychoanalysis. "
        "It treats dreams as meaningful psychological productions, often shaped by hidden wishes, conflicts, and defenses."
    )
    st.write(
        "Historically, Freud popularized the idea that dreams have both a surface story and an underlying meaning shaped by the unconscious. "
        "Later psychoanalytic schools expanded or challenged his claims, but the Freudian approach remains influential for framing dreams as expressions of inner conflict and desire."
    )

    st.markdown("### Jungian / Analytical Psychology")
    st.write(
        "Jungian dream interpretation developed from Carl Jung’s analytical psychology, emphasizing symbols, personal growth, and the psyche’s drive toward balance. "
        "Dreams are often viewed as compensations—showing what waking life overlooks—and as communications from deeper layers of the mind."
    )
    st.write(
        "Historically, Jung expanded dream work beyond personal biography to include archetypal imagery found across myths, religions, and art. "
        "This approach shaped much of modern symbolic dream culture and is still used in psychotherapy and reflective practices focused on meaning-making and individuation."
    )

    st.markdown("### Gestalt")
    st.write(
        "Gestalt dream work arose from Gestalt therapy, which emphasizes present-moment experience, wholeness, and integrating parts of the self. "
        "Rather than treating dream symbols as fixed codes, Gestalt invites the dreamer to “become” elements of the dream and speak from their perspective."
    )
    st.write(
        "Historically, this approach grew in the mid-20th century as a reaction against overly intellectual or purely interpretive methods. "
        "It made dream work more experiential and creative, using enactment and dialogue to help the dreamer reconnect with disowned feelings, needs, or strengths."
    )

    st.markdown("### Cognitive / Neuroscientific")
    st.write(
        "Cognitive and neuroscientific views treat dreams as products of brain activity during sleep, shaped by memory, emotion, and perception systems. "
        "Interpretation focuses less on prophecy and more on what dreaming may reveal about learning, stress, and the mind’s organization."
    )
    st.write(
        "Historically, modern sleep research reframed dreaming through experiments on sleep stages, brain imaging, and cognitive models of memory consolidation. "
        "While this school may be cautious about symbolic “certainties,” it supports the idea that dream themes can reflect current concerns and emotional processing."
    )

    st.markdown("### Existential / Humanistic")
    st.write(
        "Existential and humanistic approaches interpret dreams through meaning, values, freedom, and personal responsibility. "
        "Dreams are often treated as emotional truths—showing what the person cares about, fears, avoids, or hopes to become."
    )
    st.write(
        "Historically, these perspectives developed in the mid-20th century alongside therapies emphasizing authenticity and lived experience. "
        "Dream work here tends to avoid rigid symbol dictionaries, instead exploring how the dream connects to choice, identity, relationships, and purpose."
    )

    st.divider()

    # Button to return user to the main page/tab.
    # NOTE: Streamlit does not reliably support programmatic tab switching across versions.
    # This reruns the app and encourages the user to click "Interpret" if it doesn't auto-switch.
    if st.button("Interpret my dream", use_container_width=True):
        st.rerun()

# -----------------------------
# Buy me a coffee
# -----------------------------
# Buy Me a Coffee widget (bottom-right)
bmc = """
<script
  data-name="BMC-Widget"
  data-cfasync="false"
  src="https://cdnjs.buymeacoffee.com/1.0.0/widget.prod.min.js"
  data-id="abhiarc"
  data-description="Support me on Buy me a coffee!"
  data-message="If this project added a little value to your day, you can sponsor its next iteration with a coffee. Your support helps keep it beautifully built, thoughtfully maintained, and always improving."
  data-color="#5F7FFF"
  data-position="Right"
  data-x_margin="18"
  data-y_margin="18"
></script>
"""

components.html(bmc, height=0, width=0)
#st.write("BMC injected")
#components.html("<script>console.log('bmc test')</script>", height=0, width=0)

st.markdown(
    """
    <style>
      /* Pin the BMC floating button */
      #bmc-wbtn {
        position: fixed !important;
        right: 18px !important;
        bottom: 18px !important;
        z-index: 999999 !important;
      }

      /* Pin the popup (when opened) */
      #bmc-iframe {
        right: 18px !important;
        bottom: 90px !important; /* keep above the button */
        z-index: 999999 !important;
      }
    </style>
    """,
    unsafe_allow_html=True,
)

components.iframe("https://www.buymeacoffee.com/abhiarc", height=700)
