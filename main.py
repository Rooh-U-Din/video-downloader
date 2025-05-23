import streamlit as st
import yt_dlp
import os
from pathlib import Path

# Configuration
DOWNLOAD_FOLDER = "downloads"
Path(DOWNLOAD_FOLDER).mkdir(exist_ok=True)

def download_video(url, quality, platform):
    try:
        ydl_opts = {
            'progress_hooks': [progress_hook],
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
        }
        
        # Platform-specific format selection
        if "facebook" in platform.lower():
            ydl_opts['format'] = f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]'
        else:  # YouTube and others
            ydl_opts['format'] = f'bestvideo[ext=mp4][height<={quality}]+bestaudio[ext=m4a]/best'
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'video')
            filename = ydl.prepare_filename(info)
            ydl.download([url])
        return True, title, filename
    except Exception as e:
        return False, str(e), None

def progress_hook(d):
    if d['status'] == 'downloading':
        progress = d.get('_percent_str', '0%')
        progress = progress.replace('%', '')
        try:
            progress_float = float(progress)
            progress_bar.progress(progress_float / 100)
        except:
            pass

# Streamlit UI
st.title("Video Downloader")
st.write("Download videos from YouTube and Facebook.")

url = st.text_input("Enter Video URL:", placeholder="https://...")

# Detect platform
platform = "facebook" if "facebook.com" in url.lower() else "youtube" if "youtube.com" in url.lower() else "other"

# Quality options (common options that work for both platforms)
quality = st.selectbox(
    "Select video quality:",
    options=["4320","2160","1440","1080", "720", "480", "360"],
    index=0 if platform == "facebook" else 1  # Default to 720p for YouTube
)

progress_bar = st.progress(0)

if st.button("Download Video"):
    if url:
        with st.spinner("Downloading..."):
            success, message, filename = download_video(url, quality, platform)
            if success:
                st.success(f"Download complete: {message}")
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
                progress_bar.progress(0)
    else:
        st.warning("Please enter a video URL")

