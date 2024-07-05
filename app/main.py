from typing import Union
from exam import FastAPI
app = FastAPI()
@app.get("/")
def read_root():
    return {"Hello": "exam Jenkins"}
