CORS_ALLOW_ALL_ORIGINS = True  # For development only
CORS_ALLOWED_ORIGINS = [
    "https://homebid-real-estate.vercel.app"
    "https://homebid-real-estate.vercel.app/properties"
    "http://localhost:5173",
]

# Make sure your media files are being served correctly
MEDIA_URL = '/media/'
MEDIA_ROOT = os.path.join(BASE_DIR, 'media') 