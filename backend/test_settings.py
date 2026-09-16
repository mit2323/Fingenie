from app.core.config import settings

print("SECRET_KEY:", settings.SECRET_KEY)
print("ALGORITHM:", settings.ALGORITHM)
print("EXPIRE:", settings.ACCESS_TOKEN_EXPIRE_MINUTES)

print(
    "GEMINI_API_KEY:",
    settings.GEMINI_API_KEY
)