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

    # 📊 Rating Distribution in Genre
    st.markdown("#### 📊 Rating Distribution in Genre")
    col1, col2 = st.columns([2, 1])
    with col1:
        fig1, ax1 = plt.subplots(figsize=(6, 3))
        sns.histplot(genre_monetization['averageUserRating'], bins=20, kde=True, ax=ax1)
        ax1.axvline(app_data['averageUserRating'], color='red', linestyle='--', label='Selected App')
        ax1.set_title(f"Ratings in {genre}")
        ax1.legend()
        st.pyplot(fig1)
    with col2:
        st.metric("Selected App Rating", f"{app_data['averageUserRating']} ⭐")

    # 💸 Price vs. Rating
    st.markdown("#### 💸 Price vs. Rating in Genre")
    fig2, ax2 = plt.subplots(figsize=(6, 3))
    sns.boxplot(data=genre_monetization, x='formattedPrice', y='averageUserRating', ax=ax2)
    ax2.set_title(f"Price vs. Rating in {genre}")
    st.pyplot(fig2)

    # 🔥 Review Volume vs. Rating
    st.markdown("#### 🔥 Review Volume vs. Rating")
    fig3, ax3 = plt.subplots(figsize=(6, 3))
    sns.scatterplot(data=genre_monetization, x='userRatingCount', y='averageUserRating', ax=ax3)
    ax3.axhline(app_data['averageUserRating'], color='red', linestyle='--')
    ax3.axvline(app_data['userRatingCount'], color='red', linestyle='--')
    ax3.set_title("Review Volume vs. Rating")
    st.pyplot(fig3)