from flask import Flask, request, jsonify, make_response
from pymongo import MongoClient
import face_recognition
import numpy as np
import base64
import cv2
import zlib
import logging
from datetime import datetime
from bson import Binary



# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# MongoDB connection
try:
    client = MongoClient('mongodb://localhost:27017/')
    db = client['face_recognition_db']
    students_collection = db['students']
    attendance_collection = db['attendance']

    # Create indexes
    students_collection.create_index('student_id', unique=True)
    attendance_collection.create_index([('student_id', 1), ('scan_time', 1)])
    
    # Test connection
    client.server_info()
    logger.info("Successfully connected to MongoDB")
except Exception as e:
    logger.error(f"Failed to connect to MongoDB: {str(e)}")
    raise

def add_cors_headers(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    return response

@app.route('/', defaults={'path': ''}, methods=['OPTIONS'])
@app.route('/<path:path>', methods=['OPTIONS'])
def handle_options(path):
    response = make_response()
    return add_cors_headers(response)

def compress_encoding(face_encoding):
    """Compress face encoding using zlib"""
    return Binary(zlib.compress(face_encoding.tobytes()))

def decompress_encoding(compressed_data):
    """Decompress face encoding and convert to numpy array"""
    decompressed_data = zlib.decompress(compressed_data)
    return np.frombuffer(decompressed_data)

# Add a test endpoint
@app.route('/api/test', methods=['GET'])
def test_connection():
    try:
        # Test MongoDB connection
        students_count = students_collection.count_documents({})
        attendance_count = attendance_collection.count_documents({})
        
        response = jsonify({
            'status': 'success',
            'message': 'API is working',
            'database': {
                'connected': True,
                'students_count': students_count,
                'attendance_count': attendance_count
            }
        })
        return add_cors_headers(response)
    except Exception as e:
        logger.error(f"Test endpoint error: {str(e)}")
        response = jsonify({
            'status': 'error',
            'message': str(e)
        })
        return add_cors_headers(response), 500

@app.route('/api/scan', methods=['GET', 'POST'])
def scan_face():
    logger.info(f"Received {request.method} request to /api/scan")
    
    if request.method == 'GET':
        return add_cors_headers(jsonify({
            'error': 'This endpoint only accepts POST requests',
            'message': 'Please send a POST request with image data'
        })), 405
    
    try:
        if not request.is_json:
            logger.error("Request does not contain JSON data")
            return add_cors_headers(jsonify({'error': 'Request must be JSON'})), 400
        
        image_data = request.json.get('image')
        if not image_data:
            logger.error("No image data in request")
            return add_cors_headers(jsonify({'error': 'No image data provided'})), 400
        
        # Process image...
        
    except Exception as e:
        logger.error(f"Unexpected error in scan_face: {str(e)} - Request data: {request.json}")
        return add_cors_headers(jsonify({'error': 'An unexpected error occurred'})), 500


@app.route('/api/register', methods=['GET', 'POST'])
def register_student():
    # Log the request
    logger.info(f"Received {request.method} request to /api/register")
    
    # Handle GET request
    if request.method == 'GET':
        response = jsonify({
            'error': 'This endpoint only accepts POST requests',
            'message': 'Please send a POST request with student data and image'
        })
        return add_cors_headers(response), 405
    
    try:
        if not request.is_json:
            logger.error("Request does not contain JSON data")
            response = jsonify({'error': 'Request must be JSON'})
            return add_cors_headers(response), 400
            
        data = request.json
        required_fields = ['image', 'studentId', 'firstName', 'lastName']
        for field in required_fields:
            if field not in data:
                logger.error(f"Missing required field: {field}")
                response = jsonify({'error': f'Missing required field: {field}'})
                return add_cors_headers(response), 400
        
        image_data = data['image']
        student_id = data['studentId']
        first_name = data['firstName']
        last_name = data['lastName']
        
        # Convert base64 image to numpy array
        try:
            image_bytes = base64.b64decode(image_data.split(',')[1])
        except Exception as e:
            logger.error(f"Failed to decode base64 image: {str(e)}")
            response = jsonify({'error': 'Invalid image data'})
            return add_cors_headers(response), 400
            
        nparr = np.frombuffer(image_bytes, np.uint8)
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        
        # Get face encoding
        face_locations = face_recognition.face_locations(img)
        if not face_locations:
            logger.warning("No face detected in registration image")
            response = jsonify({'error': 'No face detected'})
            return add_cors_headers(response), 400
            
        face_encoding = face_recognition.face_encodings(img, face_locations)[0]
        
        # Compress and store face encoding
        compressed_encoding = compress_encoding(face_encoding)
        
        # Store in database
        students_collection.insert_one({
            'student_id': student_id,
            'first_name': first_name,
            'last_name': last_name,
            'face_encoding': compressed_encoding,
            'created_at': datetime.now()
        })
        
        logger.info(f"Successfully registered student: {student_id}")
        response = jsonify({
            'message': 'Student registered successfully',
            'student_id': student_id
        })
        return add_cors_headers(response)
        
    except Exception as e:
        if 'duplicate key error' in str(e).lower():
            logger.error(f"Duplicate student ID: {student_id}")
            response = jsonify({'error': 'Student ID already exists'})
            return add_cors_headers(response), 400
        logger.error(f"Error in register_student: {str(e)}")
        response = jsonify({'error': str(e)})
        return add_cors_headers(response), 500

@app.errorhandler(404)
def not_found(error):
    response = jsonify({
        'error': 'Not found',
        'message': 'The requested URL was not found on the server'
    })
    return add_cors_headers(response), 404

@app.errorhandler(405)
def method_not_allowed(error):
    response = jsonify({
        'error': 'Method not allowed',
        'message': f'The {request.method} method is not allowed for this endpoint'
    })
    return add_cors_headers(response), 405

if __name__ == '__main__':
    logger.info("Starting Flask application...")
    app.run(debug=True, port=5000)