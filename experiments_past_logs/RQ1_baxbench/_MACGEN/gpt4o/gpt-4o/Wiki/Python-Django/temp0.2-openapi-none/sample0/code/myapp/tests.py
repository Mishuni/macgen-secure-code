from django.test import TestCase
from .models import Entry

class EntryModelTest(TestCase):
    def setUp(self):
        Entry.objects.create(title="Test Entry", content="This is a test entry.", last_modified_by="tester")

    def test_entry_content(self):
        entry = Entry.objects.get(id=1)
        expected_object_name = f'{entry.title}'
        self.assertEqual(expected_object_name, 'Test Entry')