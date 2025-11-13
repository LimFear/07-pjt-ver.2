import json
from datetime import date
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404, render
from django.views.decorators.http import require_GET, require_http_methods
from django.views.decorators.csrf import csrf_exempt

from .models import Category, Book, Thread, Comment

# Create your views here.
# ---------- 직렬화 유틸 ----------
def d(dt):   # 날짜/시간 ISO 문자열로
    return dt.isoformat() if hasattr(dt, "isoformat") else dt

def category_dict(c: Category):
    return {"id": c.id, "name": c.name}

def book_list_dict(b: Book):
    return {"id": b.id, "title": b.title, "author": b.author, "isbn": b.isbn, "cover": b.cover}

def thread_short_dict(t: Thread):
    return {"id": t.id, "title": t.title, "content": t.content, "reading_date": d(t.reading_date)}

def book_detail_dict(b: Book):
    return {
        "id": b.id,
        "title": b.title,
        "description": b.description,
        "isbn": b.isbn,
        "cover": b.cover,
        "publisher": b.publisher,
        "pub_date": d(b.pub_date),
        "author": b.author,
        "customer_review_rank": b.customer_review_rank,
        "category": category_dict(b.category),
        "threads": [thread_short_dict(t) for t in b.threads.all()],
        "thread_count": b.threads.count(),
    }

def comment_dict(c: Comment):
    return {
        "id": c.id,
        "content": c.content,
        "created_at": d(c.created_at),
        "updated_at": d(c.updated_at),
    }

def comment_detail_dict(c: Comment):
    out = comment_dict(c)
    out["thread_title"] = c.thread.title
    return out

def thread_detail_dict(t: Thread):
    return {
        "id": t.id,
        "title": t.title,
        "content": t.content,
        "reading_date": d(t.reading_date),
        "created_at": d(t.created_at),
        "updated_at": d(t.updated_at),
        "book": book_list_dict(t.book),
        "comments": [comment_dict(c) for c in t.comments.all()],
        "comment_count": t.comments.count(),
    }

# ---------- Categories ----------
@require_GET
def category_list(request):
    data = [category_dict(c) for c in Category.objects.all()]
    return JsonResponse(data, safe=False)

# ---------- Books ----------
@require_GET
def book_list(request):
    data = [book_list_dict(b) for b in Book.objects.all()]
    return JsonResponse(data, safe=False)

@require_GET
def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return JsonResponse(book_detail_dict(book), safe=False)

# ---------- Threads ----------
@require_GET
def thread_list(request):
    qs = Thread.objects.select_related("book").all()
    data = [{"id": t.id, "title": t.title, "book_title": t.book.title} for t in qs]
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def thread_detail(request, pk):
    thread = get_object_or_404(Thread, pk=pk)

    if request.method == "GET":
        return JsonResponse(thread_detail_dict(thread), safe=False)

    if request.method == "PUT":
        try:
            payload = json.loads(request.body.decode())
        except Exception:
            return JsonResponse({"detail": "invalid json"}, status=400)
        title = payload.get("title", thread.title)
        content = payload.get("content", thread.content)
        rd = payload.get("reading_date", d(thread.reading_date))
        thread.title = title
        thread.content = content
        thread.reading_date = date.fromisoformat(rd)
        thread.save()
        return JsonResponse(thread_detail_dict(thread), safe=False)

    # DELETE
    thread.delete()
    return HttpResponse(status=204)

@csrf_exempt
@require_http_methods(["POST"])
def create_thread(request, book_pk):
    book = get_object_or_404(Book, pk=book_pk)
    try:
        payload = json.loads(request.body.decode())
        title = payload["title"]
        content = payload["content"]
        rd = date.fromisoformat(payload["reading_date"])
    except Exception:
        return JsonResponse({"detail": "invalid json"}, status=400)
    obj = Thread.objects.create(book=book, title=title, content=content, reading_date=rd)
    return JsonResponse(thread_detail_dict(obj), status=201, safe=False)

# ---------- Comments ----------
@csrf_exempt
@require_http_methods(["POST"])
def create_comment(request, thread_pk):
    thread = get_object_or_404(Thread, pk=thread_pk)
    try:
        payload = json.loads(request.body.decode())
        content = payload["content"]
    except Exception:
        return JsonResponse({"detail": "invalid json"}, status=400)
    obj = Comment.objects.create(thread=thread, content=content)
    return JsonResponse(comment_detail_dict(obj), status=201, safe=False)

@csrf_exempt
@require_http_methods(["GET", "PUT", "DELETE"])
def comment_detail(request, pk):
    comment = get_object_or_404(Comment, pk=pk)

    if request.method == "GET":
        return JsonResponse(comment_detail_dict(comment), safe=False)

    if request.method == "PUT":
        try:
            payload = json.loads(request.body.decode())
            comment.content = payload["content"]
        except Exception:
            return JsonResponse({"detail": "invalid json"}, status=400)
        comment.save()
        return JsonResponse(comment_detail_dict(comment), safe=False)

    # DELETE
    comment.delete()
    return HttpResponse(status=204)
