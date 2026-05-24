from django.http import JsonResponse, HttpResponse, Http404
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from django.utils.timezone import now
from .models import Entry, Edit
import json

@csrf_exempt
def entries(request):
    if request.method == 'GET':
        entries = Entry.objects.all()
        data = [{"id": entry.id, "title": entry.title} for entry in entries]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            title = data['title']
            content = data['content']
            created_by = data['createdBy']
            entry = Entry.objects.create(title=title, content=content, last_modified_by=created_by)
            return JsonResponse({"id": entry.id, "title": entry.title, "content": entry.content}, status=201)
        except KeyError:
            return JsonResponse({"error": "Invalid data"}, status=400)

@csrf_exempt
def entry_detail(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)

    if request.method == 'GET':
        data = {
            "id": entry.id,
            "title": entry.title,
            "content": entry.content,
            "lastModifiedBy": entry.last_modified_by,
            "lastModifiedAt": entry.last_modified_at,
        }
        return JsonResponse(data)

    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            content = data['content']
            modified_by = data['modifiedBy']
            summary = data['summary']
            Edit.objects.create(entry=entry, content=entry.content, modified_by=modified_by, summary=summary)
            entry.content = content
            entry.last_modified_by = modified_by
            entry.save()
            return JsonResponse({"id": entry.id, "title": entry.title, "content": entry.content})
        except KeyError:
            return JsonResponse({"error": "Invalid data"}, status=400)

def entry_edits(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    edits = entry.edits.all()
    data = [
        {
            "content": edit.content,
            "modifiedBy": edit.modified_by,
            "summary": edit.summary,
            "modifiedAt": edit.modified_at,
        }
        for edit in edits
    ]
    return JsonResponse(data, safe=False)