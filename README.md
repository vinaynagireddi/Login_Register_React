🔐 React + Django + MongoDB Authentication App
This is a full-stack web application featuring user registration, login, and data visibility after authentication. It uses a React frontend and a Django backend, with MongoDB as the database. User data is securely stored, and the app uses session-based or token-based authentication logic.

🚀 Features
✅ User registration with real-time validation

🔐 Login system with secure authentication

📄 Post-login protected dashboard (data visibility page)

⚛️ React frontend using Axios, React Router

🌐 Backend with Django REST API

💾 MongoDB integration via djongo or mongoengine

🔄 AJAX-style communication using Axios

🛠️ Tech Stack
Layer	Tech
Frontend	React, JavaScript, Axios, React Router
Backend	Django (with Django REST Framework)
Database	MongoDB
Styling	CSS3, optionally Bootstrap or Tailwind

Frontend (React):

Form components collect user info.

Axios is used to communicate with Django backend (register, login).

React Router manages page transitions (e.g., /login, /dashboard).

Dashboard is protected – accessible only after login.

Backend (Django):

Handles user creation, authentication, and session/token management.

Uses MongoDB to store user data via mongoengine or djongo.

Auth Flow:

User registers → data sent via Axios to Django → MongoDB stores it.

On login → credentials validated → user session/token created.

If authenticated → redirected to protected Dashboard.

🧾 Project Description
This project was created to demonstrate a full-stack authentication system using React and Django with a NoSQL backend. It’s a scalable starting point for building user portals, admin dashboards, or SaaS products.

👨‍💻 Developer Notes
Created custom API endpoints in Django to interact with the frontend.

Used React functional components with Hooks (useState, useEffect).

Built an Axios wrapper for consistent API requests and error handling.

Managed session-based or token-based access (e.g., JWT if needed).

📈 Future Enhancements
Add email verification on registration.

JWT-based token auth with refresh logic.

Add role-based access control (Admin/User).

Dashboard enhancements like charts, user profiles, etc.

Dockerized deployment and CI/CD integration.
