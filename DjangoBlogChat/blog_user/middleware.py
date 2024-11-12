# from django.http import JsonResponse
# from django.db import DatabaseError
# import requests

# class CustomErrorMiddleware:
#     def __init__(self, get_response):
#         self.get_response = get_response

#     def __call__(self, request):
#         response = self.get_response(request)
#         if response.status_code >= 400:
#             print("Произошла ошибка!")
#         return response