import subprocess
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont


def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout)[-3000:])

def duration_seconds(audio: Path):
    p = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", str(audio)], capture_output=True, text=True)
    return max(1.0, float(p.stdout.strip()))

def add_caption(image_path: Path, caption: str):
    im = Image.open(image_path).convert("RGB").resize((1920, 1080))
    overlay = Image.new("RGBA", im.size, (0,0,0,0))
    draw = ImageDraw.Draw(overlay)
    try:
        font = ImageFont.truetype("DejaVuSans-Bold.ttf", 42)
    except Exception:
        font = ImageFont.load_default()
    words, lines, line = caption.split(), [], ""
    for word in words:
        test = (line + " " + word).strip()
        if draw.textbbox((0,0), test, font=font)[2] > 1650 and line:
            lines.append(line); line = word
        else:
            line = test
        if len(lines) == 2: break
    if line and len(lines) < 2: lines.append(line)
    y = 880 - len(lines) * 55
    for text in lines:
        box = draw.textbbox((0,0), text, font=font, stroke_width=2)
        x = (1920 - (box[2]-box[0])) // 2
        draw.text((x,y), text, font=font, fill=(255,255,255,245), stroke_width=3, stroke_fill=(0,0,0,220))
        y += 58
    Image.alpha_composite(im.convert("RGBA"), overlay).convert("RGB").save(image_path, quality=94)

def render_video(scene_files, audio_files, output: Path, work: Path):
    clips=[]; audios=[]
    for i,(img,aud) in enumerate(zip(scene_files,audio_files)):
        dur=duration_seconds(aud)
        clip=work/f"clip_{i:03d}.mp4"
        # Subtle Ken Burns movement; each scene's own narration determines its duration.
        run(["ffmpeg","-y","-loop","1","-i",str(img),"-t",f"{dur:.3f}","-vf",
             "scale=2200:1238:force_original_aspect_ratio=increase,crop=1920:1080,zoompan=z='min(zoom+0.00035,1.08)':d=1:s=1920x1080:fps=25,format=yuv420p",
             "-r","25","-an","-c:v","libx264","-preset","veryfast","-crf","21",str(clip)])
        clips.append(clip); audios.append(aud)
    concat=work/"clips.txt"
    concat.write_text("\n".join(f"file '{p.as_posix()}'" for p in clips), encoding="utf-8")
    silent=work/"silent.mp4"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(concat),"-c","copy",str(silent)])
    audio_list=work/"audio.txt"
    audio_list.write_text("\n".join(f"file '{p.as_posix()}'" for p in audios),encoding="utf-8")
    narration=work/"narration.mp3"
    run(["ffmpeg","-y","-f","concat","-safe","0","-i",str(audio_list),"-c:a","libmp3lame","-q:a","3",str(narration)])
    output.parent.mkdir(parents=True,exist_ok=True)
    run(["ffmpeg","-y","-i",str(silent),"-i",str(narration),"-map","0:v:0","-map","1:a:0","-c:v","copy","-c:a","aac","-b:a","192k","-shortest","-movflags","+faststart",str(output)])
    return output
