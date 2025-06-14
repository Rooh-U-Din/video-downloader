import streamlit as st
import yt_dlp
import os
import re
from pathlib import Path
from io import BytesIO
import yt_dlp.utils

# Add this before your download functions
yt_dlp.utils.std_headers['User-Agent'] = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

# 📁 Folder for downloads
DOWNLOAD_FOLDER = "downloads"
Path(DOWNLOAD_FOLDER).mkdir(exist_ok=True)

# 🚫 Fix: Remove dangerous characters in filenames
def sanitize_filename(title, max_length=100):
    title = re.sub(r'[\\/*?:"<>|🥵\u0000-\u001F]', "", title)
    title = re.sub(r'\s+', ' ', title).strip()
    return title[:max_length]

# 🔄 Progress bar
progress_bar = st.progress(0)

# ✅ Download progress update
def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').replace('%', '')
        try:
            progress_bar.progress(float(percent) / 100)
        except:
            pass

# 🎥 Download Video Function (Safe)
def download_video(url, quality):
    try:
        # Step 1: Extract info to get title
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = sanitize_filename(info.get('title', 'video'))

        filename = os.path.join(DOWNLOAD_FOLDER, f"{title}.mp4")

        # Step 2: Set download options with improved format selection
        ydl_opts = {
            'format': f'bestvideo[height<={quality}]+bestaudio/best[height<={quality}]',
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{title}.%(ext)s'),
            'postprocessors': [{'key': 'FFmpegVideoConvertor', 'preferedformat': 'mp4'}],
            'quiet': True,
        }

        # Step 3: Download video
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        # Check for both possible extensions (.mp4 and .mkv)
        if not os.path.exists(filename):
            filename = os.path.join(DOWNLOAD_FOLDER, f"{title}.mkv")
            if not os.path.exists(filename):
                return False, "Downloaded file not found.", None

        return True, title, filename

    except Exception as e:
        return False, str(e), None

# 🎧 Download Audio Function (Safe)
def download_audio(url, audio_quality):
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = sanitize_filename(info.get('title', 'audio'))

        filename = os.path.join(DOWNLOAD_FOLDER, f"{title}.mp3")

        ydl_opts = {
            'format': 'bestaudio/best',
            'progress_hooks': [progress_hook],
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{title}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': audio_quality,
            }],
            'quiet': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        if not os.path.exists(filename):
            return False, "Downloaded audio not found.", None

        return True, title, filename

    except Exception as e:
        return False, str(e), None

# 🌐 Streamlit UI
st.title("🎬Video & Audio Downloader")
st.write("Download YouTube videos and audio directly from the web.")

url = st.text_input("🔗 YouTube or Facebook Video URL:", placeholder="https://www.youtube.com/watch?v=...")
quality = st.selectbox("🎥 Video Quality:", ["4320", "2160", "1440", "1080", "720", "480", "360"])
audio_quality = st.selectbox("🎧 Audio Quality:", ["64k", "128k", "192k"])

# 📥 Download Video
if st.button("📽️ Download Video"):
    progress_bar.progress(0)
    if url:
        with st.spinner("⏬ Video is downloading"):
            success, title, filepath = download_video(url, quality)
            if success:
                st.success(f"✅ Video downloaded: {title}")
                with open(filepath, "rb") as f:
                    st.download_button(
                        label="💾 Save Video",
                        data=BytesIO(f.read()),
                        file_name=os.path.basename(filepath),
                        mime="video/mp4"
                    )
                os.remove(filepath)  # ✅ Clean up file (optional)
                progress_bar.progress(100)
            else:
                st.error(f"❌ Error: {title}")
    else:
        st.warning("⚠️ Please enter link")
# 🎵 Download Audio
if st.button("🎵 Audio Download"):
    progress_bar.progress(0)
    if url:
        with st.spinner("⏬ Audio is downloading..."):
            success, title, filepath = download_audio(url, audio_quality)
            if success:
                st.success(f"✅ MP3 downloaded: {title}")
                with open(filepath, "rb") as f:
                    st.download_button(
                        label="💾 Save Audio",
                        data=BytesIO(f.read()),
                        file_name=os.path.basename(filepath),
                        mime="audio/mp3"
                    )
                os.remove(filepath)
                progress_bar.progress(100)
            else:
                st.error(f"❌ Error: {title}")
    else:
        st.warning("⚠️ Enter Video link")
