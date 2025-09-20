import streamlit as st
import pandas as pd
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.feature_extraction.text import CountVectorizer

# ------------------ CONFIG ------------------
st.set_page_config(page_title="Profitable App Profiles", layout="wide")
DATA_PATHS = {
    "overview": "data/overview.parquet",
    "top": "data/top_apps.parquet",
    "explorer": "data/explorer.parquet"
}

# ------------------ DATA LOADING ------------------
@st.cache_data
def load_data():
    return (
        pd.read_parquet(DATA_PATHS["overview"]),
        pd.read_parquet(DATA_PATHS["top"]),
        pd.read_parquet(DATA_PATHS["explorer"])
    )

overview_df, top_df, explorer_df = load_data()

# ------------------ TAB FUNCTIONS ------------------
def render_overview_tab():
    st.subheader("🎯 Genre-Level Profitability Signals")
    top_genres = overview_df['primaryGenreName'].value_counts().head(3)
    col1, col2, col3 = st.columns(3)
    col1.metric("Top Genre", top_genres.index[0], f"{top_genres.iloc[0]} apps")
    col2.metric("2nd Genre", top_genres.index[1], f"{top_genres.iloc[1]} apps")
    col3.metric("3rd Genre", top_genres.index[2], f"{top_genres.iloc[2]} apps")

    genre_summary = overview_df.groupby('primaryGenreName').agg({
        'averageUserRating': 'mean',
        'userRatingCount': 'sum'
    }).reset_index().sort_values(by='userRatingCount', ascending=False)

    genre_bar = alt.Chart(genre_summary).mark_bar().encode(
        x=alt.X('primaryGenreName:N', sort='-y'),
        y='userRatingCount:Q',
        color='averageUserRating:Q',
        tooltip=['primaryGenreName', 'userRatingCount', 'averageUserRating']
    ).properties(title="📊 Genre Popularity & Ratings", width=800, height=400)
    st.altair_chart(genre_bar, use_container_width=True)

    st.subheader("📋 Rating Distribution by Advisory Category")
    rating_chart = alt.Chart(overview_df).mark_boxplot().encode(
        x='contentAdvisoryRating:N',
        y='averageUserRating:Q',
        color='contentAdvisoryRating:N'
    ).properties(width=700, height=400)
    st.altair_chart(rating_chart, use_container_width=True)

    st.caption("ℹ️ “Not Yet Rated” sounds neutral, but it often reflects apps that are either unrated by Apple’s content system or haven’t gained enough traction to earn high user ratings.")

def render_top_apps_tab():
    st.subheader("💎 High-Rated, High-Engagement Apps")
    min_rating = st.slider("Minimum Rating", 0.0, 5.0, 4.0)
    price_filter = st.selectbox("Price Type", ["All", "Free", "Paid"])
    search_term = st.text_input("Search Title")

    filtered_top = top_df[top_df['averageUserRating'] >= min_rating]
    if price_filter == "Free":
        filtered_top = filtered_top[filtered_top['formattedPrice'] == 'Free']
    elif price_filter == "Paid":
        filtered_top = filtered_top[filtered_top['formattedPrice'] != 'Free']
    if search_term:
        filtered_top = filtered_top[filtered_top['trackName'].str.contains(search_term, case=False)]

    if not filtered_top.empty:
        top_rated = filtered_top.sort_values(by='averageUserRating', ascending=False).iloc[0]
        most_reviewed = filtered_top.sort_values(by='userRatingCount', ascending=False).iloc[0]
        col1, col2 = st.columns(2)
        col1.metric("⭐ Highest Rated", top_rated['trackName'], f"{top_rated['averageUserRating']} stars")
        col2.metric("🔥 Most Reviewed", most_reviewed['trackName'], f"{most_reviewed['userRatingCount']} reviews")

    st.subheader("📱 Top 12 Apps")
    top_apps = filtered_top.sort_values(by='userRatingCount', ascending=False).head(12)
    rows = [top_apps.iloc[i:i+4] for i in range(0, len(top_apps), 4)]
    for row in rows:
        cols = st.columns(len(row))
        for idx, app in enumerate(row.itertuples()):
            with cols[idx]:
                st.markdown(f"""
                <div style='border:1px solid #ddd; padding:10px; border-radius:8px; background-color:#f9f9f9'>
                    <h5 style='margin-bottom:5px'>{app.trackName}</h5>
                    <p style='margin:0'><strong>Rating:</strong> {app.averageUserRating} ⭐</p>
                    <p style='margin:0'><strong>Reviews:</strong> {app.userRatingCount}</p>
                    <p style='margin:0'><strong>Price:</strong> {app.formattedPrice}</p>
                    <p style='margin:0'><strong>Advisory:</strong> {app.contentAdvisoryRating}</p>
                    <a href="{app.trackViewUrl}" target="_blank">🔗 View</a>
                </div>
                """, unsafe_allow_html=True)

    st.subheader("💸 Price vs. Rating")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.scatterplot(data=filtered_top, x='price', y='averageUserRating', ax=ax)
    ax.set_title("Price vs. Rating", fontsize=12)
    ax.set_xlabel("Price ($)", fontsize=10)
    ax.set_ylabel("Average User Rating", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.4)
    st.pyplot(fig)

def render_explorer_tab():
    # Your full Explorer tab logic goes here (already well-structured)
    pass  # Placeholder for brevity

# ------------------ MAIN ------------------
tab1, tab2, tab3 = st.tabs(["📈 Overview", "💰 Top Apps", "🧩 Explorer"])
with tab1: render_overview_tab()
with tab2: render_top_apps_tab()
with tab3: render_explorer_tab()