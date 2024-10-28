import streamlit as st
from streamlit_autorefresh import st_autorefresh
from pymongo import MongoClient
import pymongo
import pandas as pd
import plotly.express as px
import os
import math
from datetime import datetime

VALID_COLLECTIONS = [
    "avg_interactions_per_user_whole",
    "avg_interactions_per_item_whole",
    "avg_interactions_per_item_5m",
    "avg_interactions_per_user_5m",
    "interactions_per_item_5m",
    "interactions_per_user_5m",
    "max_min_per_item"
]

# Connect to MongoDB using environment variable
client = MongoClient(os.getenv("MONGO_URI"))
db = client[os.getenv("DATABASE")]

def get_df(collection_name, start_date, start_time, end_date, end_time, is_timeseries = True):
    """
    Get data from MongoDB collection

    Parameters:
    collection_name (str): Name of the collection
    start_date (str): Start date in YYYY-MM-DD format
    start_time (str): Start time in HH:MM:SS format
    end_date (str): End date in YYYY-MM-DD format
    end_time (str): End time in HH:MM:SS format
    is_timeseries (bool): Whether the data is time-series or not
    """
    if collection_name not in VALID_COLLECTIONS:
        raise ValueError(f"Invalid collection name. Valid collections are: {VALID_COLLECTIONS}")
    
    collection = db[collection_name]
    start_datetime = datetime.strptime(f"{start_date} {start_time}", "%Y-%m-%d %H:%M:%S")
    end_datetime = datetime.strptime(f"{end_date} {end_time}", "%Y-%m-%d %H:%M:%S")
    filter = {
        "window.start": {
            "$gte": start_datetime,
            "$lte": end_datetime
        }
    }
    if is_timeseries:
        df = pd.DataFrame(list(collection.find(filter=filter).sort("window.start", pymongo.DESCENDING)))
        if df.empty:
            return df
        
        df['timestamp'] = df['window'].apply(lambda x: x['start'])
        return df
    
    return pd.DataFrame(list(collection.find()))

def get_scalar(collection_name, field_name):
    """
    Get scalar value from MongoDB collection

    Parameters:
    collection_name (str): Name of the collection
    field_name (str): Name of the field
    """
    if collection_name not in VALID_COLLECTIONS:
        raise ValueError(f"Invalid collection name. Valid collections are: {VALID_COLLECTIONS}")
        
    collection = db[collection_name]
    data = collection.find_one()
    if not data:
        return None
    
    return data[field_name]


st.title("Time-Series Data from MongoDB")

st_autorefresh(interval=5000, key="autorefresh")

col1, col2, col3, col4 = st.columns(4)
with col1:
    start_date = st.date_input('Start date', value=pd.to_datetime('2024-10-28'))
with col2:
    start_time = st.time_input('Start time', value=pd.to_datetime('00:00:00').time())
with col3:
    end_date = st.date_input('End date', value=pd.to_datetime('2024-10-28'))
with col4:
    end_time = st.time_input('End time', value=pd.to_datetime('23:59:59').time())


col1, col2 = st.columns(2)
with col1:
    st.metric(label="**Avg Interactions per User**", value=round(get_scalar("avg_interactions_per_user_whole", "avg_interactions_per_user"), 2))
with col2:
    st.metric(label="**Avg Interactions per Item**", value=round(get_scalar("avg_interactions_per_item_whole", "avg_interactions_per_item"), 2))

col1, col2 = st.columns(2)
with col1:
    df = get_df("avg_interactions_per_item_5m", start_date, start_time, end_date, end_time)
    fig = px.line(df, x='timestamp', y='avg_interactions_per_item', title='Average Interactions per Item', labels={"avg_interactions_per_item": "Avg Interactions"})
    st.plotly_chart(fig)
with col2:
    df = get_df("avg_interactions_per_user_5m", start_date, start_time, end_date, end_time)
    fig = px.line(df, x='timestamp', y='avg_interactions_per_user', title='Average Interactions per User', labels={"avg_interactions_per_user": "Avg Interactions"})
    st.plotly_chart(fig)

col1, col2 = st.columns(2)
with col1:
    df = get_df("interactions_per_item_5m", start_date, start_time, end_date, end_time)
    fig = px.bar(df, x='timestamp', y='interaction_count', color="interaction_type", title='Interactions per type', barmode='stack')
    st.plotly_chart(fig)
with col2:
    df = get_df("interactions_per_item_5m", start_date, start_time, end_date, end_time)
    fig = px.bar(df, x='timestamp', y='interaction_count', color="item_id", title='Interactions per item', barmode='stack')
    st.plotly_chart(fig)

df = get_df("max_min_per_item", start_date, start_time, end_date, end_time, False)
df.rename(columns={"_id": "item_id"}, inplace=True)
if not df.empty:
    df["item_id"] = df["item_id"].astype(int)
    df = df.sort_values(by="item_id").reset_index(drop=True)
    
st.write("**Interactions with Most and Least Occurence per Item**")
st.dataframe(df)