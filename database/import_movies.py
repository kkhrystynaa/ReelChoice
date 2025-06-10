import os
import django
import csv
from datetime import datetime
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ReelChoice.settings')
django.setup()

from reelchoice_app.models import Genre, Company, Country, Movie


def import_movies():
    """
    Зчитає movies.csv і імпортує дані в базу,
    нормалізуючи genres, production_companies і production_countries.
    """
    project_root = settings.BASE_DIR
    csv_path = os.path.join(project_root, 'data', 'movies.csv')
    print(f"Шукаю CSV за шляхом: {csv_path}")
    if not os.path.exists(csv_path):
        print(f"Файл не знайдено")
        return

    with open(csv_path, encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:

            rd = None
            date_str = row.get('release_date')
            if date_str:
                try:
                    rd = datetime.strptime(date_str, '%Y-%m-%d').date()
                except ValueError:
                    rd = None

            movie_id = int(row['id'])
            defaults = {
                'title': row['title'][:255],
                'poster_path': row.get('poster_path') or None,
                'overview': row.get('overview') or '',
                'release_date': rd,
                'runtime': int(row['runtime']) if row.get('runtime') else None,
                'vote_average': float(row['vote_average']) if row.get('vote_average') else None,
                'vote_count': int(row['vote_count']) if row.get('vote_count') else None,
                'popularity': float(row.get('popularity') or 0),
            }
            movie, created = Movie.objects.update_or_create(
                id=movie_id,
                defaults=defaults
            )

            movie.genres.clear()
            for name in row.get('genres', '').split(','):
                name = name.strip()
                if name:
                    genre, _ = Genre.objects.get_or_create(name=name)
                    movie.genres.add(genre)

            movie.companies.clear()
            for name in row.get('production_companies', '').split(','):
                name = name.strip()
                if name:
                    pc, _ = Company.objects.get_or_create(name=name)
                    movie.companies.add(pc)

            movie.countries.clear()
            for name in row.get('production_countries', '').split(','):
                name = name.strip()
                if name:
                    country, _ = Country.objects.get_or_create(name=name)
                    movie.countries.add(country)

    print("\n Імпорт фільмів завершено!")


if __name__ == '__main__':
    import_movies()