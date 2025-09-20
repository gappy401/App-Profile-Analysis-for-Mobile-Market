import streamlit as st
import pandas as pd
import altair as alt
import seaborn as sns
import matplotlib.pyplot as plt

st.set_page_config(page_title="Profitable App Profiles", layout="wide")
st.title("📱 Profitable App Profiles for Mobile Market")

# Load modular Parquet files
overview_df = pd.read_parquet('data/overview.parquet')
top_df = pd.read_parquet('data/top_apps.parquet')
explorer_df = pd.read_parquet('data/explorer.parquet')

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Overview", "💰 Top Apps", "🧩 Explorer"])

# ------------------ TAB 1: OVERVIEW ------------------
with tab1:
    st.subheader("🎯 Genre-Level Profitability Signals")

    # KPI Cards
    top_genres = overview_df['primaryGenreName'].value_counts().head(3)
    col1, col2, col3 = st.columns(3)
    col1.metric("Top Genre", top_genres.index[0], f"{top_genres.iloc[0]} apps")
    col2.metric("2nd Genre", top_genres.index[1], f"{top_genres.iloc[1]} apps")
    col3.metric("3rd Genre", top_genres.index[2], f"{top_genres.iloc[2]} apps")

    # Genre Distribution Bar Chart
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

    # Advisory Rating Boxplot
    st.subheader("📋 Rating Distribution by Advisory Category")
    rating_chart = alt.Chart(overview_df).mark_boxplot().encode(
        x='contentAdvisoryRating:N',
        y='averageUserRating:Q',
        color='contentAdvisoryRating:N'
    ).properties(width=700, height=400)
    st.altair_chart(rating_chart, use_container_width=True)

# ------------------ TAB 2: TOP APPS ------------------
with tab2:
    st.subheader("💎 High-Rated, High-Engagement Apps")

    # Filters
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

    # KPI Cards
    if not filtered_top.empty:
        top_rated = filtered_top.sort_values(by='averageUserRating', ascending=False).iloc[0]
        most_reviewed = filtered_top.sort_values(by='userRatingCount', ascending=False).iloc[0]
        col1, col2 = st.columns(2)
        col1.metric("⭐ Highest Rated", top_rated['trackName'], f"{top_rated['averageUserRating']} stars")
        col2.metric("🔥 Most Reviewed", most_reviewed['trackName'], f"{most_reviewed['userRatingCount']} reviews")

    # App Cards
    st.subheader("📱 Top 10 Apps")
    top_apps = filtered_top.sort_values(by='userRatingCount', ascending=False).head(10)
    for _, row in top_apps.iterrows():
        st.markdown(f"""
        <div style='border:1px solid #ddd; padding:10px; margin:10px; border-radius:8px'>
            <h4>{row['trackName']}</h4>
            <p><strong>Rating:</strong> {row['averageUserRating']} ⭐</p>
            <p><strong>Price:</strong> {row['formattedPrice']}</p>
            <p><strong>Advisory:</strong> {row['contentAdvisoryRating']}</p>
            <a href="{row['trackViewUrl']}" target="_blank">🔗 View on App Store</a>
        </div>
        """, unsafe_allow_html=True)

    # Scatterplot
    st.subheader("💸 Price vs. Rating")
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_top, x='price', y='averageUserRating', ax=ax)
    ax.set_title("Price vs. Rating")
    st.pyplot(fig)

