from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from pymongo import MongoClient
from django.template.loader import render_to_string
import bcrypt
import json
import pdfkit

client = MongoClient("mongodb://localhost:27017/")
db = client["offDatabase"]
user_collection = db["reactcoll"]
@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)

            if user_collection.find_one({"userName": data["userName"]}):
                return JsonResponse({"message": "user Name already existed"})
            if user_collection.find_one({"phNumber": data["phNumber"]}):
                return JsonResponse({"message": "phNumber already existed"})
            if user_collection.find_one({"email": data["email"]}):
                return JsonResponse({"message": "email already existed"})

            hashed_pass = bcrypt.hashpw(
                data["password"].encode("utf-8"), bcrypt.gensalt()
            )
            data["password"] = hashed_pass.decode("utf-8")

            user_collection.insert_one(data)
            return JsonResponse(
                {"message": "User registered successfully!"}, status=201
            )
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class LoginView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            email = data.get("email")
            password = data.get("password")

            if not email or not password:
                return JsonResponse({"message": "Fill the fields"})

            user = user_collection.find_one({"email": email})
            if user:
                stored_pass = user.get("password").encode("utf-8")
                if bcrypt.checkpw(password.encode("utf-8"), stored_pass):
                    return JsonResponse({"message": "Login Successfully"})
                else:
                    return JsonResponse({"message": "Invalid Password"})
            else:
                return JsonResponse({"message": "User Not Found"})
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class GetUsersView(View):

    def get(self, request):
        try:
            users = list(
                user_collection.find(
                    {}, {"_id": 0, "userName": 1, "email": 1, "phNumber": 1}
                )
            )
            return JsonResponse(users, safe=False)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    def post(self, request):
        try:
            body = json.loads(request.body)
            for user in body:
                user_collection.update_one(
                    {"email": user["email"]},  # use email as unique identifier
                    {
                        "$set": {
                            "userName": user["userName"],
                            "phNumber": user["phNumber"],
                        }
                    },
                )
            return JsonResponse({"message": "Users updated successfully"})
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


class DownloadUsersPDFView(View):
    def get(self, request):
        try:
            users = list(
                user_collection.find(
                    {}, {"_id": 0, "userName": 1, "email": 1, "phNumber": 1}
                )
            )
            html = render_to_string("users_template.html", {"users": users})
            pdf = pdfkit.from_string(html, False)
            return HttpResponse(pdf, content_type="application/pdf")
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
