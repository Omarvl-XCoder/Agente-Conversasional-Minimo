from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversacionViewSet, MensajeViewSet

# El router crea automáticamente las URLs para los ViewSets
router = DefaultRouter()
router.register(r'conversaciones', ConversacionViewSet)
router.register(r'mensajes', MensajeViewSet)

urlpatterns = [
    path('', include(router.urls)),
]