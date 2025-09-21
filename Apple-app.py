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
    st.subheader("High-Rated, High-Engagement Apps")

    # Filters
    
    min_rating = st.slider("Minimum Rating", 0.0, 5.0, 4.0)
    price_filter = st.selectbox("Price Type", ["All", "Free", "Paid"])
    genre_options = sorted(top_df['primaryGenreName'].dropna().unique())
    genre_filter = st.selectbox("Genre", ["All"] + genre_options)
    search_term = st.text_input("Search Title")

    # Apply filters
    filtered_top = top_df[top_df['averageUserRating'] >= min_rating]
    if price_filter == "Free":
        filtered_top = filtered_top[filtered_top['formattedPrice'] == 'Free']
    elif price_filter == "Paid":
        filtered_top = filtered_top[filtered_top['formattedPrice'] != 'Free']
    if genre_filter != "All":
        filtered_top = filtered_top[filtered_top['primaryGenreName'] == genre_filter]
    if search_term:
        filtered_top = filtered_top[filtered_top['trackName'].str.contains(search_term, case=False)]

    # KPI Cards
    if not filtered_top.empty:
        top_rated = filtered_top.sort_values(by='averageUserRating', ascending=False).iloc[0]
        most_reviewed = filtered_top.sort_values(by='userRatingCount', ascending=False).iloc[0]
        col1, col2 = st.columns(2)
        col1.metric("Highest Rated", top_rated['trackName'], f"{top_rated['averageUserRating']} stars")
        col2.metric("Most Reviewed", most_reviewed['trackName'], f"{most_reviewed['userRatingCount']} reviews")

    # Top 12 Apps Grid
    st.subheader("Top 12 Apps")
    top_apps = filtered_top.sort_values(by='userRatingCount', ascending=False).head(12)
    rows = [top_apps.iloc[i:i+4] for i in range(0, len(top_apps), 4)]

    for row in rows:
        cols = st.columns(len(row))
        for idx, app in enumerate(row.itertuples()):
            with cols[idx]:
                st.markdown(f"""
                <div style='border:1px solid #ccc; padding:10px; border-radius:6px; background-color:#000000;'>
                    <h5 style='margin-bottom:6px;'>{app.trackName}</h5>
                    <p style='margin:0; font-size:14px;'><strong>Genre:</strong> {app.primaryGenreName}</p>
                    <p style='margin:0; font-size:14px;'><strong>Rating:</strong> {app.averageUserRating} / 5</p>
                    <p style='margin:0; font-size:14px;'><strong>Reviews:</strong> {app.userRatingCount}</p>
                    <p style='margin:0; font-size:14px;'><strong>Price:</strong> {app.formattedPrice}</p>
                    <p style='margin:0; font-size:14px;'><strong>Advisory:</strong> {app.contentAdvisoryRating}</p>
                    <p style='margin-top:6px;'><a href="{app.trackViewUrl}" target="_blank">View on App Store</a></p>
                </div>
                """, unsafe_allow_html=True)

    # Price vs. Rating Chart
    st.subheader("Price vs. Rating")
    fig, ax = plt.subplots(figsize=(6, 4))
    sns.scatterplot(data=filtered_top, x='price', y='averageUserRating', ax=ax)
    ax.set_title("Price vs. Rating", fontsize=12)
    ax.set_xlabel("Price ($)", fontsize=10)
    ax.set_ylabel("Average User Rating", fontsize=10)
    ax.grid(True, linestyle='--', alpha=0.4)
    st.pyplot(fig)

