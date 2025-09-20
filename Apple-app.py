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
    st.subheader("Genre-Level Profitability Signals")

    genre_summary = overview_df.groupby('primaryGenreName').agg({
        'averageUserRating': 'mean',
        'userRatingCount': 'sum'
    }).reset_index().sort_values(by='userRatingCount', ascending=False)

    st.dataframe(genre_summary.head(10), use_container_width=True, hide_index=True)

    st.subheader("Genre Distribution")
    genre_bar = alt.Chart(genre_summary).mark_bar().encode(
        x=alt.X('primaryGenreName:N', sort='-y'),
        y='userRatingCount:Q',
        tooltip=['primaryGenreName', 'userRatingCount']
    ).properties(width=800, height=400)
    st.altair_chart(genre_bar, use_container_width=True)

    st.subheader("Rating Distribution by Advisory Category")
    rating_chart = alt.Chart(overview_df).mark_boxplot().encode(
        x='contentAdvisoryRating:N',
        y='averageUserRating:Q',
        color='contentAdvisoryRating:N'
    ).properties(width=700, height=400)
    st.altair_chart(rating_chart, use_container_width=True)

# ------------------ TAB 2: TOP APPS ------------------
with tab2:
    st.subheader("High-Rated, High-Engagement Apps")

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

    st.subheader("Price vs. Rating Correlation")
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_top, x='price', y='averageUserRating', ax=ax)
    ax.set_title("Price vs. Rating")
    st.pyplot(fig)

# ------------------ TAB 3: EXPLORER ------------------
with tab3:
    st.subheader("Explore Filtered Apps")

    min_rating_exp = st.slider("Minimum Rating", 0.0, 5.0, 3.0, key="exp_rating")
    price_filter_exp = st.selectbox("Price Type", ["All", "Free", "Paid"], key="exp_price")
    search_term_exp = st.text_input("Search Title", key="exp_search")

    filtered_explorer = explorer_df[explorer_df['averageUserRating'] >= min_rating_exp]
    if price_filter_exp == "Free":
        filtered_explorer = filtered_explorer[filtered_explorer['formattedPrice'] == 'Free']
    elif price_filter_exp == "Paid":
        filtered_explorer = filtered_explorer[filtered_explorer['formattedPrice'] != 'Free']
    if search_term_exp:
        filtered_explorer = filtered_explorer[filtered_explorer['trackName'].str.contains(search_term_exp, case=False)]

    st.dataframe(
        filtered_explorer[['trackName', 'averageUserRating', 'userRatingCount', 'formattedPrice', 'contentAdvisoryRating', 'trackViewUrl']],
        use_container_width=True,
        hide_index=True
    )

    st.download_button("📥 Download Filtered Data", filtered_explorer.to_csv(index=False), "filtered_apps.csv")

    st.subheader("Ratings Histogram")
    fig2, ax2 = plt.subplots()
    sns.histplot(filtered_explorer['averageUserRating'], bins=20, kde=True, ax=ax2)
    ax2.set_title("Distribution of App Ratings")
    st.pyplot(fig2)

# Footer
st.markdown("---")
st.markdown("Made by Nandita Ghildyal")