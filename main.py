from fastapi import FastAPI 
 
app = FastAPI() #creating instance of fastapi

@app.get("/") #define route using this decorator - tells FastAPI that func root handles GET requests to root URL ("/")
async def root():
    return {"message":"Hello, FastAPI!"} #returns JSON object
