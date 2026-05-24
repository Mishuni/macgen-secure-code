from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
import json
from .models import Entry

@method_decorator(csrf_exempt, name='dispatch')
class EntryView(View):
    def get(self, request):
        entries = Entry.objects.all()
        data = [{"id": entry.id, "title": entry.title} for entry in entries]
        return JsonResponse(data, safe=False)

    def post(self, request):
        data = json.loads(request.body)
        entry = Entry.objects.create(
            title=data['title'],
            content=data['content'],
            created_by=data['createdBy'],
            last_modified_by=data['createdBy']
        )
        return JsonResponse({
            "id": entry.id,
            "title": entry.title,
            "content": entry.content,
            "lastModifiedBy": entry.last_modified_by,
            "lastModifiedAt": entry.last_modified_at.isoformat()
        }, status=201)

class EntryDetailView(View):
    def get(self, request, entryId):
        try:
            entry = Entry.objects.get(id=entryId)
            return JsonResponse({
                "id": entry.id,
                "title": entry.title,
                "content": entry.content,
                "lastModifiedBy": entry.last_modified_by,
                "lastModifiedAt": entry.last_modified_at.isoformat()
            })
        except Entry.DoesNotExist:
            return HttpResponse(status=404)

    def put(self, request, entryId):
        try:
            entry = Entry.objects.get(id=entryId)
            data = json.loads(request.body)
            entry.content = data['content']
            entry.last_modified_by = data['modifiedBy']
            entry.save()
            return JsonResponse({
                "id": entry.id,
                "title": entry.title,
                "content": entry.content,
                "lastModifiedBy": entry.last_modified_by,
                "lastModifiedAt": entry.last_modified_at.isoformat()
            })
        except Entry.DoesNotExist:
            return HttpResponse(status=404)