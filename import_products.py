import pandas as pd
from main.models import Product, Category

def parse_price(price):
    try:
        return float(price)
    except (ValueError, TypeError):
        return None

def get_deepest_category(row):
    # Проверяем наличие категорий по приоритету: category3 > category2 > category
    for level in ['category3', 'category2', 'category']:
        if level in row and pd.notna(row[level]):
            name_or_id = str(row[level]).strip()
            # Пробуем сначала найти по ID
            if name_or_id.isdigit():
                try:
                    return Category.objects.get(id=int(name_or_id))
                except Category.DoesNotExist:
                    continue
            # Затем по имени
            try:
                return Category.objects.get(name=name_or_id)
            except Category.DoesNotExist:
                continue
    return None

def import_products(filepath):
    df = pd.read_excel(filepath)
    success_count = 0
    fail_count = 0

    for i, row in df.iterrows():
        try:
            category = get_deepest_category(row)
            if not category:
                print(f"❌ [{i}] Категория не найдена для '{row.get('title', 'Без названия')}' (ID: {row.get('category')})")
                fail_count += 1
                continue

            price = parse_price(row['price'])
            if price is None:
                print(f"❌ [{i}] Невалидная цена: '{row['price']}' для '{row['title']}'")
                fail_count += 1
                continue

            Product.objects.create(
                title=row['title'],
                price=price,
                image=row['image'],
                article=row['article'],
                brand=row['brand'],
                description=row['description'],
                category=category
            )
            success_count += 1
        except Exception as e:
            print(f"💥 [{i}] Ошибка при импорте '{row.get('title', '???')}': {e}")
            fail_count += 1

    print(f"\n✅ Успешно импортировано: {success_count}")
    print(f"❌ Не удалось импортировать: {fail_count}")
