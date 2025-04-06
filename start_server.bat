@echo off
cd /d D:\face_attendance
call .\venv_new\Scripts\activate
echo Server starting...
echo Local access: http://localhost:5000
echo Network access: http://192.168.0.110:5000
python app.py 