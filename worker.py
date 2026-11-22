import asyncio, re
from pathlib import Path
from .config import OUTPUT_DIR
from .state import update_job, log_job
from .story import split_script, visual_prompt
from .gemini_browser import browser
from .narration import make_voice
from .render import add_caption, render_video

async def produce(job_id: str, payload):
    project = OUTPUT_DIR / job_id
    images_dir, audio_dir, work_dir = project/"images", project/"audio", project/"work"
    for d in (images_dir,audio_dir,work_dir): d.mkdir(parents=True,exist_ok=True)
    try:
        update_job(job_id,status="running",stage="Planning scenes",progress=2,message="Breaking your script into scenes")
        scenes = split_script(payload.script, payload.scenes)
        if not scenes:
            raise RuntimeError("Could not split the supplied script into scenes.")
        update_job(job_id,total_scenes=len(scenes))
        log_job(job_id,f"Script divided into {len(scenes)} scenes")
        scene_images=[]; scene_audio=[]
        total_words = max(1, len(payload.script.split()))
        target_wpm = total_words / max(1, payload.duration_minutes)
        # Approximate the selected target runtime by adjusting neural TTS speaking rate.
        # Edge voices differ, so this is a guide rather than an exact duration guarantee.
        rate_pct = max(-15, min(20, round((target_wpm / 150 - 1) * 100)))
        tts_rate = f"{rate_pct:+d}%"
        log_job(job_id, f"Narration pace set to {tts_rate} to target approximately {payload.duration_minutes} minutes")
        for i, scene in enumerate(scenes, start=1):
            pct = 5 + int((i-1)/len(scenes)*55)
            update_job(job_id,stage="Generating images",progress=pct,completed_scenes=i-1,message=f"Generating image {i} of {len(scenes)}")
            prompt = visual_prompt(scene,payload.visual_style,i,len(scenes))
            image_path = images_dir/f"scene_{i:03d}.png"
            await browser.generate_image(prompt,image_path)
            # Short, legible on-screen scene label derived from the narration.
            caption = " ".join(re.findall(r"[\wÀ-ÿ'-]+",scene)[:8])
            add_caption(image_path,caption)
            scene_images.append(image_path)
            audio_path = audio_dir/f"scene_{i:03d}.mp3"
            await make_voice(scene,audio_path,payload.voice,tts_rate)
            scene_audio.append(audio_path)
            update_job(job_id,completed_scenes=i,progress=5+int(i/len(scenes)*55),message=f"Created image and narration for scene {i}/{len(scenes)}")
            log_job(job_id,f"Scene {i}/{len(scenes)} image and narration complete")
        update_job(job_id,stage="Rendering video",progress=65,message="Animating scenes and assembling narration")
        log_job(job_id,"Rendering 1080p scenes with subtle camera movement")
        output = project/"AsanEditing_final.mp4"
        await asyncio.to_thread(render_video,scene_images,scene_audio,output,work_dir)
        update_job(job_id,status="completed",stage="Complete",progress=100,message="Your documentary is ready",video_url=f"/download/{job_id}")
        log_job(job_id,"MP4 export completed")
    except Exception as exc:
        update_job(job_id,status="failed",stage="Needs attention",message=str(exc),error=str(exc))
        log_job(job_id,f"ERROR: {exc}")
