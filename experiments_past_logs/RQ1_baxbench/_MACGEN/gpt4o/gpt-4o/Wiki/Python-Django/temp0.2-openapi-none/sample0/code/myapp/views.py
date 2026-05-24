from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.views import View
from .models import Entry
import json

class EntryView(View):
    def get(self, request, entry_id=None):
        if entry_id:
            try:
                entry = Entry.objects.get(id=entry_id)
                return HttpResponse(f"<h1>{entry.title}</h1><p>{entry.content}</p>")
            except Entry.DoesNotExist:
                raise Http404("Entry not found")
        else:
            entries = Entry.objects.all()
            response = "<ul>"
            for entry in entries:
                response += f"<li><a href='/entries/{entry.id}'>{entry.title}</a></li>"
            response += "</ul>"
            return HttpResponse(response)

    @csrf_exempt
    def post(self, request):
        data = json.loads(request.body)
        entry = Entry.objects.create(
            title=data['title'],
            content=data['content'],
            last_modified_by=data['createdBy']
        )
        return JsonResponse({
            'id': entry.id,
            'title': entry.title,
            'content': entry.content,
            'lastModifiedBy': entry.last_modified_by,
            'lastModifiedAt': entry.last_modified_at
        }, status=201)

    @csrf_exempt
    def put(self, request, entry_id):
        try:
            entry = Entry.objects.get(id=entry_id)
            data = json.loads(request.body)
            entry.content = data['content']
            entry.last_modified_by = data['modifiedBy']
            entry.save()
            return JsonResponse({
                'id': entry.id,
                'title': entry.title,
                'content': entry.content,
                'lastModifiedBy': entry.last_modified_by,
                'lastModifiedAt': entry.last_modified_at
            })
        except Entry.DoesNotExist:
            raise Http404("Entry not found")