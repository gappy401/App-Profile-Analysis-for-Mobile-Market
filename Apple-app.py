import streamlit as st
import pandas as pd
import altair as alt

# Load Parquet file (tracked via Git LFS)
df = pd.read_parquet('data/mac_US_cleaned.parquet')

# Basic cleaning
df['averageUserRating'] = pd.to_numeric(df['averageUserRating'], errors='coerce').fillna(0)
df['userRatingCount'] = pd.to_numeric(df['userRatingCount'], errors='coerce').fillna(0)
df['formattedPrice'] = df['formattedPrice'].fillna('Unknown')
df['is_paid'] = df['formattedPrice'].apply(lambda x: x != 'Free')
df['contentAdvisoryRating'] = df['contentAdvisoryRating'].fillna('Unrated')
df['trackViewUrl'] = df['trackViewUrl'].fillna('#')

# Page config
st.set_page_config(page_title="Mac App Store Analytics", layout="wide")
st.title("🖥️ Mac App Store Analytics Dashboard")

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Apps", len(df))
col2.metric("Avg Rating", round(df['averageUserRating'].mean(), 2))
col3.metric("Paid Apps", f"{df['is_paid'].sum()} ({round(100 * df['is_paid'].mean(), 1)}%)")

# Sidebar filters
st.sidebar.header("Filter Apps")
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 3.0)
price_filter = st.sidebar.selectbox("Price Type", ["All", "Free", "Paid"])
search_term = st.sidebar.text_input("Search Title")

# Apply filters
filtered_df = df[df['averageUserRating'] >= min_rating]
if price_filter == "Free":
    filtered_df = filtered_df[~filtered_df['is_paid']]
elif price_filter == "Paid":
    filtered_df = filtered_df[df['is_paid']]
if search_term:
    filtered_df = filtered_df[filtered_df['trackViewUrl'].str.contains(search_term, case=False)]

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Overview", "🏆 Top Apps", "🧩 Explorer"])

with tab1:
    st.subheader("Rating Distribution by Advisory Rating")
    rating_chart = alt.Chart(df).mark_boxplot().encode(
        x='contentAdvisoryRating:N',
        y='averageUserRating:Q',
        color='contentAdvisoryRating:N'
    ).properties(width=700, height=400)
    st.altair_chart(rating_chart, use_container_width=True)

with tab2:
    st.subheader("Top Rated Apps")
    top_apps = filtered_df.sort_values(by='averageUserRating', ascending=False).head(10)
    for _, row in top_apps.iterrows():
        st.markdown(f"""
        <div style='border:1px solid #ddd; padding:10px; margin:10px; border-radius:8px'>
            <h4>{row['trackViewUrl'].split('/')[-1].replace('-', ' ').title()}</h4>
            <p><strong>Rating:</strong> {row['averageUserRating']} ⭐</p>
            <p><strong>Price:</strong> {row['formattedPrice']}</p>
            <p><strong>Advisory:</strong> {row['contentAdvisoryRating']}</p>
            <a href="{row['trackViewUrl']}" target="_blank">🔗 View on App Store</a>
        </div>
        """, unsafe_allow_html=True)

with tab3:
    st.subheader("Explore Filtered Apps")
    st.dataframe(filtered_df[['trackViewUrl', 'averageUserRating', 'userRatingCount', 'formattedPrice', 'contentAdvisoryRating']])
    st.download_button("📥 Download Filtered Data", filtered_df.to_csv(index=False), "mac_apps_filtered.csv")

# Footer
st.markdown("---")
st.markdown("Made by Nandita Ghildyal | Powered by Streamlit & Git LFS")