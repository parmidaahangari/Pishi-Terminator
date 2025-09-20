from rest_framework import serializers

from .models import Project, Category

class ProjectSerializer(serializers.ModelSerializer):
    members = serializers.SerializerMethodField()
    class Meta:
        model = Project
        fields = [
            'title', 'description',
            'category', 'members',
            'created_at', 'updated_at',
        ]

    def get_members(self, obj):
        return [i.person.id for i in obj.members.all()]
