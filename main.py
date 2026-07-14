from fastapi import FastAPI, File, UploadFile, Form
from fastapi.responses import StreamingResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from cv_reader import extract_text
from matcher import stream_match

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
async def home():
    return FileResponse("index.html")


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.post("/match")
async def match_endpoint(
    file: UploadFile = File(...),
    region: str = Form("any"),
    duration: str = Form("any")
):
    try:
        if not file.filename:
            return JSONResponse(
                status_code=400,
                content={"error": "No file uploaded."}
            )

        if not file.filename.lower().endswith(".pdf"):
            return JSONResponse(
                status_code=400,
                content={"error": "Only PDF files are allowed."}
            )

        pdf_bytes = await file.read()
        cv_text = extract_text(pdf_bytes)

        if not cv_text.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Could not extract text from the PDF."}
            )

        return StreamingResponse(
            stream_match(cv_text, region, duration),
            media_type="text/event-stream"
        )

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": f"Internal server error: {str(e)}"}
        )