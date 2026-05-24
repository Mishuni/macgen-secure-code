from django.http import JsonResponse, HttpResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Entry, Edit
import json
from django.utils.html import escape

@csrf_exempt
def entries(request):
    if request.method == 'GET':
        entries = Entry.objects.all()
        data = [{'id': entry.id, 'title': entry.title} for entry in entries]
        return JsonResponse(data, safe=False)

    elif request.method == 'POST':
        body = json.loads(request.body)
        entry = Entry.objects.create(
            title=body['title'],
            content=body['content'],
            lastModifiedBy=body['createdBy']
        )
        return JsonResponse({'id': entry.id, 'title': entry.title, 'content': entry.content}, status=201)

@csrf_exempt
def entry_detail(request, entryId):
    try:
        entry = Entry.objects.get(id=entryId)
    except Entry.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        safe_content = escape(entry.content)
        return HttpResponse(safe_content)

    elif request.method == 'PUT':
        body = json.loads(request.body)
        entry.content = body['content']
        entry.lastModifiedBy = body['modifiedBy']
        entry.save()
        Edit.objects.create(entry=entry, modifiedBy=body['modifiedBy'], summary=body.get('summary', ''), content=body['content'])
        return JsonResponse({'id': entry.id, 'title': entry.title, 'content': entry.content})

@csrf_exempt
def entry_edits(request, entryId):
    try:
        entry = Entry.objects.get(id=entryId)
    except Entry.DoesNotExist:
        return HttpResponse(status=404)

    if request.method == 'GET':
        edits = entry.edits.all()
        data = [{'modifiedBy': edit.modifiedBy, 'summary': edit.summary, 'modifiedAt': edit.modifiedAt} for edit in edits]
        return JsonResponse(data, safe=False)