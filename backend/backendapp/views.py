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
import backend.settings as sts

def now_str():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

@method_decorator(csrf_exempt, name="dispatch")
class RegisterView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
            if sts.dbcursor.reactcoll.find_one({"userName": data["userName"]}):
                return JsonResponse({"message": "user Name already existed"})
            if sts.dbcursor.reactcoll.find_one({"phNumber": data["phNumber"]}):
                return JsonResponse({"message": "phNumber already existed"})
            if sts.dbcursor.reactcoll.find_one({"email": data["email"]}):
                return JsonResponse({"message": "email already existed"})

            hashed_pass = bcrypt.hashpw(
                data["password"].encode("utf-8"), bcrypt.gensalt()
            )
            data["password"] = hashed_pass.decode("utf-8")
            data["role"] = "user"
            sts.dbcursor.reactcoll.insert_one(data)
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

            user = sts.dbcursor.reactcoll.find_one({"email": email})
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
                existing_session = sts.dbcursor.SessionHistory.find_one({"email": email})
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
                sts.dbcursor.SessionHistory.insert_one(
                    {
                        "email": email,
                        "sessionKey": session_key,
                        "role": user.get("role", "user"),
                        "loginTime": now_str(),
                        "lastActivityOn": now_str(),
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
                sts.dbcursor.reactcoll.find(
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

            oldData = json.loads(request.body)
            for user in oldData:
                sts.dbcursor.reactcoll.update_one(
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
                sts.dbcursor.reactcoll.find(
                    {}, {"_id": 0, "userName": 1, "email": 1, "phNumber": 1}
                )
            )
            html = render_to_string("users_template.html", {"users": users})
            path_wkhtmltopdf = r"C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe"
            config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)

            pdf = pdfkit.from_string(html, False, configuration=config)

            response = HttpResponse(pdf, content_type="application/pdf")
            response["Content-Disposition"] = 'attachment; filename="users.pdf"'
            return response

        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)

def verifySession(http_req, response):
    session_data = dict(http_req.session.items())
    session_key = session_data.get("sessionKey")

    if not session_key:
        session_key = http_req.headers.get("X-Session-Key")
    response.update({"message": "Invalid Session", "status": "failed", "code": 401})

    if session_key:
        userSessionInfo = sts.dbcursor.SessionHistory.find_one({"sessionKey": session_key}, {"_id": 0})

        if userSessionInfo:
            try:
                last_activity = userSessionInfo.get("lastActivityOn")
                if isinstance(last_activity, str):
                    last_activity = datetime.strptime(last_activity, "%Y-%m-%d %H:%M:%S")

                recent_activity = datetime.now()
                delta_minutes = (recent_activity - last_activity).total_seconds() / 60

                if delta_minutes <= 30:
                    sts.dbcursor.SessionHistory.update_one(
                        {"sessionKey": session_key},
                        {"$set": {"lastActivityOn": now_str()}},
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
                    count = sts.dbcursor.SessionHistory.delete_one({"sessionKey": session_key}).deleted_count
                    response.update(
                        {
                            "message": "Session Expired",
                            "code": 401,
                            "status": "failed",
                            "sessionKeyDeleteCount": count,
                        }
                    )
            except Exception as e:
                response.update(
                    {
                        "message": f"Session parse error: {str(e)}",
                        "code": 500,
                        "status": "failed",
                    }
                )
        else:
            response.update({"message": "Session Key Not Found", "code": 401})

    return response

@method_decorator(csrf_exempt, name="dispatch")
class Logout(View):
    def post(self, request):
        try:
            session_key = request.headers.get("X-Session-Key")
            if session_key:
                sts.dbcursor.SessionHistory.delete_one({"sessionKey": session_key})
                request.session.flush()
                return JsonResponse({"message": "Logged out successfully"}, status=200)
            else:
                return JsonResponse({"message": "No active session"}, status=400)
        except Exception as e:
            return JsonResponse({"message": str(e)}, status=500)
