from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

# 创建 router
router = DefaultRouter()
router.register(r'meetings', views.MeetingViewSet)
router.register(r'voiceprints', views.VoiceprintViewSet)

urlpatterns = [
    path("recognize/", views.recognize, name="recognize"),
    path("summarize/", views.summarize_content, name="summarize_content"),
    path("", include(router.urls)),  # 自动生成 ViewSet 的 RESTful 路由
]
