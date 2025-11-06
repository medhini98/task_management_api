from fastapi import FastAPI, HTTPException, Request, status
from datetime import datetime
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

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

#### Error Handling
"""
Decorator - @app.exception_handler(HTTPException): Whenever an HTTPException occurs within this router, call this function instead of using the default error response - overrides the default behavior of FastAPI for that router only.
Function runs whenever an HTTPException is raised.
request: the incoming HTTP request (so you could log details like path or method if needed),
exc: the exception object that was raised (it contains status_code, detail, etc.)
JSONResponse is a FastAPI helper class that lets you send a well-formatted JSON error message.
Here, you are:
    - Returning an HTTP response
    - Setting its status code to the same as the exception (e.g., 404, 400, etc.)
    - Returning a JSON body that looks like this: {"detail": "Task not found"}
"""

@app.exception_handler(HTTPException)
def http_exception_handler(request, exc: HTTPException):
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.detail,
            "path": str(request.url),
            "method": request.method,
            "timestamp": datetime.now().isoformat(),
        },
    )

"""
To intercept and reformat Pydantic validation errors (at the app level) into a consistent JSON structure:
Decorator - @app.exception_handler(RequestValidationError): Tells FastAPI to use this function whenever a validation error happens anywhere in the app
def validation_exc_handler(request, exc): Defines the handler function that receives the request and the exception object
status_code = 422: HTTP status 422 → Unprocessable Content, used for validation errors
'details': exc.errors(): Gives a list of which fields failed validation (e.g. “title must be a string”)
'path': str(request.url): Adds the request URL to make debugging easier
'error': "Validation failed": Adds a cleaner top-level message for readability
"""

@app.exception_handler(RequestValidationError)
def validation_exc_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        content={
            'error': 'Validation failed',
            'details': exc.errors(),
            'path': str(request.url)
        },
    )

from routers import todo   #importing router module (folder: routers/todo.py)
app.include_router(todo.router)  #mount all /todos routes

from routers import lookup
app.include_router(lookup.router)

from routers import attachments
app.include_router(attachments.router)

from core.config import settings
print("CONFIG:", {
    "storage_backend": settings.storage_backend,
    "aws_region": settings.aws_region,
    "aws_s3_bucket": settings.aws_s3_bucket,
    "aws_s3_prefix": settings.aws_s3_prefix,
    "local_storage_dir": settings.local_storage_dir,
})

import os

handler = None
if os.getenv("AWS_EXECUTION_ENV", "").startswith("AWS_Lambda"):
    try:
        from mangum import Mangum
        handler = Mangum(app)
    except Exception:
        # Optional: log/ignore; on ECS we don't need Mangum anyway
        handler = None
        
@app.get("/healthz")
def healthz():
    return {"status": "ok"}