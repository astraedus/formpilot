#!/usr/bin/env python3
"""Final render: combine prepared images + audio into demo.mp4 with proper audio."""

import os
import subprocess

DIR = "/home/astraedus/projects/formpilot/demo/v2"
W, H = 1920, 1080

# Segment definitions: (image_key, audio_num_or_None, duration)
# duration=None means use audio duration
SEGMENTS = [
    ("title",    None,  3.0),    # Title slide, 3s silent
    ("seg_01",   1,     None),   # Chrome extension intro
    ("seg_02",   2,     None),   # Government forms
    ("seg_03",   3,     None),   # Form page, click icon
    ("seg_04",   4,     None),   # Enter context
    ("seg_05",   5,     None),   # Click Analyze
    ("seg_06",   6,     None),   # Sends to Gemini Vision
    ("seg_07",   7,     None),   # Numbered circles
    ("seg_08",   8,     None),   # Autofill All
    ("seg_09",   9,     None),   # Works on any form
    ("arch",     10,    None),   # Architecture diagram
    ("closing",  None,  4.0),    # Closing slide, 4s silent
]

def get_audio_duration(audio_path):
    result = subprocess.run(
        ["ffprobe", "-i", audio_path, "-show_entries", "format=duration",
         "-v", "quiet", "-of", "csv=p=0"],
        capture_output=True, text=True
    )
    return float(result.stdout.strip())

# Build one large ffmpeg command with all inputs and filter_complex
# Strategy: for each segment, create image video + audio, then concatenate with audio

print("Building individual segment videos with audio...")

segment_videos = []

for seg_key, audio_num, dur in SEGMENTS:
    img_path = os.path.join(DIR, f"prepared_{seg_key}.png")
    out_path = os.path.join(DIR, f"v2_{seg_key}.mp4")
    segment_videos.append(out_path)

    if audio_num is not None:
        audio_path = os.path.join(DIR, f"audio_{audio_num:02d}.mp3")
        actual_dur = get_audio_duration(audio_path)

        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", img_path,
            "-i", audio_path,
            "-c:v", "libx264", "-preset", "fast",
            "-r", "30", "-pix_fmt", "yuv420p",
            "-vf", f"scale={W}:{H}",
            "-c:a", "aac", "-b:a", "128k",
            "-t", str(actual_dur),
            "-shortest",
            out_path
        ]
    else:
        # Silent segment: generate silent audio
        cmd = [
            "ffmpeg", "-y",
            "-loop", "1", "-i", img_path,
            "-f", "lavfi", "-i", "anullsrc=r=44100:cl=stereo",
            "-c:v", "libx264", "-preset", "fast",
            "-r", "30", "-pix_fmt", "yuv420p",
            "-vf", f"scale={W}:{H}",
            "-c:a", "aac", "-b:a", "128k",
            "-t", str(dur),
            "-shortest",
            out_path
        ]

    print(f"  {seg_key}...")
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"  ERROR: {result.stderr[-300:]}")
        raise RuntimeError(f"Failed for {seg_key}")

print("\nConcatenating all segments...")

concat_list = os.path.join(DIR, "concat_final.txt")
with open(concat_list, "w") as f:
    for sv in segment_videos:
        f.write(f"file '{sv}'\n")

output = os.path.join(DIR, "demo.mp4")
cmd = [
    "ffmpeg", "-y",
    "-f", "concat", "-safe", "0",
    "-i", concat_list,
    "-c:v", "libx264", "-preset", "fast",
    "-r", "30", "-pix_fmt", "yuv420p",
    "-c:a", "aac", "-b:a", "128k",
    output
]

result = subprocess.run(cmd, capture_output=True, text=True)
if result.returncode != 0:
    print(f"ERROR:\n{result.stderr[-500:]}")
    raise RuntimeError("Final concat failed")

# Verify
result = subprocess.run(
    ["ffprobe", "-v", "error", "-show_streams", output],
    capture_output=True, text=True
)
streams = result.stdout

result2 = subprocess.run(
    ["ffprobe", "-i", output, "-show_entries", "format=duration",
     "-v", "quiet", "-of", "csv=p=0"],
    capture_output=True, text=True
)
dur = float(result2.stdout.strip())
size = os.path.getsize(output) / (1024 * 1024)

print(f"\nDone!")
print(f"Output: {output}")
print(f"Duration: {dur:.1f}s ({dur/60:.1f} min)")
print(f"Size: {size:.1f} MB")

# Check streams
has_video = "codec_name=h264" in streams
has_audio = "codec_name=aac" in streams
print(f"Has video: {has_video}")
print(f"Has audio: {has_audio}")
