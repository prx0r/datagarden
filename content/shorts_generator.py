"""
Datagarden — Free YouTube Shorts Generator

Uses only free tools:
- Groq API (script generation) — free tier
- Edge-TTS (voiceover) — free, Microsoft
- Pexels API (background images) — free
- Pillow (thumbnails/text overlays) — free
- FFmpeg (video assembly) — free
- YouTube Data API v3 (upload) — free 10k units/day
"""

import os
import json
import asyncio
import subprocess
import textwrap
from pathlib import Path
from datetime import datetime

try:
    import edge_tts
except ImportError:
    print("pip install edge-tts")
    exit(1)

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("pip install Pillow")
    exit(1)

try:
    import requests
except ImportError:
    print("pip install requests")
    exit(1)


OUTPUT_DIR = Path(__file__).parent.parent / 'content' / 'shorts'


def generate_script(topic: str, title: str) -> str:
    """Generate a 30-second script using Groq (free) or fallback."""
    # For now, generate a template script
    # In production, use Groq API with Llama 3
    script = f"{title}. Here's what the data shows."
    return script


def generate_voiceover(text: str, output_path: str, voice: str = "en-GB-RyanNeural"):
    """Generate voiceover using Edge-TTS (free, Microsoft)."""
    async def _generate():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
    asyncio.run(_generate())


def create_text_frame(text: str, width: int = 1080, height: int = 1920,
                      bg_color: str = "#1a1a2e", text_color: str = "#ffffff") -> str:
    """Create a text frame using Pillow (free)."""
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Wrap text
    wrapped = textwrap.fill(text, width=25)
    lines = wrapped.split('\n')

    # Use default font (or load a better one if available)
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
    except:
        font = ImageFont.load_default()

    # Center text
    total_height = len(lines) * 60
    y_start = (height - total_height) // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = y_start + i * 60
        draw.text((x, y), line, fill=text_color, font=font)

    output_path = f"/tmp/frame_{datetime.now():%Y%m%d_%H%M%S}.png"
    img.save(output_path)
    return output_path


def create_thumbnail(title: str, subtitle: str = "", output_path: str = None) -> str:
    """Create a YouTube thumbnail."""
    width, height = 1280, 720
    img = Image.new('RGB', (width, height), "#1a1a2e")
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 64)
        sub_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 36)
    except:
        title_font = ImageFont.load_default()
        sub_font = ImageFont.load_default()

    # Title
    wrapped = textwrap.fill(title, width=20)
    lines = wrapped.split('\n')
    y = 100
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y), line, fill="#ff6b35", font=title_font)
        y += 80

    # Subtitle
    if subtitle:
        bbox = draw.textbbox((0, 0), subtitle, font=sub_font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        draw.text((x, y + 40), subtitle, fill="#ffffff", font=sub_font)

    if output_path is None:
        output_path = f"/tmp/thumbnail_{datetime.now():%Y%m%d_%H%M%S}.png"
    img.save(output_path)
    return output_path


def assemble_short(frame_path: str, audio_path: str, output_path: str,
                   duration: float = 30.0):
    """Assemble frame + audio into a Short using FFmpeg."""
    cmd = [
        'ffmpeg', '-y',
        '-loop', '1',
        '-i', frame_path,
        '-i', audio_path,
        '-c:v', 'libx264',
        '-tune', 'stillimage',
        '-c:a', 'aac',
        '-b:a', '192k',
        '-pix_fmt', 'yuv420p',
        '-t', str(duration),
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
        output_path
    ]
    subprocess.run(cmd, capture_output=True)
    return output_path


def generate_short(title: str, script: str = None, topic: str = None) -> dict:
    """Full pipeline: script → voice → frame → video → thumbnail."""
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    timestamp = datetime.now():%Y%m%d_%H%M%S

    # Script
    if script is None:
        script = generate_script(topic or title, title)

    # Voiceover
    audio_path = str(OUTPUT_DIR / f"audio_{timestamp}.mp3")
    generate_voiceover(script, audio_path)

    # Frame
    frame_path = create_text_frame(title)

    # Video
    video_path = str(OUTPUT_DIR / f"short_{timestamp}.mp4")
    assemble_short(frame_path, audio_path, video_path)

    # Thumbnail
    thumb_path = str(OUTPUT_DIR / f"thumb_{timestamp}.png")
    create_thumbnail(title, subtitle="Data says...", output_path=thumb_path)

    return {
        'video': video_path,
        'thumbnail': thumb_path,
        'audio': audio_path,
        'title': title,
        'script': script,
    }


if __name__ == '__main__':
    result = generate_short(
        title="Things people are selling too cheaply",
        script="The median sold price for used Technics turntables is £185. "
               "But on Facebook Marketplace right now, there are 12 listed under £80. "
               "That's a 56% spread. Here's the data.",
    )
    print(f"Video: {result['video']}")
    print(f"Thumbnail: {result['thumbnail']}")
