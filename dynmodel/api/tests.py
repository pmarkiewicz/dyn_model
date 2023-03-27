from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


class DynamicModelsTests(APITestCase):
    create_datamodel = {
        "make": "character",
        "model": "character",
        "year": "integer",
        "valid_license": "boolean"
    }

    update_datamodel = {
        "make": "character",
        "model": "character",
        "make_year": "integer",
        "licence_valid_year": "integer"
    }

    error_datamodel = {
        "make": "character",
        "model": "charcter",
        "make_year": "integer",
        "licence_valid_year": "integer"   
    }

    data = [
        {
            "make": "toyota",
            "model": "corolla",
            "year": 2012,
            "valid_license": True
        },
        {
            "make": "mazda",
            "model": "cx-5",
            "year": 2018,
            "valid_license": True
        }
    ]

    def test_create_table(self):
        create_url = reverse('create-table')

        response = self.client.post(create_url, self.create_datamodel, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)

        response = self.client.post(create_url, self.create_datamodel, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)

    def test_alter_table(self):
        create_url = reverse('create-table')

        response = self.client.post(create_url, self.create_datamodel, format='json')
        id = response.data['id']
        update_url = reverse('update-table', args=[id])

        response = self.client.put(update_url, self.update_datamodel, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_inserts_select(self):
        create_url = reverse('create-table')
        response = self.client.post(create_url, self.create_datamodel, format='json')
        id = response.data['id']

        list_rows_url = reverse('list-rows', args=[id])
        response = self.client.get(list_rows_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 0)

        create_row_url = reverse('create-row', args=[id])
        for d in self.data:
            response = self.client.post(create_row_url, d, format='json')
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        response = self.client.get(list_rows_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0].get("make"), "toyota")

    def test_error_creation(self):
        create_url = reverse('create-table')
        response = self.client.post(create_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        response = self.client.post(create_url, self.error_datamodel, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        create_url = reverse('create-table')
        response = self.client.post(create_url, self.create_datamodel, format='json')
        id = response.data['id']

        update_url = reverse('update-table', args=[id])

        response = self.client.put(update_url, self.error_datamodel, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_error_data(self):
        list_error_row_url = reverse('list-rows', args=[9999])
        response = self.client.get(list_error_row_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

        create_error_row_url = reverse('create-row', args=[9999])
        response = self.client.post(create_error_row_url, {}, format='json')
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
