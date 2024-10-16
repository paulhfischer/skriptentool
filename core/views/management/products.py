from django.http import JsonResponse
from core.models import LectureNote
from django.views.decorators.csrf import csrf_exempt
import json

@csrf_exempt
def products(request):
    if request.method == 'POST':
        try: 
            data = json.loads(request.body);
            studienfach = data.get('fach');
            semester = data.get('semester');

            lecture_notes = LectureNote.objects.filter(semester_start = semester, subject = studienfach);
            
            number_lecturenotes = len(lecture_notes);

            return JsonResponse({'content': number_lecturenotes}, status=200);
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Ungültige Daten'}, status=400);
        
    return JsonResponse({'error': 'Invalid request'}, status=400);
