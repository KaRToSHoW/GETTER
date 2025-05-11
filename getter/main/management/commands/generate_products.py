from django.core.management.base import BaseCommand
from django.utils import timezone
from main.models import Product, Category
import random
import lorem
import json
import os
from django.conf import settings


class Command(BaseCommand):
    help = 'Генерирует 10 тестовых товаров, распределенных по категориям'

    def handle(self, *args, **options):
        # Создаем или получаем категории
        category_names = [
            "Смартфоны", 
            "Ноутбуки", 
            "Аудиотехника", 
            "Фототехника",
            "Аксессуары"
        ]
        
        self.stdout.write(self.style.SUCCESS('Создание категорий...'))
        category_map = {}
        for name in category_names:
            category, created = Category.objects.get_or_create(name=name)
            category_map[name] = category
            if created:
                self.stdout.write(self.style.SUCCESS(f'Создана категория: {name}'))
            else:
                self.stdout.write(self.style.WARNING(f'Категория уже существует: {name}'))

        # Создаем 10 товаров
        self.stdout.write(self.style.SUCCESS('Создание товаров...'))
        
        # Данные для генерации товаров по категориям
        product_data = [
            # Смартфоны
            {
                "category": "Смартфоны",
                "products": [
                    {
                        "name": "iPhone 15 Pro",
                        "sku": "IP15PRO-128",
                        "price": 89990,
                        "stock": random.randint(5, 50),
                        "specifications": {
                            "Процессор": "A17 Pro",
                            "Память": "128 ГБ",
                            "Экран": "6.1 дюймов",
                            "Камера": "48 Мп",
                            "Цвет": "Титановый чёрный"
                        }
                    },
                    {
                        "name": "Samsung Galaxy S24 Ultra",
                        "sku": "SGS24U-256",
                        "price": 109990,
                        "stock": random.randint(5, 30),
                        "specifications": {
                            "Процессор": "Snapdragon 8 Gen 3",
                            "Память": "256 ГБ",
                            "Экран": "6.8 дюймов",
                            "Камера": "200 Мп",
                            "Цвет": "Титановый серый"
                        }
                    }
                ]
            },
            # Ноутбуки
            {
                "category": "Ноутбуки",
                "products": [
                    {
                        "name": "MacBook Pro 16",
                        "sku": "MBP16-M3-1TB",
                        "price": 249990,
                        "stock": random.randint(3, 15),
                        "specifications": {
                            "Процессор": "Apple M3 Max",
                            "Память": "32 ГБ",
                            "Хранилище": "1 ТБ SSD",
                            "Экран": "16 дюймов Liquid Retina XDR",
                            "Цвет": "Космический серый"
                        }
                    },
                    {
                        "name": "ASUS ROG Zephyrus G16",
                        "sku": "ROG-G16-RTX4080",
                        "price": 189990,
                        "stock": random.randint(2, 12),
                        "specifications": {
                            "Процессор": "Intel Core i9-14900H",
                            "Память": "32 ГБ",
                            "Хранилище": "2 ТБ SSD",
                            "Видеокарта": "NVIDIA GeForce RTX 4080",
                            "Экран": "16 дюймов 240 Гц"
                        }
                    }
                ]
            },
            # Аудиотехника
            {
                "category": "Аудиотехника",
                "products": [
                    {
                        "name": "Sony WH-1000XM5",
                        "sku": "SONY-WH1000XM5",
                        "price": 34990,
                        "stock": random.randint(10, 40),
                        "specifications": {
                            "Тип": "Накладные",
                            "Шумоподавление": "Активное",
                            "Время работы": "До 30 часов",
                            "Подключение": "Bluetooth 5.2, проводное",
                            "Цвет": "Серебристый"
                        }
                    },
                    {
                        "name": "Apple AirPods Pro 2",
                        "sku": "APP2-USBC",
                        "price": 24990,
                        "stock": random.randint(15, 60),
                        "specifications": {
                            "Тип": "Вкладыши",
                            "Шумоподавление": "Активное",
                            "Время работы": "До 6 часов",
                            "Подключение": "Bluetooth 5.3",
                            "Зарядка": "USB-C"
                        }
                    }
                ]
            },
            # Фототехника
            {
                "category": "Фототехника",
                "products": [
                    {
                        "name": "Sony Alpha A7 IV",
                        "sku": "SONY-A7IV-BODY",
                        "price": 199990,
                        "stock": random.randint(2, 8),
                        "specifications": {
                            "Тип": "Беззеркальная",
                            "Матрица": "Full-frame 33MP",
                            "Автофокус": "759 точек",
                            "Видео": "4K 60fps",
                            "Стабилизация": "5-осевая"
                        }
                    },
                    {
                        "name": "Canon EOS R6 Mark II",
                        "sku": "CANON-R6II",
                        "price": 179990,
                        "stock": random.randint(3, 10),
                        "specifications": {
                            "Тип": "Беззеркальная",
                            "Матрица": "Full-frame 24.2MP",
                            "Автофокус": "Dual Pixel CMOS AF II",
                            "Видео": "4K 60fps",
                            "Стабилизация": "In-body"
                        }
                    }
                ]
            },
            # Аксессуары
            {
                "category": "Аксессуары",
                "products": [
                    {
                        "name": "Зарядное устройство Anker 65W",
                        "sku": "ANKER-65W-GAN",
                        "price": 3990,
                        "stock": random.randint(20, 100),
                        "specifications": {
                            "Мощность": "65W",
                            "Технология": "GaN II",
                            "Порты": "2x USB-C, 1x USB-A",
                            "Протоколы": "PD 3.0, QC 4.0",
                            "Складная вилка": "Да"
                        }
                    },
                    {
                        "name": "Чехол для iPhone 15 Pro (кожаный)",
                        "sku": "CASE-IP15PRO-LEATHER",
                        "price": 4990,
                        "stock": random.randint(15, 80),
                        "specifications": {
                            "Материал": "Натуральная кожа",
                            "Совместимость": "iPhone 15 Pro",
                            "Защита камеры": "Да",
                            "MagSafe": "Поддерживается",
                            "Цвет": "Темно-синий"
                        }
                    }
                ]
            }
        ]

        # Создаем товары
        created_count = 0
        for category_data in product_data:
            # Получаем категорию из нашего словаря
            category_name = category_data["category"]
            if category_name in category_map:
                category = category_map[category_name]
                
                # Создаем товары для категории
                for product_info in category_data["products"]:
                    # Проверяем, существует ли товар с таким SKU
                    if not Product.objects.filter(sku=product_info["sku"]).exists():
                        # Генерируем описание, если его нет
                        description = product_info.get("description", lorem.paragraph())
                        
                        # Создаем товар
                        product = Product.objects.create(
                            sku=product_info["sku"],
                            name=product_info["name"],
                            description=description,
                            price=product_info["price"],
                            stock=product_info["stock"],
                            category=category,
                            is_available=True,
                            specifications=product_info["specifications"],
                            creation_date=timezone.now()
                        )
                        
                        created_count += 1
                        self.stdout.write(self.style.SUCCESS(f'Создан товар: {product.name} (SKU: {product.sku})'))
                    else:
                        self.stdout.write(self.style.WARNING(f'Товар с SKU {product_info["sku"]} уже существует'))
            else:
                self.stdout.write(self.style.ERROR(f'Ошибка: категория "{category_name}" отсутствует в словаре категорий'))

        self.stdout.write(self.style.SUCCESS(f'Успешно создано {created_count} товаров')) 