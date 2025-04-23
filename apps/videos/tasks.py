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
            filename = os.path.basename(input_path)
            output_filename = f"processed_{filename}"
            output_path = os.path.join(settings.MEDIA_ROOT, 'processed', output_filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            with tracer.start_as_current_span("resize_and_write") as span:
                clip = VideoFileClip(input_path)
                clip_resized = clip.resized(height=720)
                clip_resized.write_videofile(output_path, codec='libx264', audio_codec='aac')

                file_size = os.path.getsize(output_path)
                span.set_attribute("video.resize_and_write.file_size", file_size)
                span.set_attribute("video.resize_and_write.file_path", output_path)

            video.output_file.name = os.path.relpath(output_path, settings.MEDIA_ROOT)
            video.processed = True
            video.processed_at = timezone.now()
            video.status = 'done'
            video.save()

        except Exception as e:
            print(f"[ERROR] Video processing failed: {e}")
            video.status = 'failed'
            video.save()


        except Exception as e:
            print(f"[ERROR] Failed to process video {video_id}: {e}")
            video.status = 'failed'
            video.save()

