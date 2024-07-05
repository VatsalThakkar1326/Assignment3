## Detailed Technical Report
## Acess Website: https://flask-app3-0-u64ezt75sq-uc.a.run.app
## Github Repo: https://github.com/VatsalThakkar1326/Assignment3
### Project Overview

This project aims to develop a student management web application using Flask, SQLAlchemy, and Docker. The application performs CRUD (Create, Read, Update, Delete) operations on student records and is designed to be deployed on Google Cloud Run.

### 1. Flask Application (`app.py`)

The `app.py` file is the core of the application, handling routing, request handling, and interaction with the database.

#### Code Breakdown

1. **Imports and Configuration**
    ```python
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
    ```

    - **Imports**: Import necessary modules for Flask, datetime, os, and the database model.
    - **Flask App Initialization**: Initialize the Flask application and configure it to use an SQLite database.
    - **Database Initialization**: Check if the database file exists and create it if it does not.

2. **Routes**
    ```python
    @app.route('/')
    def index():
        return render_template('index.html')
    ```

    - **GET `/`**: Renders the homepage using the `index.html` template.

    ```python
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
    ```

    - **POST `/students`**: Accepts JSON data to create a new student record. The date of birth is parsed into a date object, and the student is added to the database.

    ```python
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
    ```

    - **GET `/students`**: Retrieves all student records from the database and returns them in JSON format.

    ```python
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
    ```

    - **GET `/students/<student_id>`**: Retrieves a specific student record by student ID. If the student is not found, it returns a 404 error.

    ```python
    @app.route('/search_students', methods=['GET'])
    def search_students():
        first_name = request.args.get('first_name')
        last_name = request.args.get('last_name')
        query = Student.query

        if (first_name):
            query = query.filter(Student.first_name.like(f'%{first_name}%'))
        if (last_name):
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
    ```

    - **GET `/search_students`**: Searches for students based on first and/or last name using query parameters. Supports partial matches.

    ```python
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
    ```

    - **PUT `/students/<student_id>`**: Updates an existing student record with new data. If the student is not found, it returns a 404 error.

    ```python
    @app.route('/students/<student_id>', methods=['DELETE'])
    def delete_student(student_id):
        student = Student.query.filter_by(student_id=student_id).first()
        if student:
            db.session.delete(student)
            db.session.commit()
            return jsonify({'message': 'Student deleted successfully'})
        return jsonify({'message': 'Student not found'}), 404
    ```

    - **DELETE `/students/<student_id>`**: Deletes a student record. If the student is not found, it returns a 404 error.

    ```python
    if __name__ == '__main__':
        port = int(os.environ.get('PORT', 8080))
        app.run(host='0.0.0.0', port=port)
    ```

    - **Main Function**: Reads the `PORT` environment variable and starts the Flask app on the specified port. This is crucial for compatibility with Google Cloud Run.

### 2. Database Models (`models.py`)

The `models.py` file defines the data model for the application using SQLAlchemy.

#### Code Breakdown

```python
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Student(db.Model):
    __tablename__ = 'students'
    student_id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    first_name = db.Column(db.String(50), nullable=False)
    last_name = db.Column(db.String(50), nullable=False)
    dob = db.Column(db.Date, nullable=False)
    amount_due = db.Column(db.Float, nullable=False)

    def __repr__(self):
        return f'<Student {self.student_id}: {self.first_name} {self.last_name}>'

    def to_dict(self):
        return {
            'student_id': self.student_id,
            'first_name': self.first_name,
            'last_name': self.last_name,
            'dob': self.dob.strftime('%Y-%m-%d'),
            'amount_due': self.amount_due
        }
```

- **Student Model**: Defines the `Student` table with columns for student ID, first name, last name, date of birth, and amount due. Includes methods for string representation and converting the model to a dictionary.

### 3. HTML Template (`index.html`)

The `index.html` file provides the user interface for interacting with the student records.

#### Code Breakdown

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Student Management</title>
    <link rel="stylesheet" href="/static/styles.css">
