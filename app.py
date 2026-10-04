import streamlit as st

from hybrid_log_classifier.api import build_service
from hybrid_log_classifier.domain import LogEvent


st.set_page_config(page_title="Hybrid Log Classifier", page_icon="🔎")
st.title("Hybrid Log Classifier")
st.caption("Rules first → ML when confident → LLM only when needed")


@st.cache_resource
def get_service():
    return build_service()


text = st.text_area("Log line", placeholder="failed login user=alice ip=203.0.113.7")

if st.button("Classify"):
    if not text.strip():
        st.warning("Enter a log line.")
    else:
        try:
            result = get_service().classify(LogEvent(text))
            st.metric("Category", result.category.value)
            st.write({
                "tier": result.tier.value,
                "confidence": round(result.confidence, 3),
                "reason": result.reason,
                "latency_ms": round(result.latency_ms, 2),
            })
        except RuntimeError as exc:
            st.error(str(exc))
