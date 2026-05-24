from django.shortcuts import get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Entry
import json
import uuid

def list_entries(request):
    entries = Entry.objects.all().values('id', 'title')
    return JsonResponse(list(entries), safe=False)

@csrf_exempt
def create_entry(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        entry = Entry(
            id=str(uuid.uuid4()),
            title=data['title'],
            content=data['content'],
            last_modified_by=data['createdBy']
        )
        entry.save()
        return JsonResponse({'id': entry.id, 'title': entry.title, 'content': entry.content}, status=201)
    return HttpResponse(status=405)

def get_entry(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    return JsonResponse({
        'id': entry.id,
        'title': entry.title,
        'content': entry.content,
        'lastModifiedBy': entry.last_modified_by,
        'lastModifiedAt': entry.last_modified_at
    })

@csrf_exempt
def update_entry(request, entry_id):
    if request.method == 'PUT':
        entry = get_object_or_404(Entry, id=entry_id)
        data = json.loads(request.body)
        entry.content = data['content']
        entry.last_modified_by = data['modifiedBy']
        entry.save()
        return JsonResponse({'id': entry.id, 'title': entry.title, 'content': entry.content})
    return HttpResponse(status=405)

def entry_edits(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id)
    # Placeholder for edit history logic
    return JsonResponse({'message': 'Edit history not implemented yet.'})