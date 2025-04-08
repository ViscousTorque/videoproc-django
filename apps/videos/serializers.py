from rest_framework import serializers
from apps.videos.models import Video
from opentelemetry import trace

tracer = trace.get_tracer(__name__)

class VideoSerializer(serializers.ModelSerializer):
    class Meta:
        model = Video
        fields = '__all__'
        read_only_fields = ('processed', 'output_file', 'created_at', 'processed_at')

    def create(self, validated_data):
        with tracer.start_as_current_span("serializer_create_video"):
            return super().create(validated_data)
