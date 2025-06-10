from django.db import models
from django.conf import settings
from django.core.validators import MinValueValidator, MaxValueValidator


class Country(models.Model):
    name = models.CharField("Назва країни", max_length=100, unique=True)

    class Meta:
        db_table = "country"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Company(models.Model):
    name = models.CharField("Назва компанії", max_length=100, unique=True)

    class Meta:
        db_table = "company"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField("Назва жанру", max_length=100, unique=True)

    class Meta:
        db_table = "genre"
        ordering = ["name"]

    def __str__(self):
        return self.name


class Movie(models.Model):
    id = models.IntegerField("ID з CSV", primary_key=True)
    title = models.CharField("Назва", max_length=255)
    poster_path = models.URLField("Шлях до постеру", max_length=500, null=True, blank=True)
    overview = models.TextField("Опис", blank=True)
    release_date = models.DateField("Дата виходу", null=True, blank=True)
    runtime = models.PositiveIntegerField("Тривалість (хв)", null=True, blank=True)
    vote_average = models.FloatField(
        "Середній рейтинг",
        validators=[MinValueValidator(0), MaxValueValidator(10)],
        null=True,
        blank=True
    )
    vote_count = models.PositiveIntegerField("Кількість голосів", null=True, blank=True)
    countries = models.ManyToManyField(
        Country,
        related_name="movies",
        blank=True,
        verbose_name="Країни виробництва"
    )
    companies = models.ManyToManyField(
        Company,
        related_name="movies",
        blank=True,
        verbose_name="Компанії виробництва"
    )
    genres = models.ManyToManyField(
        Genre,
        related_name="movies",
        blank=True,
        verbose_name="Жанри"
    )

    class Meta:
        db_table = "movie"
        ordering = ["id"]

    def __str__(self):
        return self.title


class Comment(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    content = models.TextField("Текст коментаря")
    created_at = models.DateTimeField("Час створення", auto_now_add=True)

    class Meta:
        db_table = "comment"
        ordering = ["user", "created_at"]

    def __str__(self):
        return f"{self.user.username} on {self.movie.title}: {self.content[:30]}…"


class Rating(models.Model):
    score = models.IntegerField(
        "Оцінка",
        validators=[MinValueValidator(0), MaxValueValidator(10)],
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    movie = models.ForeignKey(
        Movie,
        on_delete=models.CASCADE,
        related_name='ratings'
    )
    created_at = models.DateTimeField("Час створення", auto_now_add=True)

    class Meta:
        db_table = "rating"
        unique_together = ("user", "movie")

    def __str__(self):
        return f"{self.user.username} → {self.movie.title}: {self.score}"
