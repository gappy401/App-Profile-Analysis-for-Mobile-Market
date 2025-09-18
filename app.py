import streamlit as st
import pandas as pd
import altair as alt

# Load cleaned data
df = pd.read_csv('data/apple_cleaned.csv')

# Page config
st.set_page_config(page_title="Apple App Store Insights", layout="wide")

# Title and intro
st.markdown("<h1 style='color:#ff4b4b;'>📱 Apple App Store Insights</h1>", unsafe_allow_html=True)
st.markdown("Explore genre trends, ratings, and top-performing apps using metadata and machine learning.")

# KPIs
col1, col2, col3 = st.columns(3)
col1.metric("Total Apps", len(df))
col2.metric("Average Rating", round(df['rating_value'].mean(), 2))
col3.metric("Most Common Genre", df['predicted_genre'].mode()[0])

# Sidebar filters
st.sidebar.header("🔍 Filter Apps")
selected_genres = st.sidebar.multiselect("Select Genres", df['predicted_genre'].unique(), default=df['predicted_genre'].unique())
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 3.0)
search_term = st.sidebar.text_input("Search App Title")

# Apply filters
filtered_df = df[df['predicted_genre'].isin(selected_genres)]
filtered_df = filtered_df[filtered_df['rating_value'] >= min_rating]
if search_term:
    filtered_df = filtered_df[filtered_df['title'].str.contains(search_term, case=False)]

# Tabs
tab1, tab2, tab3 = st.tabs(["📈 Overview", "🏆 Top Apps", "📝 App Explorer"])

# Tab 1: Overview
with tab1:
    st.subheader("📊 Genre Distribution")
    genre_counts = df['predicted_genre'].value_counts().reset_index()
    genre_counts.columns = ['genre', 'count']
    genre_chart = alt.Chart(genre_counts).mark_bar().encode(
        x=alt.X('genre:N', title='Genre'),
        y=alt.Y('count:Q', title='Number of Apps'),
        color='genre:N'
    ).properties(width=600, height=400, title='Genre Distribution')
    st.altair_chart(genre_chart, use_container_width=True)

    st.subheader("⭐ Average Rating by Genre")
    avg_ratings = df.groupby('predicted_genre')['rating_value'].mean().reset_index()
    avg_ratings.columns = ['genre', 'avg_rating']
    rating_chart = alt.Chart(avg_ratings).mark_bar().encode(
        x=alt.X('genre:N', title='Genre'),
        y=alt.Y('avg_rating:Q', title='Average Rating'),
        color='genre:N'
    ).properties(width=600, height=400, title='Average Rating by Genre')
    st.altair_chart(rating_chart, use_container_width=True)

# Tab 2: Top Apps
with tab2:
    st.subheader("🏆 Top Rated Apps")
    top_apps = filtered_df.sort_values(by='rating_value', ascending=False).head(10)
    for _, row in top_apps.iterrows():
        st.markdown(f"""
        <div style='border:1px solid #ddd; padding:10px; margin:10px; border-radius:8px'>
            <h4>{row['title']}</h4>
            <p><strong>Rating:</strong> {row['rating_value']} ⭐</p>
            <p><strong>Genre:</strong> {row['predicted_genre']}</p>
            <p><strong>Developer:</strong> {row['developer']}</p>
            <a href="{row.get('url', '#')}" target="_blank">🔗 View on App Store</a>
        </div>
        """, unsafe_allow_html=True)

# Tab 3: App Explorer
with tab3:
    st.subheader("🔎 Explore Filtered Apps")
    st.dataframe(filtered_df[['title', 'rating_value', 'reviews_count', 'predicted_genre', 'developer']])
    st.download_button("📥 Download Filtered Data", filtered_df.to_csv(index=False), "filtered_apps.csv")

# Footer
st.markdown("---")
st.markdown("Made by Nandita Ghildyal | Powered by Streamlit & ML")