def render_explorer_tab():
    st.subheader("Explore Filtered Apps")

    # ------------------ Filters ------------------
    min_rating = st.slider("Minimum Rating", 0.0, 5.0, 3.0, key="exp_rating")
    price_type = st.selectbox("Price Type", ["All", "Free", "Paid"], key="exp_price")
    genre_options = sorted(top_df['primaryGenreName'].dropna().unique())
    genre_selected = st.selectbox("Genre", ["All"] + genre_options, key="exp_genre")
    search_term = st.text_input("Search Title", key="exp_search")

    # ------------------ Apply Filters ------------------
    filtered_df = top_df.copy()
    filtered_df = filtered_df[filtered_df['averageUserRating'] >= min_rating]
    if price_type == "Free":
        filtered_df = filtered_df[filtered_df['formattedPrice'] == 'Free']
    elif price_type == "Paid":
        filtered_df = filtered_df[filtered_df['formattedPrice'] != 'Free']
    if genre_selected != "All":
        filtered_df = filtered_df[filtered_df['primaryGenreName'] == genre_selected]
    if search_term:
        filtered_df = filtered_df[filtered_df['trackName'].str.contains(search_term, case=False)]

    # ------------------ Display Table ------------------
    display_cols = [
        'trackName', 'primaryGenreName', 'averageUserRating',
        'userRatingCount', 'formattedPrice', 'contentAdvisoryRating'
    ]
    pretty_names = {
        'trackName': 'App Title',
        'primaryGenreName': 'Genre',
        'averageUserRating': 'Avg Rating',
        'userRatingCount': 'Review Count',
        'formattedPrice': 'Price',
        'contentAdvisoryRating': 'Advisory'
    }
    valid_cols = [col for col in display_cols if col in filtered_df.columns]
    display_df = filtered_df[valid_cols].rename(columns=pretty_names)

    if display_df.empty:
        st.warning("No apps match the current filters.")
        return

    st.dataframe(display_df, use_container_width=True, hide_index=True, key="explorer_table")

    # ------------------ App Selection ------------------
    selected_app = st.selectbox("📌 Select an App to Explore", filtered_df['trackName'].unique())
    app_data = filtered_df[filtered_df['trackName'] == selected_app].iloc[0]

    genre_info = overview_df[overview_df['trackName'] == selected_app]
    genre = genre_info['primaryGenreName'].iloc[0] if not genre_info.empty else "N/A"

    genre_subset = top_df[top_df['primaryGenreName'] == genre]

    rating_percentile = round((genre_subset['averageUserRating'] < app_data['averageUserRating']).mean() * 100, 2)
    z_score_reviews = (
        (app_data['userRatingCount'] - genre_subset['userRatingCount'].mean()) /
        genre_subset['userRatingCount'].std()
    ) if genre_subset['userRatingCount'].std() > 0 else 0

    # ------------------ Metrics ------------------
    
    st.markdown(f"### 📱 {app_data['trackName']}")


    # First Row: Core App Info
    col_rating, col_reviews, col_price, col_genre = st.columns([1, 1, 1, 1])
    col_rating.metric(label="Rating", value=f"{app_data['averageUserRating']}")
    col_reviews.metric(label="Reviews", value=f"{app_data['userRatingCount']}")
    col_price.metric(label="Price", value=f"{app_data['formattedPrice']}")
    col_genre.metric(label="Genre", value=genre)

 

    # Second Row: Advisory + Comparative Metrics
    col_advisory, col_percentile, col_zscore = st.columns([1, 1, 1])
    col_advisory.metric(label="Advisory", value=app_data['contentAdvisoryRating'])
    col_zscore.metric(label="Review Z-Score", value=f"{z_score_reviews:.2f}")

    # ------------------ Charts ------------------
    chart1, chart2 = st.columns(2)

    with chart1:
        st.markdown("#### Rating Distribution")
        fig1, ax1 = plt.subplots(figsize=(5, 3))
        sns.histplot(genre_subset['averageUserRating'], bins=20, kde=True, ax=ax1)
        ax1.axvline(app_data['averageUserRating'], color='red', linestyle='--', label='Selected App')
        ax1.set_title(f"Ratings in {genre}")
        ax1.legend()
        st.pyplot(fig1)

    with chart2:
        genre_subset['price_numeric'] = pd.to_numeric(genre_subset['price'], errors='coerce')
        genre_subset['price_bin'] = pd.cut(
            genre_subset['price_numeric'],
            bins=[0, 0.99, 4.99, 9.99, 19.99, 99.99],
            labels=["Free", "<$1", "$1–5", "$5–10", "$10+"]
        )
        fig2, ax2 = plt.subplots(figsize=(6, 4))
        sns.boxplot(data=genre_subset, x='price_bin', y='averageUserRating', ax=ax2)
        ax2.set_title(f"Price vs. Rating — {genre}", fontsize=12)
        ax2.set_xlabel("Price Range", fontsize=10)
        ax2.set_ylabel("Average User Rating", fontsize=10)
        ax2.grid(True, linestyle='--', alpha=0.4)
        st.pyplot(fig2)

    # ------------------ Update Timeline ------------------
    if 'currentVersionReleaseDate' in top_df.columns and 'version' in top_df.columns:
        update_df = top_df[top_df['trackName'] == selected_app].copy()
        update_df['currentVersionReleaseDate'] = pd.to_datetime(update_df['currentVersionReleaseDate'], errors='coerce')
        update_df = update_df.sort_values('currentVersionReleaseDate')

        if not update_df.empty:
            st.markdown("#### Update Timeline")
            update_chart = alt.Chart(update_df).mark_bar().encode(
                x='currentVersionReleaseDate:T',
                y=alt.Y('version:N', title='Version'),
                tooltip=['version', 'currentVersionReleaseDate']
            ).properties(width=600, height=200)
            st.altair_chart(update_chart, use_container_width=True)

    # ------------------ Keyword Extraction ------------------
    if 'description' in top_df.columns:
        desc_text = top_df[top_df['trackName'] == selected_app]['description'].fillna('').values[0]
        vectorizer = CountVectorizer(stop_words='english', max_features=10)
        X = vectorizer.fit_transform([desc_text])
        keywords = vectorizer.get_feature_names_out()

        st.markdown("#### Top Keywords in Description")
        st.write(", ".join([f"`{kw}`" for kw in keywords]))
# ------------------ MAIN ------------------
tab1, tab2, tab3 = st.tabs(["📈 Overview", "💰 Top Apps", "🧩 Explorer"])
with tab1: render_overview_tab()
with tab2: render_top_apps_tab()
with tab3: render_explorer_tab()