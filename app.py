import pandas as pd
import streamlit as st
from pathlib import Path

st.set_page_config(page_title="SignalDesk Health Check", page_icon="📊", layout="centered")

DATA_PATH = Path(__file__).parent / "decision_table.csv"


@st.cache_data
def load_data(path):
    df = pd.read_csv(path)
    required = {
        "workflow", "source", "status", "sessions_pre_change",
        "sessions_post_change", "completion_rate_change",
        "acceptance_rate_change", "review_flag_rate_change", "reasons"
    }
    missing = required - set(df.columns)
    if missing:
        raise ValueError(f"decision_table.csv is missing: {', '.join(sorted(missing))}")
    return df


def next_action(row):
    actions = {
        ("Reply draft", "queue"): (
            "Pause broader rollout for this workflow/source. Review a small sample of "
            "accepted and flagged outputs, then confirm whether the review-policy change "
            "affected the post-change comparison."
        ),
        ("Reply draft", "manual"): (
            "Review a small sample of flagged outputs to understand why acceptance improved "
            "while review flags also increased."
        ),
        ("Feedback clustering", "csv upload"): (
            "Inspect recent CSV-upload inputs and failed/incomplete runs before changing the "
            "workflow or expanding use."
        ),
        ("Feedback clustering", "manual"): (
            "Collect more comparable pre- and post-change usage before making a rollout decision."
        ),
        ("Lead summary", "manual"): (
            "Keep this workflow in a monitored pilot and re-check the same metrics with another "
            "week of normal usage."
        ),
        ("Lead summary", "email"): (
            "Continue monitoring. There is no material movement in the current short comparison window."
        ),
    }
    return actions.get(
        (row["workflow"], row["source"]),
        "Review the underlying records and collect another comparable reporting period before rollout."
    )


def delta_text(value, favorable_when):
    if pd.isna(value):
        return "Not available", "off"
    direction = "up" if value > 0 else "down" if value < 0 else "unchanged"
    is_favorable = (value > 0 and favorable_when == "up") or (value < 0 and favorable_when == "down")
    color = "normal" if is_favorable else "inverse" if value != 0 else "off"
    return f"{value:+.1f} pp ({direction})", color


try:
    df = load_data(DATA_PATH)
except FileNotFoundError:
    st.error("Place decision_table.csv in the same folder as app.py, then run the app again.")
    st.stop()
except ValueError as error:
    st.error(str(error))
    st.stop()

st.title("SignalDesk Prompt Health Check")
st.caption("A lightweight pre/post comparison to prioritize the next rollout investigation.")

st.info(
    "Use case: a product teammate selects one workflow and source to decide whether "
    "the observed post-change signals look promising, need investigation, or remain inconclusive."
)

options = df.apply(lambda row: f"{row['workflow']} — {row['source']}", axis=1).tolist()
priority_index = next((i for i, value in enumerate(df["status"]) if value == "Investigate"), 0)
selected = st.selectbox("Workflow and source", options, index=priority_index)
row = df.loc[options.index(selected)]

status_styles = {
    "Promising": ("🟢", "Promising"),
    "Investigate": ("🟠", "Investigate before rollout"),
    "Inconclusive": ("🔵", "Inconclusive"),
}
icon, label = status_styles.get(row["status"], ("⚪", row["status"]))

st.subheader(f"{icon} Decision: {label}")
st.write(row["reasons"])

st.markdown("### Comparison context")
col1, col2 = st.columns(2)
col1.metric("Pre-change sessions", f"{row['sessions_pre_change']:.0f}")
col2.metric("Post-change sessions", f"{row['sessions_post_change']:.0f}")

st.markdown("### Observed metric movement")
col1, col2, col3 = st.columns(3)
completion_text, completion_color = delta_text(row["completion_rate_change"], "up")
acceptance_text, acceptance_color = delta_text(row["acceptance_rate_change"], "up")
review_text, review_color = delta_text(row["review_flag_rate_change"], "down")
col1.metric("Completion rate", completion_text, delta_color=completion_color)
col2.metric("Acceptance rate", acceptance_text, delta_color=acceptance_color)
col3.metric("Review-flag rate", review_text, delta_color=review_color)

if "avg_user_rating_change" in df.columns and pd.notna(row["avg_user_rating_change"]):
    rating_text, rating_color = delta_text(row["avg_user_rating_change"], "up")
    st.metric("Average user-rating change", rating_text, delta_color=rating_color)

st.markdown("### Recommended next action")
st.success(next_action(row))

st.markdown("### Interpretation guardrails")
st.markdown(
    "- This is an observational pre/post comparison, **not** causal evidence that the prompt change caused the metric movement.\n"
    "- Acceptance is a rough usefulness signal; it is not a correctness measure.\n"
    "- Review flags can reflect output risk, stricter policy, or different reviewer behavior.\n"
    "- Model confidence is intentionally excluded from the decision because it is not a quality metric.\n"
    "- Known duplicate-export and demo-account rows were excluded during the notebook analysis."
)

with st.expander("See all workflow/source decisions"):
    overview = df[[
        "workflow", "source", "status", "sessions_pre_change", "sessions_post_change",
        "completion_rate_change", "acceptance_rate_change", "review_flag_rate_change"
    ]].copy()
    for column in ["completion_rate_change", "acceptance_rate_change", "review_flag_rate_change"]:
        overview[column] = overview[column].map(lambda value: f"{value:+.1f} pp")
    st.dataframe(overview, use_container_width=True, hide_index=True)

st.caption("Data window: Aug. 1–7, 2026. Prompt-change boundary: Aug. 4, 2026.")
