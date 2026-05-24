from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import get_object_or_404
from .models import Entry
import json

@csrf_exempt
def entry_list(request):
    if request.method == 'GET':
        entries = Entry.objects.all()
        data = [{'id': entry.id, 'title': entry.title} for entry in entries]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        try:
            body = json.loads(request.body)
            entry = Entry.objects.create(
                title=body['title'],
                content=body['content'],
                created_by=body['createdBy']
            )
            return JsonResponse({
                'id': entry.id,
                'title': entry.title,
                'content': entry.content,
                'lastModifiedBy': entry.last_modified_by,
                'lastModifiedAt': entry.last_modified_at.isoformat()
            }, status=201)
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data'}, status=400)

@csrf_exempt
def entry_detail(request, entryId):
    entry = get_object_or_404(Entry, id=entryId)

    if request.method == 'GET':
        return JsonResponse({
            'id': entry.id,
            'title': entry.title,
            'content': entry.content,
            'lastModifiedBy': entry.last_modified_by,
            'lastModifiedAt': entry.last_modified_at.isoformat()
        })

    elif request.method == 'PUT':
        try:
            body = json.loads(request.body)
            entry.content = body['content']
            entry.last_modified_by = body['modifiedBy']
            entry.save()
            return JsonResponse({
                'id': entry.id,
                'title': entry.title,
                'content': entry.content,
                'lastModifiedBy': entry.last_modified_by,
                'lastModifiedAt': entry.last_modified_at.isoformat()
            })
        except (KeyError, json.JSONDecodeError):
            return JsonResponse({'error': 'Invalid data'}, status=400)