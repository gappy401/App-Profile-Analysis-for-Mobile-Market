import streamlit as st
import pandas as pd

# Load cleaned Apple App Store data
df = pd.read_csv('data/apple_cleaned.csv')

st.set_page_config(page_title="Apple App Store Insights", layout="wide")
st.title("📱 Apple App Store Insights Dashboard")

# Sidebar filters
genre = st.sidebar.selectbox("Filter by Genre", ["All"] + sorted(df['predicted_genre'].unique()))
min_rating = st.sidebar.slider("Minimum Rating", 0.0, 5.0, 3.0)

# Apply filters
filtered_df = df.copy()
if genre != "All":
    filtered_df = filtered_df[filtered_df['predicted_genre'] == genre]
filtered_df = filtered_df[filtered_df['rating_value'] >= min_rating]

# Genre distribution
st.subheader("📊 Genre Distribution")
st.bar_chart(df['predicted_genre'].value_counts())

# Ratings by genre
st.subheader("⭐ Average Rating by Genre")
avg_ratings = df.groupby('predicted_genre')['rating_value'].mean().sort_values(ascending=False)
st.bar_chart(avg_ratings)

# Top apps
st.subheader("🏆 Top Rated Apps")
top_apps = filtered_df.sort_values(by='rating_value', ascending=False).head(10)
st.dataframe(top_apps[['title', 'rating_value', 'reviews_count', 'predicted_genre', 'developer']])

# Description viewer
st.subheader("📝 App Descriptions")
for _, row in top_apps.iterrows():
    st.markdown(f"**{row['title']}** — *{row['developer']}*")
    st.write(row['description'])
    