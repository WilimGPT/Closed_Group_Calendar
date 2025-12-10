from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
import json
import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, 'data')


def get_language_file(language):
    return os.path.join(DATA_DIR, f"{language}.json")


@csrf_exempt
@require_http_methods(["GET", "POST"])
def language_data(request, language):
    file_path = get_language_file(language)

    if not os.path.exists(file_path):
        return JsonResponse({"error": "Language not found"}, status=404)

    if request.method == "GET":
        with open(file_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return JsonResponse(data, safe=False)

    if request.method == "POST":
        try:
            body = json.loads(request.body.decode("utf-8"))
        except json.JSONDecodeError:
            return JsonResponse({"error": "Invalid JSON"}, status=400)

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(body, f, indent=2)

        return JsonResponse({"status": "saved"})
