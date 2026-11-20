from fastapi import FastAPI

app = FastAPI(title="Job Application & Queue Tracker API")

@app.get("/health")
def health_check():
    return {"status": "ok", "day": 1}