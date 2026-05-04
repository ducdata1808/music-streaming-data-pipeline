import os
import sys
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import logging # check error
from typing import Optional, List, Dict, Any # for type hint
from colorama import Fore, Style, init # for color output
import clickhouse_connect # for clickhouse

# Parameters
# Dynamic path: use script's own directory so it works both locally and in Docker
_APP_DIR = os.path.dirname(os.path.abspath(__file__))
_DEFAULT_LOG_FILE = os.path.join(_APP_DIR, "logs", "app.log")
os.makedirs(os.path.join(_APP_DIR, "logs"), exist_ok=True)

LOG_FILE = os.environ.get("LOG_FILE", _DEFAULT_LOG_FILE)
CLICKHOUSE_HOST = os.environ.get("CLICKHOUSE_HOST", "localhost")
CLICKHOUSE_PORT = int(os.environ.get("CLICKHOUSE_PORT", "8123"))
CLICKHOUSE_USER = os.environ.get("CLICKHOUSE_USER", "default")
CLICKHOUSE_PASSWORD = os.environ.get("CLICKHOUSE_PASSWORD", "")
CLICKHOUSE_DATABASE = os.environ.get("CLICKHOUSE_DATABASE", "music_analytics")
VERBOSE = True # verbose output


class Background_colors:
    RED = "\033[41m"
    GREEN = "\033[42m"
    YELLOW = "\033[43m"
    BLUE = "\033[44m"
    MAGENTA = "\033[45m"
    CYAN = "\033[46m"
    END = "\033[0m"

# setup log file
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    filename=LOG_FILE,
                    filemode="a")
logger = logging.getLogger("app")

# print message with color
def verbose_output(message: str) -> None:
    if VERBOSE:
        print(f"{message}{Background_colors.END}")

# page layout
st.sidebar.title("Music Events Dashboard")
menu = st.sidebar.selectbox(
    "Choose content to display",
    ["Overview", "Top Artists", "Music listening trends by time", "Top listening trends by areas"]
)

client = clickhouse_connect.get_client(host=CLICKHOUSE_HOST, port=CLICKHOUSE_PORT, user=CLICKHOUSE_USER, password=CLICKHOUSE_PASSWORD, database=CLICKHOUSE_DATABASE)

# Overview
if menu == "Overview":
    try:
        st.title("Overview")
        total_listens = client.query("SELECT count() FROM fct_listens").result_rows[0][0]
        st.write(f"Total listens: {total_listens}")
        total_song = client.query("SELECT count(DISTINCT song) FROM fct_listens").result_rows[0][0]
        st.write(f"Total songs: {total_song}")
        total_artist = client.query("SELECT count(DISTINCT artist) FROM fct_listens").result_rows[0][0]
        st.write(f"Total artists: {total_artist}")
        total_user = client.query("SELECT count(DISTINCT user_id) FROM fct_listens").result_rows[0][0]
        st.write(f"Total users: {total_user}")
        total_session = client.query("SELECT count(DISTINCT session_id) FROM fct_listens").result_rows[0][0]
        st.write(f"Total sessions: {total_session}")
        verbose_output(f"{Background_colors.GREEN}Successfully retrieved overview{Background_colors.END}")
    except Exception as e:
        st.error(f"Error: {e}")
        logger.error(f"Error: {e}")
        verbose_output(f"{Background_colors.RED}Error: {e}{Background_colors.END}")
        st.stop()


# Top Artists
elif menu == "Top Artists":
    st.title("Top Artists")
    try:
        df_top_artists = client.query_df("SELECT * FROM mart_top_artists ORDER BY play_count DESC LIMIT 10")
        verbose_output(f"{Background_colors.GREEN}Successfully retrieved top artists{Background_colors.END}")
    except Exception as e:
        st.error(f"Error: {e}")
        logger.error(f"Error: {e}")
        verbose_output(f"{Background_colors.RED}Error: {e}{Background_colors.END}")
        st.stop()
    
    try:
        st.write("### Top Artists")
        st.dataframe(df_top_artists, use_container_width=True)
        verbose_output(f"{Background_colors.GREEN}Successfully displayed top artists{Background_colors.END}")
    except Exception as e:
        st.error(f"Error: {e}")
        logger.error(f"Error: {e}")
        verbose_output(f"{Background_colors.RED}Error: {e}{Background_colors.END}")
        st.stop()

    try:
        st.write("### Top Artists Chart")
        df_melt = df_top_artists.melt(id_vars=['artist'], value_vars=['play_count', 'unique_listeners', 'total_minutes_played'], var_name='Metric', value_name='Value')
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(data=df_melt, x='artist', y='Value', hue='Metric', ax=ax, palette='viridis')
        ax.set_title("Top Artists by Plays, Listeners, and Minutes")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        for container in ax.containers:
            ax.bar_label(container, fmt='%.0f', padding=3)
        st.pyplot(fig)
        verbose_output(f"{Background_colors.GREEN}Successfully displayed top artists chart{Background_colors.END}")
    except Exception as e:
        st.error(f"Error: {e}")
        logger.error(f"Error: {e}")
        verbose_output(f"{Background_colors.RED}Error: {e}{Background_colors.END}")
        st.stop()

