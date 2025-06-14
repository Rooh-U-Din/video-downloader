import streamlit as st
import yt_dlp
import os
from pathlib import Path
import re

# --- Utility ---
def sanitize_filename(title, max_length=100):
    title = re.sub(r'[\\/*?:"<>|🥵\u0000-\u001F]', "", title)  # Invalid chars
    title = re.sub(r'\s+', ' ', title).strip()  # Extra spaces
    return title[:max_length]  # Max length

# --- Config ---
DOWNLOAD_FOLDER = "downloads"
Path(DOWNLOAD_FOLDER).mkdir(exist_ok=True)

# --- Progress Bar ---
progress_bar = st.progress(0)

def progress_hook(d):
    if d['status'] == 'downloading':
        percent = d.get('_percent_str', '0%').replace('%', '')
        try:
            progress_bar.progress(float(percent) / 100)
        except:
            pass

# --- Download Video ---
def download_video(url, quality):
    try:
        # Extract info for title
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = sanitize_filename(info.get('title', 'video'))

        # Options
        ydl_opts = {
            'format': f'bestvideo[height={quality}]+bestaudio/best/best[height<={quality}]',
            'merge_output_format': 'mp4',
            'progress_hooks': [progress_hook],
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{title}.%(ext)s'),
            'postprocessors': [{'key': 'FFmpegMerger'}],
            'extractor_args': {'youtube': {'player_client': ['desktop']}}
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        filename = os.path.join(DOWNLOAD_FOLDER, f"{title}.mp4")

        if not os.path.exists(filename):
            return False, "Downloaded file not found.", None

        return True, title, filename

    except Exception as e:
        return False, str(e), None

# --- Download Audio ---
def download_audio(url, audio_quality):
    try:
        with yt_dlp.YoutubeDL({'quiet': True}) as ydl:
            info = ydl.extract_info(url, download=False)
            title = sanitize_filename(info.get('title', 'audio'))

        ydl_opts = {
            'format': 'bestaudio/best',
            'progress_hooks': [progress_hook],
            'outtmpl': os.path.join(DOWNLOAD_FOLDER, f'{title}.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': audio_quality,
            }]
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

        filename = os.path.join(DOWNLOAD_FOLDER, f"{title}.mp3")

        if not os.path.exists(filename):
            return False, "Downloaded audio not found.", None

        return True, title, filename

    except Exception as e:
        return False, str(e), None

# --- Streamlit UI ---
st.title("🎬 YouTube Video & Audio Downloader")
st.write("HD video ya MP3 download karein YouTube se.")

url = st.text_input("🔗 YouTube Video URL:", placeholder="https://www.youtube.com/watch?v=...")
quality = st.selectbox("🎥 Video Quality:", ["4320", "2160", "1440", "1080", "720", "480", "360"])
audio_quality = st.selectbox("🎧 MP3 Quality:", ["64k", "128k", "192k"])

# --- Video Download Button ---
if st.button("📥 Video Download karein"):
    progress_bar.progress(0)
    if url:
        with st.spinner("Video downloading..."):
            success, message, filename = download_video(url, quality)
            if success:
                st.success(f"✅ Video downloaded: {message}")
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
        st.warning("⚠️ YouTube URL daalein.")

# --- Audio Download Button ---
if st.button("🎵 MP3 Download karein"):
    progress_bar.progress(0)
    if url:
        with st.spinner("Audio downloading..."):
            success, message, filename = download_audio(url, audio_quality)
            if success:
                st.success(f"✅ Audio downloaded: {message}")
                progress_bar.progress(100)
                with open(filename, "rb") as file:
                    st.download_button(
                        label="💾 Save MP3",
                        data=file,
                        file_name=os.path.basename(filename),
                        mime="audio/mp3"
                    )
            else:
                st.error(f"❌ Error: {message}")
    else:
        st.warning("⚠️ YouTube URL daalein.")
