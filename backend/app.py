from fastapi import FastAPI

app = FastAPI()


def authenicate ():
    pass

@app.get("/borrow")
async def root():
   return {"message": "Hello World"}

@app.get("/lend")
async def lend():
   return {"message": "Hello World"}