# Music listening trends by time
elif menu == "Music listening trends by time":
    st.title("Music listening trends by time")
    try:
        df_music_listening_trends_by_time = client.query_df("SELECT * FROM mart_hourly_trends")
        verbose_output(f"{Background_colors.GREEN}Successfully retrieved music listening trends by time{Background_colors.END}")
    except Exception as e:
        st.error(f"Error: {e}")
        logger.error(f"Error: {e}")
        verbose_output(f"{Background_colors.RED}Error: {e}{Background_colors.END}")
        st.stop()
    try:
        st.write("### Music listening trends by time")
        st.dataframe(df_music_listening_trends_by_time, use_container_width=True)
        verbose_output(f"{Background_colors.GREEN}Successfully displayed music listening trends by time{Background_colors.END}")
    except Exception as e:
        st.error(f"Error: {e}")
        logger.error(f"Error: {e}")
        verbose_output(f"{Background_colors.RED}Error: {e}{Background_colors.END}")
        st.stop()

    try:
        st.write("### Music listening trends by time Chart")
        df_melt = df_music_listening_trends_by_time.melt(id_vars=['hour_timestamp'], value_vars=['total_listens', 'unique_listeners'], var_name='Metric', value_name='Count')
        fig, ax = plt.subplots(figsize=(12, 5))
        sns.lineplot(data=df_melt, x='hour_timestamp', y='Count', hue='Metric', marker='o', ax=ax)
        ax.set_title("Music Listening Trends over Time")
        st.pyplot(fig)
        verbose_output(f"{Background_colors.GREEN}Successfully displayed music listening trends by time chart{Background_colors.END}")
    except Exception as e:
        st.error(f"Error: {e}")
        logger.error(f"Error: {e}")
        verbose_output(f"{Background_colors.RED}Error: {e}{Background_colors.END}")
        st.stop()

# Top listening trends by areas
elif menu == "Top listening trends by areas":
    st.title("Top listening trends by areas")
    try:
        df_top_listening_trends_by_areas = client.query_df("SELECT * FROM mart_location_stats ORDER BY total_plays DESC LIMIT 10")
        verbose_output(f"{Background_colors.GREEN}Successfully retrieved top listening trends by areas{Background_colors.END}")
    except Exception as e:
        st.error(f"Error: {e}")
        logger.error(f"Error: {e}")
        verbose_output(f"{Background_colors.RED}Error: {e}{Background_colors.END}")
        st.stop()
        
    try:
        st.write("### Top listening trends by areas")
        st.dataframe(df_top_listening_trends_by_areas, use_container_width=True)
        verbose_output(f"{Background_colors.GREEN}Successfully displayed top listening trends by areas{Background_colors.END}")
    except Exception as e:
        st.error(f"Error: {e}")
        logger.error(f"Error: {e}")
        verbose_output(f"{Background_colors.RED}Error: {e}{Background_colors.END}")
        st.stop()

    try:
        st.write("### Top listening trends by areas Chart")
        df_melt = df_top_listening_trends_by_areas.melt(id_vars=['location'], value_vars=['total_plays', 'unique_users'], var_name='Metric', value_name='Value')
        fig, ax = plt.subplots(figsize=(12, 6))
        sns.barplot(data=df_melt, x='location', y='Value', hue='Metric', ax=ax, palette='mako')
        ax.set_title("Listening Trends by Area")
        ax.set_xticklabels(ax.get_xticklabels(), rotation=45, ha='right')
        for container in ax.containers:
            ax.bar_label(container, fmt='%.0f', padding=3)
        st.pyplot(fig)
        verbose_output(f"{Background_colors.GREEN}Successfully displayed top listening trends by areas chart{Background_colors.END}")
    except Exception as e:
        st.error(f"Error: {e}")
        logger.error(f"Error: {e}")
        verbose_output(f"{Background_colors.RED}Error: {e}{Background_colors.END}")
        st.stop()
