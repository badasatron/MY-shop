from django.db import models
from users.models import User

class Basket(models.Model):
    user = models.OneToOneField(User, null=True, on_delete=models.CASCADE)

class Category(models.Model):
    name = models.CharField(max_length=100)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True
    )

    def __str__(self):
        if self.parent:
            return f"{self.parent} > {self.name}"
        return self.name

class Product(models.Model):
    title = models.CharField(max_length=30)
    price = models.PositiveIntegerField(default=0)
    image = models.ImageField(upload_to='photos')
    brand = models.CharField(max_length=50, null=True, blank=True)
    article = models.CharField(max_length=100, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)
    similar_products = models.ManyToManyField('self', blank=True)

class In_Basket(models.Model):
    basket = models.ForeignKey(Basket, related_name="basket_of_user", on_delete=models.CASCADE)
    prodcut = models.ForeignKey(Product, related_name='product_of_user', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Отправлен'),
        ('delivered', 'Доставлен'),
    ]

    id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, related_name="order_user", on_delete=models.CASCADE)
    data = models.DateField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')

    def get_total(self):
        return sum(
            item.prodcut.price * item.quantity
            for item in self.order_of_user.all()
        )

    def __str__(self):
        return f"Заказ {self.id} от {self.user}"

class In_Order(models.Model):
    order = models.ForeignKey(Order, related_name="order_of_user", on_delete=models.CASCADE)
    prodcut = models.ForeignKey(Product, related_name='product_of_order', on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
