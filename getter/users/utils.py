from django.core.mail import send_mail
from django.conf import settings


def send_welcome_email(user_email):
    """
    Отправляет приветственное письмо новому пользователю
    """
    subject = 'Добро пожаловать в наш магазин!'
    message = f'''
    Здравствуйте!
    
    Благодарим за регистрацию в нашем интернет-магазине.
    
    С уважением,
    Команда поддержки
    '''
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
    
    return True


def send_password_reset_email(user_email, reset_link):
    """
    Отправляет письмо для сброса пароля
    """
    subject = 'Сброс пароля'
    message = f'''
    Здравствуйте!
    
    Для сброса пароля перейдите по следующей ссылке:
    {reset_link}
    
    Если вы не запрашивали сброс пароля, проигнорируйте это письмо.
    
    С уважением,
    Команда поддержки
    '''
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
    
    return True


def send_order_confirmation_email(user_email, order_number, order_details):
    """
    Отправляет письмо с подтверждением заказа
    """
    subject = f'Подтверждение заказа #{order_number}'
    message = f'''
    Здравствуйте!
    
    Ваш заказ #{order_number} успешно оформлен.
    
    Детали заказа:
    {order_details}
    
    С уважением,
    Команда поддержки
    '''
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
    
    return True


def send_order_status_update(user_email, order_number, status, comment=None):
    """
    Отправляет уведомление об изменении статуса заказа
    
    Args:
        user_email: Email пользователя
        order_number: Номер заказа
        status: Новый статус заказа
        comment: Дополнительный комментарий (опционально)
    """
    status_map = {
        'pending': 'Ожидает обработки',
        'assembling': 'В сборке',
        'shipped': 'Отправлен',
        'delivered': 'Доставлен',
        'canceled': 'Отменен'
    }
    
    status_text = status_map.get(status, status)
    
    subject = f'Обновление статуса заказа #{order_number}'
    
    message = f'''
    Здравствуйте!
    
    Статус вашего заказа #{order_number} изменился на: {status_text}
    '''
    
    if comment:
        message += f'''
    
    Комментарий: {comment}
    '''
    
    message += f'''
    
    С уважением,
    Команда поддержки
    '''
    
    send_mail(
        subject=subject,
        message=message,
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[user_email],
        fail_silently=False,
    )
    
    return True 