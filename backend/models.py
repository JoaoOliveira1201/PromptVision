from pydantic import BaseModel, HttpUrl

class PresentationRequest(BaseModel):
    duration: int
    detail_level: str
    character: str

class PresentationResponse(BaseModel):
    video_url: HttpUrl
