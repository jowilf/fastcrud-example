from unicodedata import category
from faker import Faker
from fastapi.testclient import TestClient
from sqlalchemy import null
# from mdgen import MarkdownPostProvider

from app.main import app

client = TestClient(app)

fake = Faker()
# fake.add_provider(MarkdownPostProvider)


def create_user():
    res = client.post('api/users', json=dict(
        name=fake.name(),
        age=fake.pyint(0, 100),
        is_active=fake.pybool(),
        birthday=fake.date(),
        sex=['unknown', 'male', 'female'][fake.pyint(0, 2)]
    ))
    print(res.json())


def create_post(user_id):
    res = client.post('api/posts', json=dict(
        title=fake.catch_phrase(),
        content=fake.paragraph(nb_sentences=3),
        user_id=user_id
    ))


def create_users(n):
    for i in range(n):
        create_user()


def fake_user_post():
    create_users(100)
    for i in range(20):
        for j in range(i % 5):
            create_post(i)


def fake_netflix():
    for i in range(100):
        client.post('api/categories',
                    data=dict(name=fake.job(),
                              description=fake.paragraph(nb_sentences=2)),
                    files={} if (i % 3 == 0) else {'image': (fake.file_name(
                        category='image', extension='png'), fake.image())}
                    )
    for i in range(200):
        client.post('api/movies',
                    json={
                        "name": fake.catch_phrase(),
                        "description": fake.paragraph(nb_sentences=3),
                        "watch_count": fake.pyint(0, 100000),
                        "tags": fake.pylist(allowed_types=[str]),
                        "release_date": fake.date(),
                        "category_id": None if (i % 5 == 0) else fake.pyint(1, 100),
                    }
                    )

    for i in range(100):
        client.post(f'api/movies/{fake.pyint(1, 20)}/authors',
                    json={
                        "lastname": fake.last_name(),
                        "firstname": fake.first_name(),
                        "sex": ['unknown', 'male', 'female'][fake.pyint(0, 2)],
                        "birthday": fake.date()
                    })
    for i in range(30):
        n = fake.pyint(1, 3)
        client.post('api/movie_previews',
                    data=dict(movie_id=fake.pyint(1, 200)),
                    files=[('images', (fake.file_name(
                        category='image', extension='png'), fake.image())) for _ in range(n)]
                    )
    for i in range(100):
        client.post(f'api/authors',
                    json={
                        "lastname": fake.last_name(),
                        "firstname": fake.first_name(),
                        "sex": ['unknown', 'male', 'female'][fake.pyint(0, 2)],
                        "birthday": fake.date()
                    })
    for i in range(40):
        client.post(f'api/authors/{fake.pyint(1, 20)}/movies',
                    json={
                        "name": fake.catch_phrase(),
                        "description": fake.paragraph(nb_sentences=3),
                        "watch_count": fake.pyint(0, 100000),
                        "tags": fake.pylist(allowed_types=[str]),
                        "release_date": fake.date(),
                        "category_id": None if (i % 5 == 0) else fake.pyint(1, 100),
                    }
    )
    pass


if __name__ == '__main__':
    # fake_user_post()
    fake_netflix()
    # print(zip(['i'] * 3))
    n = 2
