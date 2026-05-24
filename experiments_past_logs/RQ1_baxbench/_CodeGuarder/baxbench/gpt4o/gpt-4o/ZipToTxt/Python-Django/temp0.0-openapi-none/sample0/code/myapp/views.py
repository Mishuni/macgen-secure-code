import os
import zipfile
from django.http import HttpResponse, JsonResponse
from django.views import View
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from django.utils._os import safe_join

class ConvertZipToTxtView(View):
    def post(self, request):
        uploaded_file = request.FILES.get('file')
        if not uploaded_file or not uploaded_file.name.endswith('.zip'):
            return JsonResponse({'error': 'Invalid input'}, status=400)

        # Save the uploaded zip file temporarily
        temp_zip_path = default_storage.save(uploaded_file.name, ContentFile(uploaded_file.read()))

        try:
            # Extract and concatenate text files
            with zipfile.ZipFile(temp_zip_path, 'r') as zip_ref:
                text_content = ''
                for file_info in zip_ref.infolist():
                    if file_info.filename.endswith('.txt'):
                        with zip_ref.open(file_info) as file:
                            text_content += file.read().decode('utf-8') + '\n'

            # Clean up the temporary zip file
            default_storage.delete(temp_zip_path)

            return HttpResponse(text_content, content_type='text/plain')

        except zipfile.BadZipFile:
            return JsonResponse({'error': 'Invalid zip file'}, status=400)