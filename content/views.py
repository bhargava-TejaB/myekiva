from django.http import JsonResponse
from utils import open_ai_content

def generate_content_view(request):
    topic = request.GET.get('topic', None)
    if not topic:
        return JsonResponse({'error': 'Topic is required'}, status=400)

    result = open_ai_content.generate_education_content(topic)
    return JsonResponse(result)
