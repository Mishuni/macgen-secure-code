from django.test import TestCase
from django.urls import reverse
from django.http import JsonResponse

class DecideUnsubscribeViewTests(TestCase):
    def test_unsubscribe_request(self):
        email_content = """
        MIME-Version:1.0
        From:Alex <alex@example.com>
        Date:Thu, 10 Jan 2019 14:21:11 -0800
        Subject:Re:Newsletter Subscription
        Content-Type:text/plain; charset="UTF-8"
        Content-Transfer-Encoding:quoted-printable

        Please unsubscribe me from this mailing list.
        """
        response = self.client.post(reverse('decide_unsubscribe'), data=email_content, content_type='text/plain')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"email": "alex@example.com", "unsubscribe": True})

    def test_neutral_reply(self):
        email_content = """
        MIME-Version:1.0
        From:Chris <c@sigparser.com>
        Date:Wed, 9 Jan 2019 08:36:15 -0800
        Subject:Re:food for thought
        Content-Type:text/plain; charset="UTF-8"
        Content-Transfer-Encoding:quoted-printable

        Ok. Just a thought. Got it.
        """
        response = self.client.post(reverse('decide_unsubscribe'), data=email_content, content_type='text/plain')
        self.assertEqual(response.status_code, 200)
        self.assertJSONEqual(response.content, {"email": "c@sigparser.com", "unsubscribe": False})