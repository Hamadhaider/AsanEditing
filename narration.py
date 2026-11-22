import asyncio
from pathlib import Path
import edge_tts

async def make_voice(text: str, destination: Path, voice: str, rate: str = "-4%"):
    """Generate an expressive narration segment with gentle pacing variation.

    Edge TTS supports voice, rate, pitch and volume. We use punctuation and
    paragraph boundaries to preserve dramatic pauses; no unsupported emotion
    controls are claimed.
    """
    destination.parent.mkdir(parents=True, exist_ok=True)
    communicate = edge_tts.Communicate(
        text=text, voice=voice, rate=rate, pitch="-2Hz", volume="+0%"
    )
    await communicate.save(str(destination))
    return destination

def make_voice_sync(text: str, destination: Path, voice: str, rate: str = "-4%"): 
    return asyncio.run(make_voice(text, destination, voice, rate))
