import cv2
import numpy as np
import os
import base64
from datetime import datetime, timedelta
from flask import Flask, render_template, Response, request, jsonify
from sqlalchemy import create_engine, Column, Integer, String, DateTime, BLOB
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config

# Создание приложения Flask
app = Flask(__name__)
app.config.from_object(config[os.getenv('FLASK_ENV', 'production')])

Base = declarative_base()

# Database setup
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
Session = sessionmaker(bind=engine)
session = Session()

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String(100))
    face_image = Column(BLOB)  # Store the actual image instead of encoding
    created_at = Column(DateTime, default=datetime.now)

class Attendance(Base):
    __tablename__ = 'attendance'
    id = Column(Integer, primary_key=True)
    student_id = Column(Integer)
    date = Column(DateTime, default=datetime.now)

Base.metadata.create_all(engine)

# Load the cascade classifier
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')

# Dictionary to store last attendance time for each student
last_attendance = {}

def compare_faces(face1, face2, threshold=0.7):
    # Convert images to grayscale
    gray1 = cv2.cvtColor(face1, cv2.COLOR_BGR2GRAY)
    gray2 = cv2.cvtColor(face2, cv2.COLOR_BGR2GRAY)
    
    # Resize images to same size
    gray1 = cv2.resize(gray1, (100, 100))
    gray2 = cv2.resize(gray2, (100, 100))
    
    # Calculate similarity using correlation coefficient
    correlation = cv2.matchTemplate(gray1, gray2, cv2.TM_CCOEFF_NORMED)[0][0]
    return correlation > threshold

def process_base64_image(base64_string):
    # Remove header if present
    if 'data:image/' in base64_string:
        base64_string = base64_string.split(',')[1]
    
    # Decode base64 string to bytes
    image_bytes = base64.b64decode(base64_string)
    
    # Convert bytes to numpy array
    nparr = np.frombuffer(image_bytes, np.uint8)
    
    # Decode image
    image = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
    return image

def generate_frames():
    print("Attempting to open camera...")
    
    # Try different camera indices
    for camera_index in [0, 1]:
        print(f"Trying camera index {camera_index}...")
        video_capture = cv2.VideoCapture(camera_index)
        
        if video_capture.isOpened():
            print(f"Camera opened successfully with index {camera_index}!")
            break
    else:
        print("Failed to open camera on any index!")
        return
    
    while True:
        ret, frame = video_capture.read()
        if not ret:
            print("Failed to read frame!")
            break
            
        # Convert to grayscale
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Detect faces
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        # For each detected face
        for (x, y, w, h) in faces:
            face_img = frame[y:y+h, x:x+w]
            
            # Try to recognize the face
            students = session.query(Student).all()
            recognized = False
            
            for student in students:
                # Convert stored image back from BLOB
                nparr = np.frombuffer(student.face_image, np.uint8)
                stored_face = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
                
                if compare_faces(face_img, stored_face):
                    # Check if we should record attendance (not more often than every 5 minutes)
                    current_time = datetime.now()
                    if student.id not in last_attendance or \
                       (current_time - last_attendance[student.id]) > timedelta(minutes=5):
                        # Record attendance
                        attendance = Attendance(student_id=student.id)
                        session.add(attendance)
                        session.commit()
                        last_attendance[student.id] = current_time
                    
                    # Draw green rectangle and name
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                    cv2.putText(frame, student.name, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
                    recognized = True
                    break
            
            if not recognized:
                # Draw red rectangle for unknown face
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 0, 255), 2)
                cv2.putText(frame, "Unknown", (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 0, 255), 2)
        
        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/video_feed')
