from pydantic import BaseModel, Field

class CreateJob(BaseModel):
    script: str = Field(min_length=80, max_length=100000)
    duration_minutes: int = Field(default=5, ge=1, le=60)
    language: str = "French"
    voice: str = "fr-FR-VivienneMultilingualNeural"
    visual_style: str = "cinematic historical documentary, photorealistic, dramatic natural lighting, historically grounded, 16:9, no text, no watermark"
    scenes: int = Field(default=12, ge=3, le=60)
