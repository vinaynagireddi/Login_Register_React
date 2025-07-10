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
                return JsonResponse(
                    {"message": "Please fill in all fields", "status": "failed"},
                    status=400,
                )

            user = user_collection.find_one({"email": email})
            if not user:
                return JsonResponse(
                    {"message": "User not found", "status": "failed"}, status=404
                )

            stored_pass = user.get("password")
            if not stored_pass:
                return JsonResponse(
                    {"message": "Password not set for this user", "status": "failed"},
                    status=500,
                )

            if bcrypt.checkpw(password.encode("utf-8"), stored_pass.encode("utf-8")):
                existing_session = db.SessionHistory.find_one({"email": email})
                if existing_session:
                    return JsonResponse(
                        {
                            "message": "Already logged in on another device",
                            "status": "failed",
                        },
                        status=409,
                    )
                session_key = str(uuid.uuid4())
                request.session["sessionKey"] = session_key
                request.session["role"] = user.get("role", "user")
                request.session["login_time"] = datetime.now().isoformat()

                db.SessionHistory.insert_one(
                    {
                        "email": email,
                        "sessionKey": session_key,
                        "role": user.get("role", "user"),
                        "loginTime": datetime.now(),
                        "lastActivityOn": datetime.now(),
                    }
                )
                return JsonResponse(
                    {
                        "message": "Login Successful",
                        "status": "success",
                        "sessionKey": session_key,
                        "role": user.get("role", "user"),
                    },
                    status=200,
                )
            else:
                return JsonResponse(
                    {"message": "Invalid password", "status": "failed"}, status=401
                )
        except json.JSONDecodeError:
            return JsonResponse(
                {"message": "Invalid JSON", "status": "failed"}, status=400
            )
        except Exception as e:
            return JsonResponse(
                {"message": f"Server error: {str(e)}", "status": "failed"}, status=500
            )


@method_decorator(csrf_exempt, name="dispatch")
class GetUsersView(View):
    def get(self, request):
        response = {
            "message": "",
            "code": 400,
            "callback": __class__.__name__,
            "status": "failed",
        }

        try:
            session_check = verifySession(request, response.copy())
            if session_check["code"] != 200:
                return JsonResponse(session_check, status=session_check["code"])

            users = list(
                user_collection.find(
                    {}, {"_id": 0, "userName": 1, "email": 1, "phNumber": 1, "role": 1}
                )
            )
            return JsonResponse(users, safe=False)

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

    def post(self, request):
        response = {
            "message": "",
            "code": 400,
            "callback": __class__.__name__,
            "status": "failed",
        }

        try:
            session_check = verifySession(request, response.copy())
            if session_check["code"] != 200:
                return JsonResponse(session_check, status=session_check["code"])

            if session_check["userDetails"].get("role") != "Admin":
                return JsonResponse(
                    {
                        "message": "User not authorized to change details",
                        "status": "failed",
                        "code": 403,
                    },
                    status=403,
                )

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
            return JsonResponse({"message": "Users updated successfully"}, status=200)

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


def verifySession(http_req, response):
    session_data = dict(http_req.session.items())
    response.update({"message": "Invalid Session", "status": "failed", "code": 401})

    if "sessionKey" in session_data and session_data["sessionKey"]:
        session_key = session_data["sessionKey"]
        userSessionInfo = db.SessionHistory.find_one(
            {"sessionKey": session_key}, {"_id": 0}
        )

        if userSessionInfo:
            recent_activity = datetime.now()
            last_activity = userSessionInfo.get("lastActivityOn")
            if last_activity:
                delta_time = recent_activity - last_activity
                delta_minutes = delta_time.total_seconds() / 60

                # Check session timeout (example: 30 minutes)
                if delta_minutes <= 30:
                    db.SessionHistory.update_one(
                        {"sessionKey": session_key},
                        {"$set": {"lastActivityOn": recent_activity}},
                    )

                    response.update(
                        {
                            "message": "Session Verification Successful",
                            "userDetails": userSessionInfo,
                            "code": 200,
                            "status": "success",
                        }
                    )
                else:
                    sessionKeyDeleteCount = db.SessionHistory.delete_one(
                        {"sessionKey": session_key}
                    ).deleted_count
                    response.update(
                        {
                            "message": "Session Expired",
                            "code": 401,
                            "status": "failed",
                            "sessionKeyDeleteCount": sessionKeyDeleteCount,
                        }
                    )
            else:
                response.update(
                    {
                        "message": "Session data incomplete: 'lastActivityOn' missing",
                        "code": 500,
                    }
                )
        else:
            response.update({"message": "Session Key Not Found", "code": 401})
    else:
        response.update(
            {
                "message": "Invalid Session Data or Session Key not found",
                "code": 401,
                "status": "failed",
            }
        )

    return response


@method_decorator(csrf_exempt, name="dispatch")
class Logout(View):
    def post(self, request):
        try:
            session_key = request.session.get("session_key")
            if session_key:
                db.SessionHistory.delete_one({"session_key": session_key})
                request.session.flush()
                return JsonResponse({"message": "Logged out successfully"}, status=200)
            else:
                return JsonResponse({"message": "No active session"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
