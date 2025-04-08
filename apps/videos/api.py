from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser
from rest_framework import status
from apps.videos.models import Video
from apps.videos.serializers import VideoSerializer
from apps.videos.tasks import process_video
from opentelemetry import trace
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


tracer = trace.get_tracer(__name__)

class VideoUploadView(APIView):
    parser_classes = [MultiPartParser]

    @swagger_auto_schema(
        operation_description="Upload a video file for processing.",
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=["title", "file"],
            properties={
                "title": openapi.Schema(type=openapi.TYPE_STRING, description="Video title"),
                "file": openapi.Schema(type=openapi.TYPE_FILE, description="Video file (MP4)"),
            },
        ),
        responses={201: VideoSerializer, 400: "Validation Error"},
    )
    def post(self, request):
        with tracer.start_as_current_span("api_upload_video"):
            serializer = VideoSerializer(data=request.data)
            if serializer.is_valid():
                video = serializer.save()
                process_video.delay(video.id)
                return Response(VideoSerializer(video).data, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class VideoListView(APIView):
    @swagger_auto_schema(
        operation_description="List all uploaded and processed videos.",
        responses={200: VideoSerializer(many=True)}
    )
    def get(self, request):
        with tracer.start_as_current_span("api_list_videos"):
            videos = Video.objects.all().order_by('-created_at')
            serializer = VideoSerializer(videos, many=True)
            return Response(serializer.data)
