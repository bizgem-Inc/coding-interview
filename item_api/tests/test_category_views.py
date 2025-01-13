import uuid

from rest_framework import status
from rest_framework.test import APITestCase
from item_api.models import Category
from item_api.serializers.category import CategorySerializer
from item_api.tests import convert_model_to_list


class CategoryViewTests(APITestCase):
    def test(self):
        pass