# ------------------ TAB 3: EXPLORER ------------------
with tab3:
    st.subheader("🔍 Explore Filtered Apps")

    # Filters
    min_rating_exp = st.slider("Minimum Rating", 0.0, 5.0, 3.0, key="exp_rating")
    price_filter_exp = st.selectbox("Price Type", ["All", "Free", "Paid"], key="exp_price")
    search_term_exp = st.text_input("Search Title", key="exp_search")

    filtered_explorer = top_df[top_df['averageUserRating'] >= min_rating_exp]
    if price_filter_exp == "Free":
        filtered_explorer = filtered_explorer[filtered_explorer['formattedPrice'] == 'Free']
    elif price_filter_exp == "Paid":
        filtered_explorer = filtered_explorer[filtered_explorer['formattedPrice'] != 'Free']
    if search_term_exp:
        filtered_explorer = filtered_explorer[filtered_explorer['trackName'].str.contains(search_term_exp, case=False)]

    # Display clean table
    display_cols = ['trackName', 'averageUserRating', 'userRatingCount', 'formattedPrice', 'contentAdvisoryRating']
    valid_cols = [col for col in display_cols if col in filtered_explorer.columns]
    st.dataframe(filtered_explorer[valid_cols], use_container_width=True, hide_index=True)

    # App selection
    selected_app = st.selectbox("📌 Select an App to Explore", filtered_explorer['trackName'].unique())
    app_data = filtered_explorer[filtered_explorer['trackName'] == selected_app].iloc[0]

    # Pull genre from overview_df
    genre_info = overview_df[overview_df['trackName'] == selected_app]
    genre = genre_info['primaryGenreName'].iloc[0] if not genre_info.empty else "N/A"

    # Display app summary
    st.markdown(f"### 📱 {app_data['trackName']}")
    st.markdown(f"""
    **Genre:** {genre}  
    **Rating:** {app_data.get('averageUserRating', 'N/A')} ⭐  
    **Reviews:** {app_data.get('userRatingCount', 'N/A')}  
    **Price:** {app_data.get('formattedPrice', 'N/A')}  
    **Advisory:** {app_data.get('contentAdvisoryRating', 'N/A')}
    """)

    # Define genre_monetization
    genre_monetization = top_df.merge(
        overview_df[['trackName', 'primaryGenreName']],
        on='trackName',
        how='left'
    )
    genre_monetization = genre_monetization[genre_monetization['primaryGenreName'] == genre]

    # 📈 Percentile Rank for Rating
    if not genre_monetization.empty:
        rating_percentile = round((genre_monetization['averageUserRating'] < app_data['averageUserRating']).mean() * 100, 2)
        st.markdown(f"#### 📈 Rating Percentile")
        st.info(f"This app ranks in the top **{rating_percentile}%** of {genre} apps by average user rating.")

    # 📊 Z-Score for Review Volume
    if genre_monetization['userRatingCount'].std() > 0:
        z_score_reviews = (app_data['userRatingCount'] - genre_monetization['userRatingCount'].mean()) / genre_monetization['userRatingCount'].std()
        st.markdown("#### 📊 Review Volume Z-Score")
        st.info(f"This app has a review volume **{z_score_reviews:.2f} standard deviations** above the genre average.")

    # 📅 Update Frequency (if available)
    if 'currentVersionReleaseDate' in top_df.columns and 'version' in top_df.columns:
        update_df = top_df[top_df['trackName'] == selected_app].copy()
        update_df['currentVersionReleaseDate'] = pd.to_datetime(update_df['currentVersionReleaseDate'], errors='coerce')
        update_df = update_df.sort_values('currentVersionReleaseDate')

        if not update_df.empty:
            st.markdown("#### 📅 Update Timeline")
            update_chart = alt.Chart(update_df).mark_bar().encode(
                x='currentVersionReleaseDate:T',
                y=alt.Y('version:N', title='Version'),
                tooltip=['version', 'currentVersionReleaseDate']
            ).properties(width=600, height=200)
            st.altair_chart(update_chart, use_container_width=True)

    # 🧠 Keyword Extraction from Description
    if 'description' in top_df.columns:
        from sklearn.feature_extraction.text import CountVectorizer

        desc_text = top_df[top_df['trackName'] == selected_app]['description'].fillna('').values[0]
        vectorizer = CountVectorizer(stop_words='english', max_features=10)
        X = vectorizer.fit_transform([desc_text])
        keywords = vectorizer.get_feature_names_out()

        st.markdown("#### 🧠 Top Keywords in Description")
        st.write(", ".join([f"`{kw}`" for kw in keywords]))