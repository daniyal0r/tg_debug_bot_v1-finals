from django.db import models


class User(models.Model):
    iduser = models.PositiveIntegerField(

        verbose_name='ID user tg'
    )
    username = models.CharField(
        max_length=20,
        verbose_name='username',
        db_index=True,
    )
    name = models.CharField(
        max_length=20,
        verbose_name='name',
        db_index=True,
    )

    is_admin = models.BooleanField(
        default=False
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.name


class Platform(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='Admin',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        default=None
    )
    name = models.TextField(
        max_length=50,
        null=True,
        blank=True
    )
    url = models.TextField(
        max_length=50,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'платформы'


class Debug(models.Model):
    platform = models.ForeignKey(
        Platform,
        verbose_name='платформа',
        on_delete=models.CASCADE,
    )
    from_user = models.ForeignKey(
        User,
        verbose_name='Отправитель',
        related_name='Отправитель',
        on_delete=models.CASCADE,
    )
    request_text = models.TextField(
        max_length=1000,
        null=True,
        blank=True
    )
    file = models.TextField(
        max_length=1000,
        null=True,
        blank=True
    )
    is_answered = models.BooleanField(
        default=False
    )
    answer = models.TextField(
        max_length=1000,
        null=True,
        blank=True
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата создания',
    )

    def __str__(self):
        return f'Debug {self.pk} от {self.from_user}'


class Asnwering(models.Model):
    from_user = models.ForeignKey(
        User,
        verbose_name='Отправ',
        related_name='Отправ',
        on_delete=models.CASCADE,
    )
    ans_user = models.ForeignKey(
        User,
        verbose_name='ответ',
        related_name='ответ',
        on_delete=models.CASCADE,
    )
    problem = models.ForeignKey(
        Debug,
        verbose_name='проблема',
        related_name='проблема',
        on_delete=models.CASCADE,
    )
    active = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.id}"

    class Meta:
        verbose_name = 'онлайн ответ'