from django.http import JsonResponse, HttpResponse, Http404
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Entry, Edit
import json

@csrf_exempt
def entries_list(request):
    if request.method == 'GET':
        entries = Entry.objects.all()
        response_data = [{'id': entry.id, 'title': entry.title} for entry in entries]
        return JsonResponse(response_data, safe=False)
    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            new_entry = Entry.objects.create(
                title=data['title'],
                content=data['content'],
                last_modified_by=data['createdBy']
            )
            return JsonResponse({'id': new_entry.id, 'title': new_entry.title, 'content': new_entry.content}, status=201)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data'}, status=400)

@csrf_exempt
def entry_detail(request, entryId):
    entry = get_object_or_404(Entry, id=entryId)
    if request.method == 'GET':
        response_data = {
            'id': entry.id,
            'title': entry.title,
            'content': entry.content,
            'lastModifiedBy': entry.last_modified_by,
            'lastModifiedAt': entry.last_modified_at,
        }
        return JsonResponse(response_data)
    elif request.method == 'PUT':
        try:
            data = json.loads(request.body)
            entry.content = data['content']
            entry.last_modified_by = data['modifiedBy']
            entry.save()
            Edit.objects.create(
                entry=entry,
                content=data['content'],
                modified_by=data['modifiedBy'],
                summary=data.get('summary', '')
            )
            return JsonResponse({'id': entry.id, 'title': entry.title, 'content': entry.content})
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data'}, status=400)

def entry_edits(request, entryId):
    entry = get_object_or_404(Entry, id=entryId)
    edits = entry.edits.all()
    response_data = [{
        'content': edit.content,
        'modifiedBy': edit.modified_by,
        'summary': edit.summary,
        'modifiedAt': edit.modified_at
    } for edit in edits]
    return JsonResponse(response_data, safe=False)