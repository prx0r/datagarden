"""
Content Pipeline — Data → Script → Voice → Frame → Video

Free tools only:
- Edge-TTS (voiceover)
- Pillow (text frames / thumbnails)
- FFmpeg (video assembly)

Optional:
- TypeSafe Jev — hypothesis scoring before content creation
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

CONTENT_DIR = Path(__file__).parent.parent / 'content' / 'shorts'

# Font paths (Linux)
FONT_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
FONT_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def generate_script(title: str, answer: str, evidence: list, duration: int = 30) -> str:
    """Generate a short script from data."""
    lines = [
        f"{title}.",
        f"{answer}.",
    ]
    for e in evidence[:2]:
        lines.append(f"{e}.")

    script = ' '.join(lines)

    # Trim to ~150 words for 30 seconds
    words = script.split()
    if len(words) > 150:
        words = words[:150]
        script = ' '.join(words)

    return script


def generate_voiceover(text: str, output_path: str, voice: str = "en-GB-RyanNeural"):
    """Generate voiceover using Edge-TTS (free, Microsoft)."""
    async def _generate():
        communicate = edge_tts.Communicate(text, voice)
        await communicate.save(output_path)
    asyncio.run(_generate())


def get_audio_duration(audio_path: str) -> float:
    """Get audio duration in seconds using ffprobe."""
    try:
        result = subprocess.run(
            ['ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
             '-of', 'default=noprint_wrappers=1:nokey=1', audio_path],
            capture_output=True, text=True
        )
        return float(result.stdout.strip())
    except:
        return 30.0


def create_text_frame(text: str, width: int = 1080, height: int = 1920,
                      bg_color: str = "#1a1a2e", text_color: str = "#ffffff",
                      accent_color: str = "#ff6b35") -> str:
    """Create a text frame using Pillow."""
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)

    # Try to load fonts
    try:
        font = ImageFont.truetype(FONT_BOLD, 52)
        small_font = ImageFont.truetype(FONT_REGULAR, 32)
    except:
        font = ImageFont.load_default()
        small_font = font

    # Wrap text
    wrapped = textwrap.fill(text, width=22)
    lines = wrapped.split('\n')

    # Center text vertically
    total_height = len(lines) * 65
    y_start = (height - total_height) // 2

    for i, line in enumerate(lines):
        bbox = draw.textbbox((0, 0), line, font=font)
        text_width = bbox[2] - bbox[0]
        x = (width - text_width) // 2
        y = y_start + i * 65
        draw.text((x, y), line, fill=accent_color if i == 0 else text_color, font=font)

    # Add branding at bottom
    draw.text((width//2 - 100, height - 100), "datagarden", fill="#666666", font=small_font)

    output_path = f"/tmp/frame_{datetime.now():%Y%m%d_%H%M%S_%f}.png"
    img.save(output_path)
    return output_path


def create_thumbnail(title: str, subtitle: str = "", output_path: str = None) -> str:
    """Create a YouTube thumbnail (1280x720)."""
    width, height = 1280, 720
    img = Image.new('RGB', (width, height), "#1a1a2e")
    draw = ImageDraw.Draw(img)

    try:
        title_font = ImageFont.truetype(FONT_BOLD, 64)
        sub_font = ImageFont.truetype(FONT_REGULAR, 36)
    except:
        title_font = ImageFont.load_default()
        sub_font = title_font

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


def assemble_short(frame_path: str, audio_path: str, output_path: str) -> str:
    """Assemble frame + audio into a Short using FFmpeg."""
    duration = get_audio_duration(audio_path)

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
        '-t', str(duration + 1),  # Add 1s buffer
        '-vf', 'scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2',
        output_path
    ]
    subprocess.run(cmd, capture_output=True)
    return output_path


def score_and_gate(title: str, answer: str, evidence: list = None,
                   min_confidence: float = 0.5) -> dict:
    """Score a content hypothesis with Jev before creating the video.

    Returns:
        {
            'gated': True/False (should we proceed?),
            'scores': Jev answers dict or None,
            'reason': str explanation,
        }
    """
    state = f"Title: {title}\nAnswer: {answer}"
    if evidence:
        state += "\nEvidence: " + "; ".join(evidence[:3])

    try:
        from shared.jev import score_hypothesis
        answers = score_hypothesis(state)
    except ImportError:
        return {'gated': True, 'scores': None, 'reason': 'Jev not installed, skipping gate'}

    if answers is None:
        return {'gated': True, 'scores': None, 'reason': 'Jev unavailable (no API key), proceeding'}

    # Gate: reject if publish_candidate is clearly no, or if answerable_from_data is low
    publish = answers.get('publish_candidate')
    answerable = answers.get('answerable_from_data')
    audience = answers.get('specific_audience')
    economic = answers.get('economic_consequence')

    reasons = []
    should_publish = True

    if publish and hasattr(publish, 'noul') and publish.noul < 0.3:
        should_publish = False
        reasons.append(f"publish_candidate={publish.noul:.2f}")

    if answerable and hasattr(answerable, 'noul') and answerable.noul < 0.3:
        should_publish = False
        reasons.append(f"answerable_from_data={answerable.noul:.2f}")

    if economic and hasattr(economic, 'score') and economic.score < 1.0:
        reasons.append(f"economic_consequence={economic.score:.1f}")

    if audience and hasattr(audience, 'noul') and audience.noul > 0.7:
        reasons.append("targets specific audience")

    reason = "pass" if should_publish else f"gate: {', '.join(reasons)}"

    return {
        'gated': should_publish,
        'scores': answers,
        'reason': reason,
    }


def generate_short(title: str, answer: str, evidence: list = None,
                   subtitle: str = "Data says...", gate: bool = False) -> dict:
    """Full pipeline: data → script → voice → frame → video → thumbnail.

    If gate=True, runs Jev hypothesis scoring first and skips if not publishable.
    """
    CONTENT_DIR.mkdir(parents=True, exist_ok=True)

    # Optional Jev gate
    gate_result = None
    if gate:
        gate_result = score_and_gate(title, answer, evidence)
        if not gate_result['gated']:
            return {
                'video': None,
                'thumbnail': None,
                'audio': None,
                'script': None,
                'title': title,
                'duration': 0,
                'gated': True,
                'gate_reason': gate_result['reason'],
                'gate_scores': gate_result['scores'],
            }

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

    # Script
    script = generate_script(title, answer, evidence or [])

    # Voiceover
    audio_path = str(CONTENT_DIR / f"audio_{timestamp}.mp3")
    generate_voiceover(script, audio_path)

    # Frame
    frame_path = create_text_frame(title)

    # Video
    video_path = str(CONTENT_DIR / f"short_{timestamp}.mp4")
    assemble_short(frame_path, audio_path, video_path)

    # Thumbnail
    thumb_path = str(CONTENT_DIR / f"thumb_{timestamp}.png")
    create_thumbnail(title, subtitle=subtitle, output_path=thumb_path)

    result = {
        'video': video_path,
        'thumbnail': thumb_path,
        'audio': audio_path,
        'script': script,
        'title': title,
        'duration': get_audio_duration(audio_path),
        'gated': False,
    }

    if gate_result:
        result['gate_reason'] = gate_result['reason']
        result['gate_scores'] = gate_result['scores']

    return result


if __name__ == '__main__':
    result = generate_short(
        title="The used synths getting cheaper fastest",
        answer="Roland SP-404MKII median ask is down 11.4% in 30 days",
        evidence=["Inventory up 22%", "Supply outpacing demand"],
    )
    print(f"Video: {result['video']}")
    print(f"Thumbnail: {result['thumbnail']}")
    print(f"Script: {result['script']}")
    print(f"Duration: {result['duration']:.1f}s")
