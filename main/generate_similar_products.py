from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from main.models import Product
from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = 'Генерирует список похожих товаров'

    def handle(self, *args, **kwargs):
        products = Product.objects.exclude(description__isnull=True).exclude(description__exact='')
        titles = [p.title for p in products]
        vectorizer = TfidfVectorizer(stop_words='english')
        tfidf_matrix = vectorizer.fit_transform(titles)
        similarity_matrix = cosine_similarity(tfidf_matrix)

        for idx, product in enumerate(products):
            similar_indices = similarity_matrix[idx].argsort()[::-1][1:6]  # top-5 похожих
            similar_products = [products[i] for i in similar_indices]
            product.similar_products.set(similar_products)
            product.save()

        self.stdout.write(self.style.SUCCESS('Похожие товары успешно сохранены'))
