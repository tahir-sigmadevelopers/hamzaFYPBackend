from backend.wsgi import application
from whitenoise import WhiteNoise

app = WhiteNoise(application)
