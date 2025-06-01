from .models import Category


def categories_processor(request):
    return {
        'categories': Category.objects.prefetch_related('children__children').all()
    }
