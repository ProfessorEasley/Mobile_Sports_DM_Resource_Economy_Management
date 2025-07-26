from fastapi import FastAPI
from controllers.economy_controller import router as economy_router

app = FastAPI()
app.include_router(economy_router)
