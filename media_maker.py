#!/opt/whisper/venv/bin/python3.12

import os
import re
import argparse
import subprocess
import concurrent.futures
from pathlib import Path
import whisper
import requests
import datetime
import shutil

def NotifyMe(title: str = 'New Message', priority: str = '3', tags: str = 'incoming_envelope', message: str = 'No message included'):
    NTFY_PATH = os.path.join(os.environ['HOME'], '.config', '.credentials', 'ntfy.url')
    with open(NTFY_PATH, 'r') as file:
        NTFY_URL = file.readline().strip()

    headers = {
        "Title": title,
        "Priority": priority,
        "Tags": tags
    }

    data = (f"{message}\n").encode(encoding='utf-8')
    requests.post(NTFY_URL, data=data, headers=headers)

def LogIt(LOG: str = None, message: str = None, LEVEL: str = 'info'):
    import logging
    log_directory = '/opt/whisper/logs'
    os.makedirs(log_directory, exist_ok=True)

    logger = logging.getLogger(LOG)

    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)
        formatter = logging.Formatter('%(asctime)s:%(levelname)s :::[ ' + f'{LOG}' + ' ]::: %(message)s')
        file_handler = logging.FileHandler(f'{log_directory}/{LOG}', mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    log_level = {
        'debug': logging.DEBUG,
        'info': logging.INFO,
        'warn': logging.WARNING,
        'warning': logging.WARNING,
        'error': logging.ERROR,
        'critical': logging.CRITICAL
    }.get(LEVEL.lower(), logging.INFO)

    if message:
        logger.log(log_level, message)
        if log_level in [logging.ERROR, logging.CRITICAL]:
            NotifyMe(title=f"{LEVEL.upper()} Notification", priority='5', tags='face_with_spiral_eyes', message=message)

    return logger

def validate_imdb_id(imdb_id):
    if not re.match(r'^tt\d{7,9}$', imdb_id):
        raise ValueError("Invalid IMDB ID format. Expected: tt1234567")

    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.imdb.com/title/{imdb_id}/"
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        raise ValueError(f"IMDB ID not found: {imdb_id}")
    return imdb_id

def imdb_name(imdb_id):
    headers = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(f"https://www.imdb.com/title/{imdb_id}/", headers=headers).text
    match = re.search(r'<title>(.*?) - IMDb</title>', html)
    title = match.group(1) if match else "Unknown Title"
    title = re.sub(r'\s+\(\d{4}\)$', '', title.strip())
    if title.lower().startswith("the "):
        title = f"{title[4:]}, The"
    return title

def imdb_year(imdb_id):
    headers = {"User-Agent": "Mozilla/5.0"}
    html = requests.get(f"https://www.imdb.com/title/{imdb_id}/", headers=headers).text
    match = re.search(r'<title>.*\((\d{4})\) - IMDb</title>', html)
    return match.group(1) if match else "0000"

def encode_rung(source_path, output_path, width, height, bitrate, imdb_id, imdb_name, imdb_year, LOGGER):
    profile = "main10:level=6.0" if width == 3840 and height == 2160 else "main10:level=5.1"
    file_name = f"{imdb_name} ({imdb_year}) {{imdb-{imdb_id}}} - {height}p.mkv"
    final_output = output_path / file_name

    NotifyMe(title="Encode Status", message=f"Started encoding {file_name} …")
    LogIt(LOGGER, f"Encoding {file_name} ({width}x{height} @ {bitrate}kbps)", "info")

    command = [
        "HandBrakeCLI",
        "--input", str(source_path),
        "--output", str(final_output),
        "--encoder", "nvenc_h265_10bit",
        "--vb", str(bitrate),
        "--width", str(width),
        "--height", str(height),
        "--aencoder", "av_aac",
        "--audio", "1",
        "--mixdown", "stereo",
        "--ab", "128",
        "--format", "mkv",
        "--optimize",
        "--x265-preset", "fast",
        f"--encopts={profile}"
    ]

    try:
        OUTPUT = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if OUTPUT.returncode == 0:
            LogIt(LOGGER, f"✅ Done: {file_name}", "info")
            NotifyMe(title="Encode Status", message=f"Encoding {file_name} is complete!")
            return True
        else:
            LogIt(LOGGER, f"❌ Encode failed for {file_name} with return code {OUTPUT.returncode}", "error")
            LogIt(LOGGER, f"STDERR:\n{OUTPUT.stderr}", "debug")
            return False
    except Exception as exc:
        LogIt(LOGGER, f"❌ Exception while encoding {file_name}: {exc}", "critical")
        return False

def format_timestamp(seconds):
    hours = int(seconds // 3600)
    minutes = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    millis = int((seconds - int(seconds)) * 1000)
    return f"{hours:02}:{minutes:02}:{secs:02},{millis:03}"

def generate_srt(model, file_path, output_dir, LOGGER):
    LogIt(LOGGER, f"🎮️  Transcribing: {file_path.name}", "info")
    result = model.transcribe(
        str(file_path),
        task="transcribe",
        language="en",
        word_timestamps=True,
        verbose=False
    )
    srt_path = output_dir / (file_path.stem + ".srt")
    with open(srt_path, "w", encoding="utf-8") as f:
        for i, segment in enumerate(result["segments"]):
            f.write(f"{i+1}\n")
            f.write(f"{format_timestamp(segment['start'])} --> {format_timestamp(segment['end'])}\n")
            f.write(segment["text"].strip() + "\n\n")
    LogIt(LOGGER, f"✅ Saved: {srt_path}", "info")

def main():
    parser = argparse.ArgumentParser(description="Encode MKV in multiple resolutions and optionally generate SRT.")
    parser.add_argument("--source", help="Path to source MKV file (optional if only generating SRTs)")
    parser.add_argument("--dest", required=True, help="Destination folder for output or SRTs")
    parser.add_argument("--imdb", help="IMDB ID for the movie (e.g., tt1234567)")
    parser.add_argument("--makesrt", action="store_true", help="Generate SRT subtitles")
    parser.add_argument("--verbose", action="store_true", help="Enable verbose (DEBUG-level) logging")
    args = parser.parse_args()

    bootstrap_logger = "bootstrap.log"
    LogIt(bootstrap_logger, f"⚙️  Launch args: {vars(args)}", "info")

    dest_path = Path(args.dest).resolve()
    if not dest_path.is_dir():
        print(f"❌ Destination directory does not exist: {dest_path}")
        return

    # SRT-only mode if no source or imdb provided
    if args.makesrt and args.source is None and args.imdb is None:
        LOGGER = dest_path.name.lower().replace(" ", "_") + ".log"
        LogIt(LOGGER, f"🔁 SRT-only mode started on: {dest_path}", "info")

        mkvs = sorted(dest_path.glob("*.mkv"))
        if not mkvs:
            LogIt(LOGGER, "❌ No MKV files found in destination for SRT generation.", "error")
            return

        LogIt(LOGGER, f"🎤 Generating SRT subtitles for {len(mkvs)} MKV files...", "info")
        model = whisper.load_model("large-v3", device="cuda")

        for file in mkvs:
            srt_path = file.with_suffix(".srt")
            if srt_path.exists():
                LogIt(LOGGER, f"⚠️  Skipping existing SRT: {srt_path.name}", "info")
                continue
            generate_srt(model, file, dest_path, LOGGER)

        LogIt(LOGGER, "✅ SRT-only generation complete.", "info")
        return

    # Full encode + optional SRT
    source_path = Path(args.source).resolve()
    if not source_path.is_file():
        print(f"❌ Source file does not exist: {source_path}")
        return

    if not shutil.which("HandBrakeCLI"):
        print("❌ HandBrakeCLI is not installed or not in PATH.")
        return

    try:
        imdb_id = validate_imdb_id(args.imdb)
        name = imdb_name(imdb_id)
        year = imdb_year(imdb_id)
    except Exception as e:
        LogIt(bootstrap_logger, f"❌ IMDb metadata fetch failed: {e}", "critical")
        return

    safe_name = ''.join(c if c.isalnum() or c == '_' else '_' for c in name.replace(' ', '_').lower())
    LOGGER = f"{safe_name}.log"
    LogIt(LOGGER, f"🎬 Job started for {name} ({year}) [IMDB {imdb_id}]", "info")

    folder_name = f"{name} ({year}) {{imdb-{imdb_id}}}"
    final_output_path = dest_path / folder_name
    final_output_path.mkdir(parents=True, exist_ok=True)

    ladder = [
        ("3840x2160", 25000),
        ("1920x1080", 5800),
        ("1920x1080", 4300),
        ("1280x720", 3500),
        ("1280x720", 2750),
        ("720x404", 1750),
        ("720x404", 1100),
        ("512x288", 700),
        ("384x216", 400)
    ]

    success_count = 0
    with concurrent.futures.ThreadPoolExecutor(max_workers=len(ladder)) as executor:
        futures = []
        for res, bitrate in ladder:
            width, height = map(int, res.split("x"))
            futures.append(executor.submit(
                encode_rung, source_path, final_output_path,
                width, height, bitrate, imdb_id, name, year, LOGGER
            ))

        for future in concurrent.futures.as_completed(futures):
            try:
                if future.result():
                    success_count += 1
            except Exception as e:
                LogIt(LOGGER, f"Unhandled exception in encoding task: {e}", "critical")

    if success_count == 0 or not any(final_output_path.glob("*.mkv")):
        LogIt(LOGGER, "❌ No successful MKV encodes found. Aborting SRT stage.", "critical")
        return

    LogIt(LOGGER, f"🏁 {success_count} renditions completed successfully.", "info")

    # Delete the source MKV file if it exists
    if source_path.exists() and source_path.is_file() and success_count > 0:
        try:
            source_path.unlink()
            LogIt(LOGGER, f"🗑️  Deleted source file: {source_path.name}", "info")
        except Exception as e:
            LogIt(LOGGER, f"❌ Failed to delete source file {source_path.name}: {e}", "error")

    if args.makesrt:
        LogIt(LOGGER, "🎙️  Generating SRT subtitles...", "info")
        model = whisper.load_model("large-v3", device="cuda")
        for file in sorted(final_output_path.glob("*.mkv")):
            srt_path = file.with_suffix(".srt")
            if not srt_path.exists():
                generate_srt(model, file, final_output_path, LOGGER)
            else:
                LogIt(LOGGER, f"⚠️  Skipping existing SRT: {srt_path.name}", "info")

if __name__ == "__main__":
    main()