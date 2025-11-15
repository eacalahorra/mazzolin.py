import time
import subprocess
import shutil
import os
import sys
import re

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

AUDIO_FILE = resource_path("mazzolin.mp3")
SRT_FILE = resource_path("mazzolin.srt")
FFPLAY_PATH = resource_path("ffplay.exe")

FLOWER = "  @--<3--🌸"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def find_player():
    candidates = [
        ("ffplay", [FFPLAY_PATH, "-nodisp", "-autoexit", AUDIO_FILE]),
        ("afplay", ["afplay", AUDIO_FILE]),  # macOS
        ("vlc",    ["vlc", "--intf", "dummy", "--play-and-exit", AUDIO_FILE]),
        ("mpg123", ["mpg123", AUDIO_FILE]),
    ]
    for name, cmd in candidates:
        if shutil.which(name) is not None:
            return cmd
    return None

def typewriter(text, delay=0.03):
    for ch in text:
        print(ch, end='', flush=True)
        time.sleep(delay)
    print()

def start_audio():
    if not os.path.exists(AUDIO_FILE):
        print(f"Audio file '{AUDIO_FILE}' not found.")
        print("Put the song in this folder and/or change AUDIO_FILE at the top of the script.")
        return None

    cmd = find_player()
    if cmd is None:
        print("Could not find a command-line audio player (ffplay/afplay/vlc/mpg123).")
        print("Start the song manually in your player of choice,")
        input("then press Enter here to sync the lyrics: ")
        return None

    return subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)


def srt_time_to_seconds(t: str) -> float:

    hours, minutes, rest = t.split(":")
    seconds, millis = rest.split(",")
    total = (
        int(hours) * 3600 +
        int(minutes) * 60 +
        int(seconds) +
        int(millis) / 1000.0
    )
    return total


def parse_srt(path: str):

    if not os.path.exists(path):
        print(f"SRT file '{path}' not found.")
        sys.exit(1)

    with open(path, "r", encoding="utf-8-sig") as f:
        content = f.read()

    content = content.replace("\r\n", "\n").replace("\r", "\n")

    if not content.endswith("\n"):
        content += "\n"

    blocks = re.split(r"\n\s*\n", content.strip(), flags=re.MULTILINE)

    entries = []
    timecode_pattern = re.compile(
        r"(\d{2}:\d{2}:\d{2},\d{3})\s*-->\s*(\d{2}:\d{2}:\d{2},\d{3})"
    )

    for block in blocks:
        lines = block.strip().split("\n")
        if len(lines) < 2:
            continue


        match = None
        time_line_index = None
        for i, line in enumerate(lines):
            m = timecode_pattern.search(line)
            if m:
                match = m
                time_line_index = i
                break

        if not match:
            continue

        start_str = match.group(1)
        start_seconds = srt_time_to_seconds(start_str)

        text_lines = lines[time_line_index + 1 :]
        text_lines = [re.sub(r"<.*?>", "", tl).strip() for tl in text_lines]
        text_lines = [tl for tl in text_lines if tl]

        if not text_lines:
            continue

        text = " ".join(text_lines)
        entries.append((start_seconds, text))

    entries.sort(key=lambda x: x[0])

    return entries


def main():
    clear_screen()
    print("🌼 Quel mazzolin di fiori — terminal 🌼")
    print()
    print(f"Audio file: {AUDIO_FILE}")
    print(f"Subtitle file: {SRT_FILE}")
    print()

    print("Parsing SRT…")
    lyrics = parse_srt(SRT_FILE)
    if not lyrics:
        print("No valid subtitle entries found in the SRT file.")
        sys.exit(1)

    print(f"Loaded {len(lyrics)} lines.")
    print("Press Enter to start playback and lyric sync...")
    input()

    proc = start_audio()
    start_time = time.time()

    current_index = 0
    total_lines = len(lyrics)

    try:
        while current_index < total_lines:
            now = time.time() - start_time
            next_time, text = lyrics[current_index]

            if now >= next_time:
                typewriter(f"{text:<70}{FLOWER}", delay=0.05)
                current_index += 1
            else:
                time.sleep(0.02)  

        print()
        print("🌸 Fine! 🌸")

        if proc is not None:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                pass

    except KeyboardInterrupt:
        clear_screen()
        print("Closed. Alla prossima 🌼")
        sys.exit(0)


if __name__ == "__main__":
    main()
