from django.urls import path
from apps.videos import views
from .api import VideoUploadView, VideoListView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('', views.upload_video, name='upload_video_form'),
    path('videos/', views.video_list, name='video_list'),

    # API Endpoints
    path('api/upload/', VideoUploadView.as_view(), name='api-upload-video'),
    path('api/videos/', VideoListView.as_view(), name='api-video-list'),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
