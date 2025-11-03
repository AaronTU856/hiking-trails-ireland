from django.http import JsonResponse
import json
import os
from django.shortcuts import render

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def add_location_api(request):
    return JsonResponse({"status": "ok", "message": "add_location_api placeholder"})

def api_status(request):
    return JsonResponse({"status": "ok"})

def environment_test(request):
    return JsonResponse({"environment": "working"})

def intersect_test(request):
    """Return static intersection data (safe fallback)."""
    try:
        file_path = os.path.join(os.path.dirname(__file__), "intersect_test.json")
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                data = json.load(f)
        else:
            data = {
                "trail_1": "Clara Esker Loop",
                "trail_2": "Clara Erry Way Loop",
                "intersection": {
                    "type": "Point",
                    "coordinates": [-7.586203962517108, 53.321348451041224]
                }
            }
        return JsonResponse(data)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
