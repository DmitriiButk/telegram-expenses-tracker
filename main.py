from fastapi import FastAPI
from app.routers import expenses, users, categories


app = FastAPI()

app.include_router(expenses.router)
app.include_router(users.router)
app.include_router(categories.router)


@app.get('/')
def check_api_work():
    return {'message': 'API for telegram bot is working'}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=7777)
