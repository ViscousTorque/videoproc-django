"""Task for celery video processing"""
import os
import time

from moviepy.video.io.VideoFileClip import VideoFileClip
from opentelemetry import trace
from celery import shared_task

from django.utils import timezone
from django.conf import settings

from apps.videos.models import Video

tracer = trace.get_tracer(__name__)

# Set a safe writable temp directory for MoviePy and FFmpeg
tmp_dir = os.path.join(settings.MEDIA_ROOT, 'tmp')
os.makedirs(tmp_dir, exist_ok=True)
os.environ['TMPDIR'] = tmp_dir

@shared_task(queue='encoding')
def process_video(video_id):
    with tracer.start_as_current_span("task_process_video") as input_span:
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
            file_size = os.path.getsize(input_path)
            input_span.set_attribute("video.task_process_video.file_size", file_size)
            input_span.set_attribute("video.task_process_video.file_path", input_path)

            output_filename = f"processed_{filename}"
            output_path = os.path.join(settings.MEDIA_ROOT, 'processed', output_filename)
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Temp audio file with full filename + extension
            temp_audiofile = os.path.join(tmp_dir, f"{output_filename}_TEMP_MPY_wvf_snd.mp4")

            with tracer.start_as_current_span("resize_and_write") as output_span:
                clip = VideoFileClip(input_path)
                clip_resized = clip.resized(height=720)
                clip_resized.write_videofile(
                    output_path,
                    codec='libx264',
                    audio_codec='aac',
                    temp_audiofile=temp_audiofile,
                    remove_temp=True,
                    logger=None
                )

                # Confirm output file exists
                for _ in range(5):
                    if os.path.exists(output_path):
                        break
                    time.sleep(0.2)
                else:
                    raise FileNotFoundError(f"MoviePy said it succeeded, but output file not found: {output_path}")

                file_size = os.path.getsize(output_path)
                output_span.set_attribute("video.resize_and_write.file_size", file_size)
                output_span.set_attribute("video.resize_and_write.file_path", output_path)

            video.output_file.name = os.path.relpath(output_path, settings.MEDIA_ROOT)
            video.processed = True
            video.processed_at = timezone.now()
            video.status = 'done'
            video.save()

        except Exception as e:
            print(f"[ERROR] Video processing failed: {e}")
            video.status = 'failed'
            video.save()
