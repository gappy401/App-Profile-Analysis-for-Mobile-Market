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

# Sidebar filters
st.sidebar.header("🔍 Filter Apps")
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 3.0)
price_filter = st.sidebar.selectbox("Price Type", ["All", "Free", "Paid"])
search_term = st.sidebar.text_input("Search Title")

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Overview", "💰 Top Apps", "🧩 Explorer"])

# ------------------ TAB 1: OVERVIEW ------------------
with tab1:
    st.subheader("Genre-Level Profitability Signals")

    # Genre summary
    genre_summary = overview_df.groupby('primaryGenreName').agg({
        'averageUserRating': 'mean',
        'userRatingCount': 'sum'
    }).reset_index().sort_values(by='userRatingCount', ascending=False)

    st.dataframe(genre_summary.head(10))

    # Rating distribution
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

    # Filter top apps
    filtered_top = top_df[top_df['averageUserRating'] >= min_rating]
    if price_filter == "Free":
        filtered_top = filtered_top[filtered_top['formattedPrice'] == 'Free']
    elif price_filter == "Paid":
        filtered_top = filtered_top[filtered_top['formattedPrice'] != 'Free']
    if search_term:
        filtered_top = filtered_top[filtered_top['trackName'].str.contains(search_term, case=False)]

    # Display top 10
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

    # Price vs. Rating correlation
    st.subheader("Price vs. Rating Correlation")
    st.write("Apps with higher prices don't always have better ratings. Here's the scatterplot:")
    fig, ax = plt.subplots()
    sns.scatterplot(data=filtered_top, x='price', y='averageUserRating', ax=ax)
    st.pyplot(fig)

# ------------------ TAB 3: EXPLORER ------------------
with tab3:
    st.subheader("Explore Filtered Apps")

    filtered_explorer = explorer_df[explorer_df['averageUserRating'] >= min_rating]
    if price_filter == "Free":
        filtered_explorer = filtered_explorer[filtered_explorer['formattedPrice'] == 'Free']
    elif price_filter == "Paid":
        filtered_explorer = filtered_explorer[filtered_explorer['formattedPrice'] != 'Free']
    if search_term:
        filtered_explorer = filtered_explorer[filtered_explorer['trackName'].str.contains(search_term, case=False)]

    st.dataframe(filtered_explorer[['trackName', 'averageUserRating', 'userRatingCount', 'formattedPrice', 'contentAdvisoryRating', 'trackViewUrl']])
    st.download_button("📥 Download Filtered Data", filtered_explorer.to_csv(index=False), "filtered_apps.csv")

# Footer
st.markdown("---")
st.markdown("Made by Nandita Ghildyal | Syracuse University | Powered by Streamlit & Parquet")