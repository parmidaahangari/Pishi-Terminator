from rest_framework.serializers import ModelSerializer
from rest_framework import serializers

from .models import Comment, Post
class PostSerializer(ModelSerializer):
    owner = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = [
            'title',
            'body',
            'created',
            'owner',
        ]
        read_only_fields = ['created', 'owner']
    def get_owner(self, obj):
        return obj.owner.username


class PostDetailSerializer(ModelSerializer):
    owner = serializers.SerializerMethodField()
    comment_set = serializers.SerializerMethodField()
    class Meta:
        model = Post
        fields = [
            'title',
            'body',
            'created',
            'owner',
            'updated',
            'comment_set',
        ]
        read_only_fields = [
            'created',
            'updated',
            'owner',
            'comment_set',
        ]

    def get_owner(self, obj):
        return obj.owner.username
    
    def get_comment_set(self, obj):
        comments = obj.comment_set.all()
        return [f"http://localhost:8000/api/comments/{i.id}/" for i in comments]


class CommentSerializer(ModelSerializer):
    owner = serializers.SerializerMethodField()
    post = serializers.SerializerMethodField()
    class Meta:
        model = Comment
        fields = [
            'post',
            'owner',
            'body',
            'created',
            'updated',
        ]
        read_only_fields = [
            'post',
            'owner',
            'created',
            'updated',
        ]
        
    def get_post(self, obj):
        return f"http://localhost:8000/api/posts/{obj.post_id}/"
    
    def get_owner(self, obj):
        return obj.owner.username
