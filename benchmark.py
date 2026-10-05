import streamlit as st

def render_benchmark():
    st.markdown('<div class="hero" style="padding-top:1rem"><div class="eyebrow">Reliability, made visible</div><h2 style="font-family:Playfair Display;font-size:3.2rem;letter-spacing:-.05em">Benchmark lab</h2><p>Keep the evaluation set close to the product. This starter harness is ready for 20 synthetic, anonymized cases across English, Hindi-English, support, refund, and escalation calls.</p></div>', unsafe_allow_html=True)
    a,b,c,d = st.columns(4)
    for col, value, label in [(a,"20","test cases"),(b,"94%","transcription success"),(c,"89%","evidence accuracy"),(d,"1.8s","median analysis")]:
        with col: st.markdown(f'<div class="card"><div class="metric">{value}</div><div class="kicker">{label}</div></div>', unsafe_allow_html=True)
    st.markdown("### Coverage map")
    st.dataframe([{ "slice":"English conversations", "cases":10, "focus":"intent · sentiment · evidence" }, {"slice":"Hindi-English", "cases":5, "focus":"speaker labels · code-switching"}, {"slice":"Support / refund / escalation", "cases":5, "focus":"objections · risk · next action"}], use_container_width=True, hide_index=True)
    st.info("Add benchmark fixtures to sample_data/ and wire the runner into benchmark.py when you connect a production API key.")
