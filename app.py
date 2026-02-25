import sys
import os
import streamlit as st
import pandas as pd

# Add the project root to the Python path for deployment
project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import backend modules directly
from backend.catalog import filter_restaurants, get_locations, get_cuisines
from backend import groq_ranker
from backend.models import PreferencePayload, Restaurant

# ----------------------------------------------------------------------------
# 1. Page Configuration & Styling
# ----------------------------------------------------------------------------
st.set_page_config(
    page_title="Zomato AI Recommender",
    page_icon="🍔",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom minimal CSS for a cleaner look
st.markdown("""
<style>
    /* Main container padding */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
    }
    /* Restaurant card basic styling */
    .restaurant-card {
        background-color: #1e1e1e;
        border-radius: 10px;
        padding: 20px;
        margin-bottom: 20px;
        border: 1px solid #333;
    }
    .restaurant-name {
        color: #e23744;
        font-size: 1.5rem;
        font-weight: bold;
        margin-bottom: 5px;
    }
    .restaurant-meta {
        color: #aaa;
        font-size: 0.9rem;
        margin-bottom: 10px;
    }
    .restaurant-ai-summary {
        background-color: #2a2a2a;
        padding: 10px;
        border-radius: 5px;
        font-size: 0.9rem;
        margin-top: 10px;
        border-left: 4px solid #e23744;
    }
    .star-rating {
        color: #ff9f00;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# ----------------------------------------------------------------------------
# 2. Main App Logic
# ----------------------------------------------------------------------------
def main():
    st.title("🍔 Zomato AI Recommender")
    st.markdown("Discover restaurants you'll love based on your cravings and our AI's analysis.")

    # Load locations & cuisines
    try:
        locations_list = get_locations()
        locations = ["Any Location"] + locations_list
        cuisines = get_cuisines()
    except FileNotFoundError:
        st.error(
            "Data not found. Run the pipeline first:\n"
            "`python data_pipeline/explore_and_clean_data.py`"
        )
        st.stop()

    # Sidebar: Filters
    with st.sidebar:
        st.header("Your Preferences")
        
        # Location
        selected_loc = st.selectbox("Location", locations)
        
        # Cuisines (multi-select up to 4)
        selected_cuisines = st.multiselect("What's your craving?", cuisines, max_selections=4)
        
        # Budget
        budget = st.number_input("Price range (₹) (Optional)", min_value=0, step=100, value=0)
        
        # Minimum Rating
        min_rating = st.slider("Minimum Rating", min_value=0.0, max_value=5.0, step=0.5, value=0.0)
        
        st.divider()
        st.markdown("**Voice Search Hint:**")
        st.caption("You can use your device's built-in dictation for the text box below to search by voice!")
        
        # NLP / Search Box
        free_text = st.text_input("Or describe what you want:", placeholder="e.g. Find me some spicy Chinese in Koramangala")
        
        get_recos = st.button("Get Recommendations", type="primary", use_container_width=True)

    # ----------------------------------------------------------------------------
    # 3. Recommendation Fetching
    # ----------------------------------------------------------------------------
    if get_recos:
        # Pre-process inputs
        loc_val = "" if selected_loc == "Any Location" else selected_loc
        budget_val = budget if budget > 0 else None
        
        # If the user typed free text, we can try to extract constraints or pass it as location.
        # But for exact parity with the JS, the JS heuristic was parsing text for locations & cuisines.
        if free_text:
            text_lower = free_text.lower()
            # Detect location
            for l in locations_list:
                if l.lower() in text_lower:
                    loc_val = l
            # Detect cuisines
            for c in cuisines:
                if c.lower() in text_lower and c not in selected_cuisines and len(selected_cuisines) < 4:
                    selected_cuisines.append(c)

        # Build payload
        payload = PreferencePayload(
            location=loc_val,
            cuisines=selected_cuisines,
            min_rating=min_rating,
            max_price=budget_val
        )

        with st.spinner("Analyzing top picks for you..."):
            try:
                # 1. Filter local catalog
                df = filter_restaurants(
                    location=payload.location or "",
                    cuisines=payload.cuisines or [],
                    min_rating=payload.min_rating or 0.0,
                )
                
                # Further filter max price manually if provided
                if payload.max_price:
                    df = df[df["cost_for_two"] <= payload.max_price]

                raw_results = [
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

                if not raw_results:
                    st.warning("No restaurants found matching your criteria. Try loosening your filters!")
                    return

                # 2. Groq Rerank & Summarize
                results = groq_ranker.rerank(raw_results, payload.model_dump())
                
                st.success(f"Showing top {len(results)} recommendations!")

                # ----------------------------------------------------------------------------
                # 4. Results Rendering
                # ----------------------------------------------------------------------------
                cols = st.columns(3) # 3 Column grid
                
                for idx, r in enumerate(results):
                    col = cols[idx % 3]
                    with col:
                        # Full stars
                        stars = "★" * int(r.rating) + "☆" * (5 - int(r.rating))
                        
                        min_price_disp = getattr(r, 'min_price_for_two', r.cost_for_two) or r.cost_for_two
                        
                        card_html = f'''
                        <div class="restaurant-card">
                            <div class="restaurant-name">{r.name}</div>
                            <div class="restaurant-meta">{r.location.title()} • {r.cuisine.title()}</div>
                            
                            <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                                <span class="star-rating">{stars} {r.rating:.1f}</span>
                                <span>₹{min_price_disp}</span>
                            </div>
                        '''
                        
                        if getattr(r, 'review_summary', None):
                            card_html += f'''
                            <div class="restaurant-ai-summary">
                                <b>AI Summary:</b><br/>{r.review_summary}
                            </div>
                            '''
                            
                        card_html += '</div>'
                        st.markdown(card_html, unsafe_allow_html=True)
                        
            except Exception as e:
                st.error(f"Error fetching recommendations: {str(e)}")
    else:
        # Default empty state
        st.info("👈 Adjust filters in the sidebar and click **Get Recommendations** to discover your next meal!")
        
        # Promotional banners
        st.subheader("Quick Categories")
        c1, c2, c3 = st.columns(3)
        c1.button("Traditional", use_container_width=True) # Could wire these to set session_state but keeping it simple visual
        c2.button("Fast Food", use_container_width=True)
        c3.button("Nightlife", use_container_width=True)

if __name__ == "__main__":
    main()
