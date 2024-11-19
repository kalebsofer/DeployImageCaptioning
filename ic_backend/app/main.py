from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from .caption_engine import CaptionEngine

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

caption_engine = None


class Image(BaseModel):
    image: bytes


@app.on_event("startup")
async def startup_event():
    global caption_engine
    caption_engine = CaptionEngine()


@app.get("/health")
async def health_check():
    return {"status": "healthy"}


@app.post("/generate-caption")
async def generate_caption(image: Image) -> dict:
    if not caption_engine:
        raise HTTPException(status_code=503, detail="Caption engine not initialized")

    try:
        caption = caption_engine.generate_caption(image.image)
        return {
            "caption": caption,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/test")
async def test_endpoint():
    return {
        "message": "Backend is reachable",
        "environment": {"host": "0.0.0.0", "port": 8051},
    }
