from moviepy import *
from django.utils import timezone
from opentelemetry import trace
from celery import shared_task
from apps.videos.models import Video
from django.conf import settings
import os

# Initialize the tracer
tracer = trace.get_tracer(__name__)

tmp_dir = os.getenv('TMPDIR', settings.MEDIA_ROOT + '/tmp')

@shared_task(queue='encoding')
def process_video(video_id):
    with tracer.start_as_current_span("task_process_video"):
        try:
            video = Video.objects.get(id=video_id)
            input_path = os.path.join(settings.MEDIA_ROOT, video.file.name)
            if not os.path.exists(input_path):
                print(f"[ERROR] File does not exist: {input_path}")
                return
            if os.path.getsize(input_path) < 1000:
                print(f"[WARNING] File too small to process: {input_path}")
                return
            output_path = os.path.join(settings.MEDIA_ROOT, 'processed', os.path.basename(input_path))
            with tracer.start_as_current_span("resize_and_write") as span:
                output_path = video.file.path
                file_size = os.path.getsize(output_path)
                span.set_attribute("video.resize_and_write.file_size", file_size)
                span.set_attribute("video.resize_and_write.file_path", output_path)
                clip = VideoFileClip(input_path)
                clip_resized = clip.resized(height=720)  # Resize with bilinear interpolation
                clip_resized.write_videofile(output_path, codec='libx264', audio_codec='aac', temp_audiofile_path=tmp_dir)

            video.output_file.name = output_path.split(settings.MEDIA_ROOT)[-1]  # Save the relative path
            video.processed = True
            video.processed_at = timezone.now()
            video.save()

        except Exception as e:
            print(f"[ERROR] Failed to process video {video_id}: {e}")
