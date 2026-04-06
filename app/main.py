from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import auth, craftsman, booking, review, message, payment, verification

app = FastAPI(
    title="Handwerker Platform API",
    description="API for connecting homeowners with verified craftsmen in Germany",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_URL, "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router)
app.include_router(craftsman.router)
app.include_router(booking.router)
app.include_router(review.router)
app.include_router(message.router)
app.include_router(payment.router)
app.include_router(verification.router)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Handwerker Platform API",
        "version": "1.0.0",
        "docs": "/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "environment": settings.ENVIRONMENT
    }
