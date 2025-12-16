# coding-interview

This project is a Django REST API for managing categories and companies. It provides endpoints to create, read, update, and delete Category objects, and includes automated tests for the API.

## Features
- Django 3.11+ and Django REST Framework
- PostgreSQL database (via psycopg2)
- Category model supports parent-child relationships and company association
- Full CRUD API for Category
- Automated API tests

## Setup

### 1. Install Python 3.11
Download and install Python 3.11 from the [official website](https://www.python.org/downloads/release/python-3110/).

### 2. Install dependencies
```
pip install -r requirements.txt
```

### 3. Run migrations
```
python manage.py migrate
```

### 4. Run the development server
```
python manage.py runserver
```

### 5. Run tests
```
python manage.py test
```

## API Endpoints
- `GET /api/categories/` — List categories
- `POST /api/categories/` — Create a category
- `GET /api/categories/<id>/` — Retrieve a category
- `PUT /api/categories/<id>/` — Update a category
- `DELETE /api/categories/<id>/` — Delete a category

## Testing Requirement (日本語)
上記レポジトリ内で以下の実装を行いPull Requestのご作成をお願いいたします。
- Categoryモデルの読み取り・作成・更新・削除が出来るAPI
  ※ views/category.py, serializers/category.py に実装
- APIのテストの実装
  ※ test_views.pyに実装