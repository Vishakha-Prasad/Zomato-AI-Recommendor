"""
Zomato AI Recommender - Streamlit App
Deploy: streamlit run app.py
"""

import streamlit as st
from backend.catalog import filter_restaurants, get_locations, get_cuisines
from backend.models import Restaurant
from backend import groq_ranker

st.set_page_config(page_title="Zomato AI Recommender", page_icon="🍽️", layout="wide")

st.title("🍽️ Zomato AI Recommender")
st.markdown("*AI-powered restaurant recommendations using Groq LLM*")

# Sidebar filters
with st.sidebar:
    st.header("Filters")
    try:
        locations = get_locations()
        cuisines_list = get_cuisines()
    except FileNotFoundError as e:
        st.error(
            "Data not found. Run the pipeline first:\n"
            "`python data_pipeline/explore_and_clean_data.py`"
        )
        st.stop()

    location = st.selectbox("Location", options=[""] + locations)
    cuisines = st.multiselect("Cuisines", options=cuisines_list)
    min_rating = st.slider("Min rating", 0.0, 5.0, 0.0, 0.5)
    max_price = st.number_input("Max budget for two (₹)", min_value=0, value=0, step=500)
    if max_price == 0:
        max_price = None

    get_recs = st.button("Get recommendations")

results = []
if get_recs:
    with st.spinner("Finding restaurants..."):
        df = filter_restaurants(
            location=location or "",
            cuisines=cuisines or [],
            min_rating=min_rating or 0.0,
        )
        results = [
            Restaurant(
                name=row["name"],
                location=row["location"],
                cuisine=row["cuisine"],
                cost_for_two=int(row["cost_for_two"]),
                rating=float(row["rating"]),
                reviews=row.get("reviews", ""),
            )
            for _, row in df.iterrows()
        ]
        results = groq_ranker.rerank(results, {
            "location": location,
            "cuisines": cuisines,
            "min_rating": min_rating,
            "max_price": max_price,
        })
if not results:
    st.info("Select filters and click **Get recommendations** to find restaurants.")
else:
    st.success(f"Found **{len(results)}** restaurants")
    for i, r in enumerate(results, 1):
        with st.container():
            col1, col2 = st.columns([3, 1])
            with col1:
                st.subheader(f"{i}. {r.name}")
                st.caption(f"{r.location} · {r.cuisine}")
                if r.review_summary:
                    st.markdown(f"*{r.review_summary}*")
            with col2:
                st.metric("Rating", f"⭐ {r.rating}")
                price = r.min_price_for_two or r.cost_for_two
                st.metric("Cost for 2", f"₹{price}")
            st.divider()
