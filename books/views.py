from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.core.cache import cache
from .models import Book
from .serializers import BookSerializer

@api_view(['GET', 'POST'])
def book_list(request):
    if request.method == 'GET':
        # Try to get from cache
        cached_books = cache.get("book_list")
        print(cached_books)
        if cached_books:
            return Response(cached_books)
        books = Book.objects.all()
        serializer = BookSerializer(books, many=True)
        cache.set("book_list", serializer.data, timeout=60)  # Cache for 60 seconds
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = BookSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            cache.delete("book_list")
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
