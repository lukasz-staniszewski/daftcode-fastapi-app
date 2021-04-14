from fastapi import FastAPI

from pydantic import BaseModel

app = FastAPI()
app.counter = 0


class HelloResp(BaseModel):
    msg: str


@app.get("/hello/{name}", response_model=HelloResp)
async def hello_name_view(name: str):
    return HelloResp(msg=f"Hello {name}")


@app.get("/")
def root():
    return {"message": "Hello World"}


@app.get('/counter')
def counter():
    app.counter += 1
    return app.counter
