from django.http import JsonResponse, HttpResponse
from django.views import View
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from pymongo import MongoClient
from django.template.loader import render_to_string
import bcrypt
import json
import pdfkit
from datetime import datetime
import uuid
from django.shortcuts import redirect

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
            data["role"] = "user"
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
                return JsonResponse({"message": "Fill All  fields"}, status=400)

            user = user_collection.find_one({"email": email})
            if user:
                stored_pass = user.get("password").encode("utf-8")
                if bcrypt.checkpw(password.encode("utf-8"), stored_pass):
                    existing_session = db.SessionHistory.find_one({"email": email})
                    if existing_session:
                        return JsonResponse({
                            "message": "Already logged in on another device",
                            "status": "failed"
                        }, status=409)
                    else:
                        session_key = str(uuid.uuid4())
                        request.session["session_key"] = session_key
                        request.session["role"] = user.get("role", "user")
                        request.session["login_time"] = datetime.now().isoformat()
                        db.SessionHistory.insert_one({
                            "email": email,
                            "session_key": session_key,
                            "role": user.get("role", "user"),
                            "login_time": datetime.now().isoformat()
                        })
                        return JsonResponse({"message": "Login Successfully"}, status=200)
                else:
                    return JsonResponse({"message": "Invalid Password"}, status=401)
            else:
                return JsonResponse({"message": "User Not Found"}, status=404)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)


@method_decorator(csrf_exempt, name="dispatch")
class GetUsersView(View):

    def get(self, request):
        try:
            # print("in try")
            # response_data = {}
            # print("ghfdx",response_data)
            # if verify_session(request, response_data) and response_data.get("code") == 200:
            #     print("in sess")
                users = list(
                    user_collection.find(
                        {}, {"_id": 0, "userName": 1, "email": 1, "phNumber": 1, "role": 1}
                    )
                )
                return JsonResponse(users, safe=False)
            # else:
            #     return JsonResponse({"message": "Invalid Session"}, status=401)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    def post(self, request):
        try:
            response_data = {}
            if verify_session(request, response_data) and response_data.get("code") == 200:
                body = json.loads(request.body)
                for user in body:
                    user_collection.update_one(
                        {"email": user["email"]},
                        {
                            "$set": {
                                "userName": user["userName"],
                                "phNumber": user["phNumber"],
                            }
                        },
                    )
                return JsonResponse({"message": "Users updated successfully"})
            else:
                return JsonResponse({"message": "Invalid Session"}, status=401)
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

def verify_session(http_req, response):
    try:
        session_data = dict(http_req.session.items())
        print("Session Data:", session_data)
        response.update({"message": "Invalid Session", "status": "failed", "code": 401})

        if "session_key" in session_data and session_data["session_key"]:
            user_session_info = db.SessionHistory.find_one(
                {"session_key": session_data["session_key"]}, {"_id": 0}
            )
            if user_session_info:
                response.update({"message": "Valid Session", "status": "success", "code": 200})
                response["session"] = user_session_info
                return True
        return False
    except Exception as e:
        response.update({"message": str(e), "status": "error", "code": 500})
        return False

