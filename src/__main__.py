import os

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "src:app", port=int(os.environ["PORT"]), reload=os.environ["ENV"] == "dev"
    )
