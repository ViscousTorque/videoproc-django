from django.shortcuts import render, redirect
from django.db import transaction
from apps.videos.forms import VideoUploadForm
from apps.videos.models import Video
from apps.videos.tasks import process_video
from opentelemetry import trace
import os

tracer = trace.get_tracer(__name__)

def upload_video(request):
    with tracer.start_as_current_span("upload_video_view") as span:
        span.set_attribute("http.method", "POST" if request.method == 'POST' else "GET")
        span.set_attribute("http.route", "/upload_video/")
        span.set_attribute("user.agent", request.META.get('HTTP_USER_AGENT', 'Unknown'))
        if request.method == 'POST':
            form = VideoUploadForm(request.POST, request.FILES)
            if form.is_valid():
                video = form.save()
                file_path = video.file.path
                file_size = os.path.getsize(file_path)
                span.set_attribute("video.uploaded.file_size", file_size)
                span.set_attribute("video.uploaded.file_path", file_path)
                print(f"[UPLOAD DEBUG] Video saved at: {file_path} ({file_size} bytes)")
                transaction.on_commit(lambda: process_video.apply_async(args=[video.id], queue='encoding'))
            else:
                span.set_attribute("form.valid", False)

        else:
            form = VideoUploadForm()
            span.set_attribute("form.valid", None)
        return render(request, 'upload.html', {'form': form})

def video_list(request):
    with tracer.start_as_current_span("video_list_view"):
        videos = Video.objects.all().order_by('-created_at')
        return render(request, 'video_list.html', {'videos': videos})
