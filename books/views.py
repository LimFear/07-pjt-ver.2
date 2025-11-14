from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .models import Category, Book, Thread, Comment
from .serializers import CategorySerializer
from .serializers import BookSerializer, ThreadListSerializer
from .serializers import ThreadDetailSerailizer
from .serializers import CommentDetailSerializer

# ---------- Categories ----------

@api_view(['GET'])
def category_list(request):
    categories = Category.objects.all() # 다 조회할 때와 한개만 조회할 때의 시리얼 라이저를 다르게 사용하자
    serializer = CategorySerializer(categories, many=True)
    return Response(serializer.data)

#---------- Books ----------

@api_view(['GET'])
def book_list(request):
    books = Book.objects.all()
    serializer = BookSerializer(books, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def book_detail(request, pk):
    book = Book.objects.get(pk=pk)
    serializer = BookSerializer(book)
    return Response(serializer.data)

# ---------- Threads ----------

@api_view(['GET'])
def thread_list(request):
    threads = Thread.objects.select_related("book").all()
    serializer = ThreadListSerializer(threads, many=True)
    return Response(serializer.data)

@api_view(['GET', 'DELETE', 'PATCH']) # 조회, 삭제, 수정
def thread_detail(request, pk):
    thread = Thread.objects.get(pk=pk)

    if (request.method == 'GET'):
        serializer = ThreadDetailSerailizer(thread)
        return Response(serializer.data)

    elif (request.method == 'PATCH'):
        serializer = ThreadDetailSerailizer(thread, data=request.data, partial=True)
        if (serializer.is_valid(raise_exception=True)):
            serializer.save()
            return Response(serializer.data)

    elif (request.method == 'DELETE'):
        thread.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['POST'])
def create_thread(request, book_pk):
    book = Book.objects.get(pk=book_pk) # 어디에 댓글이 작성될 것인지 확인
    serializer = ThreadDetailSerailizer(data=request.data) # 시리얼라이저에 데이터 넣기
    if (serializer.is_valid(raise_exception=True)):
        serializer.save(book=book) # 저장
        return Response(serializer.data)

# ---------- Comments ----------

@api_view(['POST']) # Comment 생성
def create_comment(request, thread_pk):
    thread = Thread.objects.get(pk=thread_pk)
    serializer = CommentDetailSerializer(data = request.data)
    if (serializer.is_valid(raise_exception=True)):
        serializer.save(thread=thread)
        return Response(serializer.data)

@api_view(['GET', 'DELETE', 'PATCH']) # Comment 조회, 삭제 수정
def comment_detail(request, pk):
    comment = Comment.objects.get(pk=pk)

    if (request.method == 'GET'):
        serializer = CommentDetailSerializer(comment)
        return Response(serializer.data)
    
    elif (request.method == 'PATCH'):
        serializer = CommentDetailSerializer(comment, data=request.data, partial=True)
        if (serializer.is_valid(raise_exception=True)):
            serializer.save()
            return Response(serializer.data)

    elif (request.method == 'DELETE'):
        comment.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)