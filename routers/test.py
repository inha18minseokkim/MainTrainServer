from fastapi import APIRouter

router = APIRouter()

@router.post("/")
async def root():
    return {"message": "Hello World"}

@router.post("/hello/{name}")
async def say_hello(name: str):
    return {"message": f"Hello {name}"}