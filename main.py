from fastapi import FastAPI 
from datetime import datetime

app = FastAPI() #creating instance of fastapi

@app.get("/") #define route using this decorator - tells FastAPI that func root handles GET requests to root URL ("/")
async def root():
    return {"message":"Welcome to the Todo App!"} #returns JSON object

@app.get("/current-time")
async def get_current_time():
    current_time = datetime.now()
    return {
        "current_date": current_time.strftime("%Y-%m-%d"),
        "current_time": current_time.strftime("%H:%M:%S"),  
        "timezone": current_time.astimezone().tzname()  
    }