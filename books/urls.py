from django.urls import path
from . import views

urlpatterns = [
    # categories
    path('categories/', views.category_list, name='category_list'),

    # books
    path('books/', views.book_list, name='book_list'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),

    # threads
    path('threads/', views.thread_list, name='thread_list'),
    path('threads/<int:pk>/', views.thread_detail, name='thread_detail'),
    path('books/<int:book_pk>/threads/', views.create_thread, name='create_thread'),

    # comments
    path('threads/<int:thread_pk>/comments/', views.create_comment, name='create_comment'),
    path('comments/<int:pk>/', views.comment_detail, name='comment_detail'),
]