def video_feed():
    return Response(generate_frames(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/register', methods=['POST'])
def register_student():
    try:
        name = request.form.get('name')
        image_data = request.form.get('image')
        
        if not name:
            return jsonify({'error': 'Необходимо ввести имя студента'}), 400
        
        if not image_data:
            return jsonify({'error': 'Изображение не получено'}), 400
        
        # Обработка изображения
        frame = process_base64_image(image_data)
        if frame is None:
            return jsonify({'error': 'Не удалось обработать изображение'}), 400
        
        # Конвертация в оттенки серого
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        # Обнаружение лица
        faces = face_cascade.detectMultiScale(gray, 1.1, 4)
        
        if len(faces) == 0:
            return jsonify({'error': 'Лицо не обнаружено. Убедитесь, что лицо находится в кадре и есть достаточное освещение.'}), 400
        
        # Берем первое найденное лицо
        x, y, w, h = faces[0]
        face_img = frame[y:y+h, x:x+w]
        
        # Сохраняем изображение в формате JPEG
        _, img_encoded = cv2.imencode('.jpg', face_img)
        
        # Проверка на существующего студента
        existing_student = session.query(Student).filter_by(name=name).first()
        if existing_student:
            return jsonify({'error': 'Студент с таким именем уже зарегистрирован'}), 400
        
        # Сохранение в базу данных
        student = Student(name=name, face_image=img_encoded.tobytes())
        session.add(student)
        try:
            session.commit()
        except Exception as e:
            session.rollback()
            return jsonify({'error': 'Ошибка при сохранении данных. Попробуйте еще раз.'}), 500
        
        return jsonify({'message': 'Студент успешно зарегистрирован'})
        
    except Exception as e:
        return jsonify({'error': f'Произошла ошибка: {str(e)}'}), 500

@app.route('/attendance')
def get_attendance():
    attendance = session.query(Attendance).all()
    result = []
    for record in attendance:
        student = session.query(Student).filter_by(id=record.student_id).first()
        if student:  # Check if student exists
            result.append({
                'student_name': student.name,
                'date': record.date.strftime('%Y-%m-%d %H:%M:%S')
            })
    return jsonify(result)

@app.route('/students')
def get_students():
    students = session.query(Student).all()
    result = []
    for student in students:
        result.append({
            'id': student.id,
            'name': student.name,
            'created_at': student.created_at.strftime('%Y-%m-%d %H:%M:%S')
        })
    return jsonify(result)

@app.route('/students/<int:student_id>', methods=['DELETE'])
def delete_student(student_id):
    try:
        student = session.query(Student).filter_by(id=student_id).first()
        if not student:
            return jsonify({'error': 'Студент не найден'}), 404
        
        # Удаляем связанные записи посещаемости
        session.query(Attendance).filter_by(student_id=student_id).delete()
        session.delete(student)
        session.commit()
        return jsonify({'message': 'Студент успешно удален'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': f'Произошла ошибка: {str(e)}'}), 500

@app.route('/students/<int:student_id>', methods=['PUT'])
def update_student(student_id):
    try:
        student = session.query(Student).filter_by(id=student_id).first()
        if not student:
            return jsonify({'error': 'Студент не найден'}), 404
        
        name = request.json.get('name')
        if not name:
            return jsonify({'error': 'Необходимо указать имя'}), 400
        
        # Проверка на существующее имя
        existing = session.query(Student).filter(Student.name == name, Student.id != student_id).first()
        if existing:
            return jsonify({'error': 'Студент с таким именем уже существует'}), 400
        
        student.name = name
        session.commit()
        return jsonify({'message': 'Данные студента обновлены'})
    except Exception as e:
        session.rollback()
        return jsonify({'error': f'Произошла ошибка: {str(e)}'}), 500

@app.errorhandler(404)
def not_found_error(error):
    return jsonify({'error': 'Страница не найдена'}), 404

@app.errorhandler(500)
def internal_error(error):
    session.rollback()
    return jsonify({'error': 'Внутренняя ошибка сервера'}), 500

if __name__ == '__main__':
    # Создание директории для логов
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Запуск сервера
    print("Сервер запущен и доступен по следующим адресам:")
    print("Локальный доступ: http://localhost:5000")
    print("Внешний доступ: http://[ваш_IP]:5000")
    
    if app.config['DEBUG']:
        app.run(debug=True, host='0.0.0.0', port=5000, threaded=True)
    else:
        app.run(host='0.0.0.0', port=5000, threaded=True) 