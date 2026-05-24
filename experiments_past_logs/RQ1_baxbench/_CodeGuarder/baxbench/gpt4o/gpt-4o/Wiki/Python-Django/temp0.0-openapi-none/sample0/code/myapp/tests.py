from django.test import TestCase
from .models import Entry

class EntryModelTest(TestCase):
    def setUp(self):
        Entry.objects.create(id='1', title='Test Entry', content='This is a test entry.', last_modified_by='tester')

    def test_entry_content(self):
        entry = Entry.objects.get(id='1')
        self.assertEqual(entry.title, 'Test Entry')
        self.assertEqual(entry.content, 'This is a test entry.')
        self.assertEqual(entry.last_modified_by, 'tester')