from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class User(AbstractUser):
    USER_ROLES = (
        ('admin', 'admin'),
        ('user', 'user'),
        ('moderator', 'moderator')
    )
    email = models.EmailField(unique=True, blank=False)
    username = models.CharField(unique=True, max_length=100)
    bio = models.CharField(max_length=150)
    role = models.CharField(
        max_length=10,
        choices=USER_ROLES,
        default='user')

    @property
    def is_admin(self):
        return self.role == 'admin' or self.is_superuser

    @property
    def is_moderator(self):
        return self.role == 'moderator'

    class Meta:
        ordering = ('-pk',)


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('slug',)
        verbose_name = 'Categories'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        ordering = ('slug',)
        verbose_name = 'Genres'

    def __str__(self):
        return self.name


class Title(models.Model):
    name = models.CharField(max_length=100)
    year = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(
            1895,
            'Год выпуска не может быть раньше выпуска первого фильма,'),
            MaxValueValidator(
                2100,
                'Год выпуска не может быть больше 2100-го года')],
        db_index=True
    )
    genre = models.ManyToManyField(
        Genre,
        related_name='genre_title'
    )
    description = models.TextField(blank=True)
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='titles'
    )

    class Meta:
        ordering = ('-pk',)


class Review(models.Model):
    title = models.ForeignKey(Title,
                              on_delete=models.CASCADE,
                              related_name='reviews')
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='reviews'
    )
    score = models.FloatField()
    pub_date = models.DateTimeField('review date',
                                    auto_now_add=True,
                                    db_index=True)

    class Meta:
        ordering = ('-pub_date',)
        constraints = [
            models.UniqueConstraint(
                fields=('title', 'author',),
                name='unique_review'
            )
        ]

    def __str__(self):
        return self.text[:30]


class Comment(models.Model):
    review = models.ForeignKey(
        Review,
        on_delete=models.CASCADE,
        related_name='comment'
    )
    text = models.TextField()
    author = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='comment'
    )
    pub_date = models.DateTimeField('comment date',
                                    auto_now_add=True,
                                    db_index=True)

    class Meta:
        ordering = ('-pub_date',)
