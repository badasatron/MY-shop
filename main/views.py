from django.shortcuts import render, redirect, get_object_or_404
from .models import Product, Basket, In_Basket, Order, In_Order, Category
from django.contrib.auth.decorators import login_required
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from django.db.models import Q
from django.core.paginator import Paginator


def main_view(request):
    product_list = Product.objects.all()
    paginator = Paginator(product_list, 9)  # 9 товаров на страницу
    page_number = request.GET   .get('page')
    page_obj = paginator.get_page(page_number)

    return render(request, 'main.html', {'page_obj': page_obj})


def main(request):
    products = Product.objects.all()
    if request.user.is_authenticated:
        try:
            basket = Basket.objects.get(user=request.user)
        except:
            basketcr = Basket()
            basketcr.user = request.user
            basketcr.save()

    return render(request, "home.html", {'products': products})


def main(request):
    product_list = Product.objects.all()
    paginator = Paginator(product_list, 9)  # 9 товаров на страницу
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    if request.user.is_authenticated:
        Basket.objects.get_or_create(user=request.user)

    return render(request, "home.html", {'page_obj': page_obj})


@login_required
def add(request, product_id):
    product = Product.objects.get(id=product_id)
    basket = Basket.objects.get(user=request.user)
    try:
        basket_in_q = In_Basket.objects.get(product=product)
        basket_in_q.quantity += 1
        basket_in_q.save()
    except:
        add_to_basket = In_Basket()
        add_to_basket.basket = basket
        add_to_basket.prodcut = product
        add_to_basket.save()
    return redirect("cart")


@login_required
def cart(request):
    basket = Basket.objects.get(user=request.user)
    items = In_Basket.objects.filter(basket=basket)

    total_price = sum(item.prodcut.price * item.quantity for item in items)

    return render(request, 'cart.html', {
        'items': items,
        'basket': basket,
        'total_price': total_price,
    })


@login_required
def increase(request, cart_id, product_id):
    basket = Basket.objects.get(id=cart_id)
    in_bask = In_Basket.objects.filter(basket=basket)
    prod = Product.objects.get(id=product_id)
    product = in_bask.get(prodcut=prod)
    product.quantity += 1
    product.save()
    return redirect('cart')


@login_required
def decrease(request, cart_id, product_id):
    basket = Basket.objects.get(id=cart_id)
    in_bask = In_Basket.objects.filter(basket=basket)
    prod = Product.objects.get(id=product_id)
    product = in_bask.get(prodcut=prod)
    product.quantity -= 1
    product.save()
    return redirect('cart')


@login_required
def checkout(request):
    order = Order()
    order.user = request.user
    order.save()
    order_last = Order.objects.filter(user=request.user).order_by('-id').first()
    return redirect('checkoutcont', order_id=order_last.id)


def check_continue(request, order_id):
    basket = Basket.objects.get(user=request.user)
    basket_items = In_Basket.objects.filter(basket=basket)
    for basket_item in basket_items:
        order_item = In_Order()
        order_item.order = Order.objects.get(id=order_id)
        order_item.prodcut = basket_item.prodcut
        order_item.quantity = basket_item.quantity
        order_item.save()
        basket_item.delete()
    order = Order.objects.get(id=order_id)
    order_items = In_Order.objects.filter(order=order)
    return render(request, "checkout.html", {"order_items": order_items})


def orders_list(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, "order_list.html",  {"orders": orders})


def order_detail(request, order_id):
    order = Order.objects.get(id=order_id)
    order_object = In_Order.objects.filter(order=order)
    return render(request, "order_detail.html", {
        'order_objects': order_object,
        'order': order
    })



def get_category_descendants(category):
    """
    Возвращает список ID всех вложенных категорий (включая саму категорию)
    """
    descendants = [category.id]
    for child in category.children.all():
        descendants += get_category_descendants(child)
    return descendants

def products_by_category(request, category_id):
    category = get_object_or_404(Category, id=category_id)
    descendant_ids = get_category_descendants(category)
    products = Product.objects.filter(category_id__in=descendant_ids)

    return render(request, 'products_by_category.html', {
        'products': products,
        'category': category,  # <--- ВАЖНО: передать category
    })


def product_detail(request, product_id):
    product = get_object_or_404(Product, id=product_id)

    # Получаем все другие товары из других категорий
    other_products = Product.objects.exclude(id=product.id).exclude(category=product.category)

    # Подготавливаем данные
    titles = [p.title for p in other_products]
    descriptions = [p.description or '' for p in other_products]
    combined = [f"{t} {d}" for t, d in zip(titles, descriptions)]

    # Добавляем текущий товар для сравнения
    current_text = f"{product.title} {product.description or ''}"
    all_texts = combined + [current_text]

    # TF-IDF векторизация
    vectorizer = TfidfVectorizer()
    tfidf_matrix = vectorizer.fit_transform(all_texts)

    # Сравниваем текущий товар с остальными
    similarity = cosine_similarity(tfidf_matrix[-1], tfidf_matrix[:-1]).flatten()

    # Сортировка по похожести
    top_indices = similarity.argsort()[::-1][:4]  # top 4 похожих

    # Получаем объекты
    recommended = [other_products[int(i)] for i in top_indices if similarity[i] > 0]

    return render(request, 'product_detail.html', {
        'product': product,
        'recommended_products': recommended
    })



def search(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        results = Product.objects.filter(
            Q(title__icontains=query) |
            Q(article__icontains=query) |
            Q(brand__icontains=query) |
            Q(description__icontains=query) |
            Q(category__name__icontains=query) |
            Q(category__parent__name__icontains=query) |
            Q(category__parent__parent__name__icontains=query)
        ).distinct()

    return render(request, 'search_results.html', {
        'query': query,
        'results': results,
    })

def all_categories(request):
    categories = Category.objects.all()
    return render(request, 'all_categories.html', {'categories': categories})
