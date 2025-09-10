from django.test import SimpleTestCase
from accounts.models import Event

class EventCheckTest(SimpleTestCase):
    databases = "__all__"   # 👉 실제 DB 접근 허용

    def test_event_count(self):
        count = Event.objects.count()
        print("현재 이벤트 개수:", count)
        self.assertTrue(count > 0)
