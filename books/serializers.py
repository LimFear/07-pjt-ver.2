from rest_framework import serializers
from .models import Category, Book, Thread, Comment

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = '__all__'