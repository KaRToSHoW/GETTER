from django.core.management.base import BaseCommand
from main.models import Review

class Command(BaseCommand):
    help = 'Удаляет отзывы с некорректными комментариями, содержащими текст "<generator object"'

    def handle(self, *args, **options):
        # Необходимо использовать прямой SQL-запрос, так как Django ORM может не корректно искать по таким строкам
        self.stdout.write(self.style.SUCCESS('Поиск и удаление отзывов с некорректными комментариями...'))
        
        # Сначала получим все отзывы
        reviews = Review.objects.all()
        
        deleted_count = 0
        for review in reviews:
            # Проверяем, содержит ли комментарий некорректный текст
            comment_str = str(review.comment)
            if "<generator object" in comment_str:
                review_id = review.id
                review.delete()
                deleted_count += 1
                self.stdout.write(f"Удален отзыв #{review_id} с некорректным комментарием: {comment_str[:60]}...")
        
        self.stdout.write(self.style.SUCCESS(f'Удалено {deleted_count} отзывов с некорректными комментариями')) 