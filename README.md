# videoproc-django

A simple idea to play around with video processing

# References
* https://trac.ffmpeg.org/  
    * https://www.johnvansickle.com/ffmpeg/

* https://zulko.github.io/moviepy/reference/reference/moviepy.video.VideoClip.VideoClip.html#moviepy.video.VideoClip.VideoClip.resized

# TODOs
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
* make project
* make proj_down

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


