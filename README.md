# videoproc-django

A simple idea to play around with video processing

# References
* https://trac.ffmpeg.org/  
    * https://www.johnvansickle.com/ffmpeg/

* https://zulko.github.io/moviepy/reference/reference/moviepy.video.VideoClip.VideoClip.html#moviepy.video.VideoClip.VideoClip.resized

# TODOs
* Add admin views to capture state of background tasks
* Missing retry - the @shared_task def retry_failed_videos()
* Write unittests and component tests
* Refactor
* ci test docker compose
    * need to be mindful of the weird temp file creation in moviePy / FFMPEG
* github workflow

# Tech
* python django
* celery
* otel
* postgres
* jaegar

# Docker Compose 
* make project-up
* make project-down

# Upload a video
http://localhost:5000

# Otel Spans View
http://localhost:16686

# Local Setup

* Ubuntu 24.04
* vs code
* Python
    * python3 -m venv venv
    * source venv/bin/activate
    * pip install --upgrade pip
    * pip install -r requirements.txt
* create .env file and add DJANGO_SECRET_KEY
* make startLocalEnv
* TBD

# create a new 5  min video with no audio
```
ffmpeg -f lavfi -i smptebars=size=1280x720:rate=30   -vf "drawtext=fontfile=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf: \
        text='%{pts\\:hms}': fontcolor=white: fontsize=100: \
        x=(w-text_w)/2: y=(h-text_h)/2"   -t 300 -r 30 -c:v libx264 -pix_fmt yuv420p count_up_5min_clock.mp4
```

# Warning FFMPEG encoding fails silently
I havent figured out why it fails silently and states permission denied when attempting to write the temp file.

Use files with no audio for now.