</head>
<body>
    <h1>Student Management</h1>

    <!-- Form to add a new student -->
    <form id="student-form">
        <input type="text" id="first_name" placeholder="First Name" required>
        <input type="text" id="last_name" placeholder="Last Name" required>
        <input type="date" id="dob" required>
        <input type="number" id="amount_due" placeholder="Amount Due" required>
        <button type="submit">Add Student</button>
    </form>

    <!-- Section to display all students -->
    <h2>All Students</h2>
    <table id="students-table">
        <thead>
            <tr>
                <th>Student ID</th>
                <th>First Name</th>
                <th>Last Name</th>
                <th>Date of Birth</th>
                <th>Amount Due</th>
                <th>Actions</th>
            </tr>
        </thead>
        <tbody id="students-list"></tbody>
    </table>

    <!-- Form to search for students -->
    <h2>Search Students</h2>
    <form id="search-form">
        <input type="text" id="search_id" placeholder="Student ID">
        <input type="text" id="search_first_name" placeholder="First Name">
        <input type="text" id="search_last_name" placeholder="Last Name">
        <button type="submit">Search</button>
    </form>
    <table id="search-results-table">
        <thead>
            <tr>
                <th>Student ID</th>
                <th>First Name</th>
                <th>

Last Name</th>
                <th>Date of Birth</th>
                <th>Amount Due</th>
            </tr>
        </thead>
        <tbody id="search-results-list"></tbody>
    </table>

    <script src="/static/script.js"></script>
</body>
</html>
```

- **HTML Structure**: Includes forms for adding and searching for students, and tables for displaying all students and search results.

### 4. CSS Styles (`styles.css`)

The `styles.css` file contains the styling for the HTML template.

#### Code Breakdown

```css
body {
    font-family: Arial, sans-serif;
    margin: 20px;
}

h1, h2 {
    color: #333;
}

form {
    margin-bottom: 20px;
}

input, button {
    padding: 10px;
    margin: 5px 0;
}

table {
    width: 100%;
    border-collapse: collapse;
}

th, td {
    padding: 10px;
    border: 1px solid #ddd;
}

th {
    background-color: #f4f4f4;
}

button {
    background-color: #4CAF50;
    color: white;
    border: none;
    cursor: pointer;
}

button:hover {
    background-color: #45a049;
}
```

- **CSS Styling**: Provides basic styles for the body, headings, forms, inputs, buttons, and tables to ensure a clean and user-friendly interface.

### 5. Docker Configuration (`Dockerfile`)

The Dockerfile defines the container configuration for deploying the Flask application.

#### Code Breakdown

```dockerfile
# Use the official Python image from the Docker Hub
FROM python:3.9-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Make port 8080 available to the world outside this container
EXPOSE 8080

# Define environment variable
ENV FLASK_APP=app.py
ENV FLASK_ENV=production

# Run the app using gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "app:app"]
```

- **Base Image**: Uses a slim Python image.
- **Working Directory**: Sets the working directory to `/app`.
- **Copy Files**: Copies the current directory contents into the container.
- **Install Dependencies**: Installs Python packages specified in `requirements.txt`.
- **Expose Port**: Exposes port 8080.
- **Environment Variables**: Sets environment variables for Flask.
- **Start Command**: Uses Gunicorn to run the Flask app, binding it to port 8080.

### 6. Dependency Management (`requirements.txt`)

The `requirements.txt` file lists all the Python packages needed to run the application.

#### Dependencies

```
Flask==2.0.1
Flask-SQLAlchemy==2.5.1
gunicorn==20.1.0
```

- **Flask**: The web framework used to build the application.
- **Flask-SQLAlchemy**: The ORM used for database interactions.
- **Gunicorn**: The WSGI HTTP server used to serve the Flask application.

### 7. Google Cloud Deployment

The application is deployed to Google Cloud Run, a serverless platform that automatically scales the application based on traffic.

#### Deployment Steps

1. **Build the Docker Image**: Build the Docker image using the command:
    ```sh
    docker build -t gcr.io/[PROJECT_ID]/[IMAGE_NAME]:[TAG] .
    ```

2. **Push the Docker Image**: Push the Docker image to Google Container Registry:
    ```sh
    docker push gcr.io/[PROJECT_ID]/[IMAGE_NAME]:[TAG]
    ```

3. **Deploy to Cloud Run**: Deploy the image to Google Cloud Run:
    ```sh
    gcloud run deploy [SERVICE_NAME] --image gcr.io/[PROJECT_ID]/[IMAGE_NAME]:[TAG] --platform managed --region [REGION] --allow-unauthenticated --port 8080
    ```

#### Debugging

- Ensure the `PORT` environment variable is correctly set in the Cloud Run service.
- Check Cloud Run logs for errors related to port binding or environment configuration.

### Conclusion

This web application provides a solution for managing student records with a focus on scalability and ease of deployment. By leveraging Flask for backend development, SQLAlchemy for ORM, Docker for containerization, and Google Cloud Run for deployment, and efficient approach to web application development.