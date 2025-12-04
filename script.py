import random
import datetime
import yt_dlp
import os
import logging
import json
from pathlib import Path

# --- Load channels from JSON (same directory as this script) ---
_here = Path(__file__).resolve().parent
with open(_here / "YT_channels.json", "r", encoding="utf-8") as f:
    channel_metadata = json.load(f)

# --- Setup logging ---
logger = logging.getLogger("yt_logger")
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(asctime)s - %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)

# --- Cookies file ---
cookies_file_path = 'cookies.txt'
if not os.path.exists(cookies_file_path):
    raise FileNotFoundError(f"Missing cookies file!")

# --- User-Agent generator ---
def get_user_agent():
    versions = [(122, 6267, 70), (121, 6167, 131), (120, 6099, 109)]
    major, build, patch = random.choice(versions)
    return (
        f"Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        f"AppleWebKit/537.36 (KHTML, like Gecko) "
        f"Chrome/{major}.0.{build}.{patch} Safari/537.36"
    )

# --- Get Live Watch URL ---
def get_live_watch_url(channel_id):
    url = f"https://www.youtube.com/channel/{channel_id}/live"
    opts = {
        "cookiefile": cookies_file_path,
        "quiet": True,
        "no_warnings": True,
        "force_ipv4": True,
        "http_headers": {"User-Agent": get_user_agent()},
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            if info.get("is_live"):
                return info.get("webpage_url")
            if "entries" in info:
                for item in info["entries"]:
                    if item.get("is_live"):
                        return item.get("webpage_url")
    except:
        return None
    return None

# --- Get m3u8 stream ---
def get_stream_url(url):
    opts = {
        "format": "best",
        "quiet": True,
        "cookiefile": cookies_file_path,
        "force_ipv4": True,
    }
    try:
        with yt_dlp.YoutubeDL(opts) as ydl:
            info = ydl.extract_info(url, download=False)
            for fmt in info["formats"]:
                if fmt.get("protocol") in ["m3u8", "m3u8_native"]:
                    return fmt.get("manifest_url")
    except:
        return None
    return None

# --- Format Playlist ---
def format_link(name, logo, link, group):
    return f'#EXTINF:-1 group-title="{group}" tvg-logo="{logo}", {name}\n{link}'

# --- Save playlist ---
def save_playlist(data):
    with open("YT_playlist.m3u", "w", encoding="utf-8") as f:
        f.write("#EXTM3U\n")
        f.write(f"# Updated {datetime.datetime.now()}\n")
        for line in data:
            f.write(line + "\n")
    print("Playlist updated!")

# --- Main ---
def main():
    output = []
    for cid, meta in channel_metadata.items():
        print("Checking:", meta["channel_name"])
        live = get_live_watch_url(cid)
        if not live:
            print("Not live!")
            continue
        stream = get_stream_url(live)
        if not stream:
            print("Stream not found")
            continue
        output.append(format_link(meta["channel_name"], meta["channel_logo"], stream, meta["group_title"]))
    save_playlist(output)

if __name__ == "__main__":
    main()
