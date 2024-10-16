from django.http import JsonResponse
from core.models import LectureNote
from django.views.decorators.csrf import csrf_protect
import json

@csrf_protect
def products(request, model):
    if request.method == 'POST':
        try: 
            ean = '';
            data = json.loads(request.body);
            product = data.get('product');
            if (product == 'S') or (product == 'P') or (product == 's') or (product == 'p'): 
                teil = data.get('teil');
                studienfach = data.get('studienfach');
                semester = data.get('semester');

                lecture_notes = LectureNote.objects.filter(semester_start = semester, subject = studienfach);
                number_lecturenotes = len(lecture_notes);

                #Product to EAN
                match(product):
                    case('S'): ean += '0';
                    case('P'): ean += '1';

                #Fach to EAN
                match(studienfach):
                    case('I'): ean += '0';
                    case('M'): ean += '1';
                    case('P'): ean += '2';
                    case('C'): ean += '3';

                #Semester to EAN
                match(semester[0]):
                    case('W'): ean += '1'
                    case('S'): ean += '2'
                ean += semester[3]
                ean += semester[4]

                #Number to EAN
                if number_lecturenotes < 10 :
                    ean += '0';
                ean += str(number_lecturenotes); 
            
                #Teil to EAN
                ean += teil

            elif (product == 'K') or (product == 'D') or (product == 'k') or (product == 'd'): 
                content = data.get('content');
                qpilot = data.get('qpilot')

                #Product to EAN:
                match(product):
                    case('D'): ean += '9';
                    case('K'): ean += '7';
                
                #Qpilot to EAN
                if(qpilot):
                    ean += '0'
                else:
                    ean += '3'

                #Ending to EAN
                for i in range (0, 4-len(content)):
                    ean += '0';
                ean += str(content);
            
            return JsonResponse({'content': ean}, status=200);
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Ungültige Daten'}, status=400);
        
    return JsonResponse({'error': 'Invalid request'}, status=400);
