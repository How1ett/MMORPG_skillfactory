from django.db import models
from django.contrib.auth.models import User
from ckeditor.fields import RichTextField
from django.urls import reverse

categories = (('tanks', 'Танки'),
              ('healers', 'Хилы'),
              ('damage_dealers', 'ДД'),
              ('merchants', 'Торговцы'),
              ('guild_masters', 'Гилдмастеры'),
              ('quest_givers', 'Квестгиверы'),
              ('blacksmiths', 'Кузнецы'),
              ('tanners', 'Кожевники'),
              ('potion_makers', 'Зельевары'),
              ('spell_masters', 'Мастера заклинаний'))


class Advertisement(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    category = models.CharField(max_length=15, choices=categories, verbose_name='Категория')
    time_create = models.DateTimeField(auto_now_add=True)
    title = models.CharField(max_length=100, verbose_name='Заголовок')
    content = RichTextField()


class Comment(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    advertisement = models.ForeignKey(Advertisement, on_delete=models.CASCADE)
    time_create = models.DateTimeField(auto_now_add=True)
    text = models.TextField(verbose_name='Текст')
    moderation = models.BooleanField(default=False)

    def get_absolute_url(self):
        return reverse('comments_view', args=[str(self.id)])