from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from .models import Service
import json

class ServiceMonitoringTests(TestCase):

    def test_register_heartbeat(self):
        url = reverse('register_heartbeat')
        data = {'serviceId': 'test-service', 'token': 'test-token'}
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(Service.objects.count(), 1)
        self.assertEqual(Service.objects.get().service_id, 'test-service')

    def test_get_services(self):
        Service.objects.create(service_id='test-service', token='test-token')
        url = reverse('get_services')
        data = {'token': 'test-token'}
        response = self.client.post(url, data=json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.json()), 1)
        self.assertEqual(response.json()[0]['serviceId'], 'test-service')