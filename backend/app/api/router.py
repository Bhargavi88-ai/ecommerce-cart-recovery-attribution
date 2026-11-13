from fastapi import APIRouter
from app.api.customers import router as customers_router
from app.api.consents import router as consents_router
from app.api.carts import router as carts_router
from app.api.campaigns import router as campaigns_router
from app.api.send_attempts import router as send_attempts_router
from app.api.orders import router as orders_router
from app.api.attributions import router as attributions_router
from app.api.analytics import router as analytics_router
from app.api.anomalies import router as anomalies_router
from app.api.validation import router as validation_router
from app.api.generator import router as generator_router
from app.api.exports import router as exports_router

api_router = APIRouter(prefix="/api")

api_router.include_router(customers_router)
api_router.include_router(consents_router)
api_router.include_router(carts_router)
api_router.include_router(campaigns_router)
api_router.include_router(send_attempts_router)
api_router.include_router(orders_router)
api_router.include_router(attributions_router)
api_router.include_router(analytics_router)
api_router.include_router(anomalies_router)
api_router.include_router(validation_router)
api_router.include_router(generator_router)
api_router.include_router(exports_router)
