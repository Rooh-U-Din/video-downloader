import streamlit as st
import yt_dlp
import os
from pathlib import Path

# Configuration
DOWNLOAD_FOLDER = "downloads"
Path(DOWNLOAD_FOLDER).mkdir(exist_ok=True)

# Progress Hook
def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').replace('%', '')
        try:
            progress_float = float(percent)
            progress_bar.progress(progress_float / 100)
        except:
            pass

# Download Video Function
def download_video(url, quality, platform):
    try:
        ydl_opts = {
            'progress_hooks': [progress_hook],
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]' if "facebook" in platform.lower() else f'bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=m4a]/best'
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video')
            filename = ydl.prepare_filename(info)
            ydl.download([url])
        return True, title, filename
    except Exception as e:
        return False, str(e), None

# Download Audio Function
def download_audio(url, audio_quality):
    try:
        ydl_opts = {
            'format': 'bestaudio/best',
            'progress_hooks': [progress_hook],
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': audio_quality,
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'audio')
            filename = os.path.splitext(ydl.prepare_filename(info))[0] + ".mp3"
            ydl.download([url])
        return True, title, filename
    except Exception as e:
        return False, str(e), None

# Streamlit UI
st.title("Video & Audio Downloader")
st.write("Download videos or audio from YouTube and Facebook.")

url = st.text_input("Enter Video URL:", placeholder="https://...")

# Detect platform
platform = "facebook" if "facebook.com" in url.lower() else "youtube" if "youtube.com" in url.lower() else "other" "instagram" if "instagram.com" in url.lower() else "other"

# Quality Selection
quality = st.selectbox("Select video quality:", ["4320", "2160", "1440", "1080", "720", "480", "360"])
audio_quality = st.selectbox("Select audio quality:", ["64k", "128k", "192k"])

progress_bar = st.progress(0)

# Download Video Button
if st.button("Download Video"):
    progress_bar.progress(0)
    if url:
        with st.spinner("Downloading video..."):
            success, message, filename = download_video(url, quality, platform)
            if success:
                st.success(f"Video downloaded: {message}")
                progress_bar.progress(100)
                with open(filename, "rb") as file:
                    st.download_button(
                        label="Save Video to Your Device",
                        data=file,
                        file_name=os.path.basename(filename),
                        mime="video/mp4"
                    )
            else:
                st.error(f"Error: {message}")
    else:
        st.warning("Please enter a valid video URL")

# Download Audio Button
if st.button("Download Audio"):
    progress_bar.progress(0)
    if url:
        with st.spinner("Downloading audio..."):
            success, message, filename = download_audio(url, audio_quality)
            if success:
                st.success(f"Audio downloaded: {message}")
                progress_bar.progress(100)
                with open(filename, "rb") as file:
                    st.download_button(
                        label="Save Audio to Your Device",
                        data=file,
                        file_name=os.path.basename(filename),
                        mime="audio/mp3"
                    )
            else:
                st.error(f"Error: {message}")
    else:
        st.warning("Please enter a valid video URL")
