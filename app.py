from flask import Flask, request, jsonify, render_template
from datetime import datetime
import os
from models import db, Student

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///students.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Ensure the database exists
if not os.path.exists('students.db'):
    with app.app_context():
        db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/students', methods=['POST'])
def add_student():
    data = request.json
    new_student = Student(
        first_name=data['first_name'],
        last_name=data['last_name'],
        dob=datetime.strptime(data['dob'], '%Y-%m-%d').date(),
        amount_due=data['amount_due']
    )
    db.session.add(new_student)
    db.session.commit()
    return jsonify({'message': 'Student added successfully'}), 201

@app.route('/students', methods=['GET'])
def get_students():
    students = Student.query.all()
    return jsonify([{
        'student_id': student.student_id,
        'first_name': student.first_name,
        'last_name': student.last_name,
        'dob': student.dob.strftime('%Y-%m-%d'),
        'amount_due': student.amount_due
    } for student in students])

@app.route('/students/<student_id>', methods=['GET'])
def get_student(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    if student:
        return jsonify({
            'student_id': student.student_id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'dob': student.dob.strftime('%Y-%m-%d'),
            'amount_due': student.amount_due
        })
    return jsonify({'message': 'Student not found'}), 404

@app.route('/search_students', methods=['GET'])
def search_students():
    first_name = request.args.get('first_name')
    last_name = request.args.get('last_name')
    query = Student.query

    if first_name:
        query = query.filter(Student.first_name.like(f'%{first_name}%'))
    if last_name:
        query = query.filter(Student.last_name.like(f'%{last_name}%'))

    students = query.all()
    if students:
        return jsonify([{
            'student_id': student.student_id,
            'first_name': student.first_name,
            'last_name': student.last_name,
            'dob': student.dob.strftime('%Y-%m-%d'),
            'amount_due': student.amount_due
        } for student in students])
    return jsonify({'message': 'No students found'}), 404


@app.route('/students/<student_id>', methods=['PUT'])
def update_student(student_id):
    data = request.json
    student = Student.query.filter_by(student_id=student_id).first()
    if student:
        student.first_name = data['first_name']
        student.last_name = data['last_name']
        student.dob = datetime.strptime(data['dob'], '%Y-%m-%d').date()
        student.amount_due = data['amount_due']
        db.session.commit()
        return jsonify({'message': 'Student updated successfully'})
    return jsonify({'message': 'Student not found'}), 404

@app.route('/students/<student_id>', methods=['DELETE'])
def delete_student(student_id):
    student = Student.query.filter_by(student_id=student_id).first()
    if student:
        db.session.delete(student)
        db.session.commit()
        return jsonify({'message': 'Student deleted successfully'})
    return jsonify({'message': 'Student not found'}), 404


if __name__ == '__main__':
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
