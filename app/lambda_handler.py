from mangum import Mangum
from main import app

# Mangum converts API Gateway events into ASGI requests (so FastAPI can handle them)
handler = Mangum(app)
