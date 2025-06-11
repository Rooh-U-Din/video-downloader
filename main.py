import streamlit as st
import yt_dlp
import os
from pathlib import Path
from yt_dlp.utils import sanitize_filename

# Configuration
DOWNLOAD_FOLDER = "downloads"
Path(DOWNLOAD_FOLDER).mkdir(exist_ok=True)

# Progress bar placeholder
progress_bar = st.progress(0)

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
def download_video(url, quality):
    try:
        ydl_opts = {
            'format': f'bestvideo[height={quality}]+bestaudio/best/best[height<={quality}]',
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, '%(title)s.%(ext)s'),
            'postprocessors': [{'key': 'FFmpegMerger'}],
            'extractor_args': {
                'youtube': {
                    'player_client': ['desktop'],
                }
            }
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = sanitize_filename(info.get('title', 'video'))
            ydl.download([url])
            filename = os.path.splitext(ydl.prepare_filename(info))[0] + ".mp4"

        if not os.path.exists(filename):
            return False, "Downloaded file not found.", None

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
            title = sanitize_filename(info.get('title', 'audio'))
            ydl.download([url])
            filename = os.path.splitext(ydl.prepare_filename(info))[0] + ".mp3"

        if not os.path.exists(filename):
            return False, "Downloaded audio not found.", None

        return True, title, filename

    except Exception as e:
        return False, str(e), None

# Streamlit UI
st.title("🎬 YouTube Video & Audio Downloader")
st.write("HD video ya MP3 download karein YouTube se.")

url = st.text_input("🔗 Video URL daalein:", placeholder="https://www.youtube.com/watch?v=...")

quality = st.selectbox("🎥 Video quality chunein:", ["4320", "2160", "1440", "1080", "720", "480", "360"])
audio_quality = st.selectbox("🎧 Audio quality chunein:", ["64k", "128k", "192k"])

# Download Video
if st.button("📥 Video Download karein"):
    progress_bar.progress(0)
    if url:
        with st.spinner("Video download ho raha hai..."):
            success, message, filename = download_video(url, quality)
            if success:
                st.success(f"✅ Video download hogaya: {message}")
                progress_bar.progress(100)
                with open(filename, "rb") as file:
                    st.download_button(
                        label="💾 Save Video",
                        data=file,
                        file_name=os.path.basename(filename),
                        mime="video/mp4"
                    )
            else:
                st.error(f"❌ Error: {message}")
    else:
        st.warning("⚠️ Valid YouTube URL daalein")

# Download Audio
if st.button("🎵 Sirf MP3 Download karein"):
    progress_bar.progress(0)
    if url:
        with st.spinner("Audio download ho raha hai..."):
            success, message, filename = download_audio(url, audio_quality)
            if success:
                st.success(f"✅ Audio download hogaya: {message}")
                progress_bar.progress(100)
                with open(filename, "rb") as file:
                    st.download_button(
                        label="💾 Save Audio",
                        data=file,
                        file_name=os.path.basename(filename),
                        mime="audio/mp3"
                    )
            else:
                st.error(f"❌ Error: {message}")
    else:
        st.warning("⚠️ Valid YouTube URL daalein")
