from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import or_, func
from app import db
from app.models import Student, User, AuditLog
from datetime import datetime
import os

students_bp = Blueprint('students', __name__)

@students_bp.route('', methods=['GET'])
@jwt_required()
def get_students():
    """Get all students with optional filtering and pagination"""
    try:
        # Get query parameters
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 50))
        search = request.args.get('search', '').strip()
        program = request.args.get('program', '').strip()
        status = request.args.get('status', '').strip()

        # Build query
        query = Student.query

        if search:
            search_filter = f"%{search}%"
            query = query.filter(
                or_(
                    Student.student_id.ilike(search_filter),
                    Student.name.ilike(search_filter),
                    Student.email.ilike(search_filter)
                )
            )

        if program:
            query = query.filter(Student.program == program)

        if status:
            query = query.filter(Student.status == status)

        # Get total count
        total = query.count()

        # Apply pagination
        students = query.order_by(Student.name)\
                       .offset((page - 1) * per_page)\
                       .limit(per_page)\
                       .all()

        return jsonify({
            'students': [student.to_dict() for student in students],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': total,
                'pages': (total + per_page - 1) // per_page
            }
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@students_bp.route('/<student_id>', methods=['GET'])
@jwt_required()
def get_student(student_id):
    """Get a specific student by student_id"""
    try:
        student = Student.query.filter_by(student_id=student_id).first()

        if not student:
            return jsonify({'error': 'Student not found'}), 404

        return jsonify({'student': student.to_dict()}), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@students_bp.route('', methods=['POST'])
@jwt_required()
def create_student():
    """Create a new student"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()

        # Validate required fields
        required_fields = ['student_id', 'name']
        for field in required_fields:
            if not data.get(field, '').strip():
                return jsonify({'error': f'{field} is required'}), 400

        student_id = data['student_id'].strip()
        name = data['name'].strip()

        # Check if student_id already exists
        existing_student = Student.query.filter_by(student_id=student_id).first()
        if existing_student:
            return jsonify({'error': 'Student ID already exists'}), 409

        # Create new student
        student = Student(
            student_id=student_id,
            name=name,
            email=data.get('email', '').strip() or None,
            phone=data.get('phone', '').strip() or None,
            gender=data.get('gender', '').strip() or None,
            dob=data.get('dob'),  # Date will be parsed by SQLAlchemy
            address=data.get('address', '').strip() or None,
            program=data.get('program', '').strip() or None,
            status=data.get('status', 'Active'),
            guardian_name=data.get('guardian_name', '').strip() or None,
            guardian_phone=data.get('guardian_phone', '').strip() or None,
            created_by=user_id
        )

        db.session.add(student)
        db.session.commit()

        # Log the action
        log_action(user_id, 'STUDENT_CREATED', f'Student {student_id} - {name} created')

        return jsonify({
            'message': 'Student created successfully',
            'student': student.to_dict()
        }), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@students_bp.route('/<student_id>', methods=['PUT'])
@jwt_required()
def update_student(student_id):
    """Update an existing student"""
    try:
        user_id = get_jwt_identity()
        student = Student.query.filter_by(student_id=student_id).first()

        if not student:
            return jsonify({'error': 'Student not found'}), 404

        data = request.get_json()

        # Update fields
        updatable_fields = [
            'name', 'email', 'phone', 'gender', 'dob', 'address',
            'program', 'status', 'guardian_name', 'guardian_phone'
        ]

        for field in updatable_fields:
            if field in data:
                value = data[field]
                if isinstance(value, str):
                    value = value.strip()
                    value = value if value else None
                setattr(student, field, value)

        db.session.commit()

        # Log the action
        log_action(user_id, 'STUDENT_UPDATED', f'Student {student_id} updated')

        return jsonify({
            'message': 'Student updated successfully',
            'student': student.to_dict()
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@students_bp.route('/<student_id>', methods=['DELETE'])
@jwt_required()
def delete_student(student_id):
    """Delete a student"""
    try:
        user_id = get_jwt_identity()
        student = Student.query.filter_by(student_id=student_id).first()

        if not student:
            return jsonify({'error': 'Student not found'}), 404

        # Delete associated image file if exists
        if student.image_path and os.path.exists(student.image_path):
            try:
                os.remove(student.image_path)
            except:
                pass  # Ignore file deletion errors

        db.session.delete(student)
        db.session.commit()

        # Log the action
        log_action(user_id, 'STUDENT_DELETED', f'Student {student_id} - {student.name} deleted')

        return jsonify({'message': 'Student deleted successfully'}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@students_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_student_stats():
    """Get student statistics"""
    try:
        total_students = Student.query.count()

        # Gender distribution
        gender_stats = db.session.query(
            Student.gender,
            func.count(Student.id).label('count')
        ).group_by(Student.gender).all()

        # Program distribution
        program_stats = db.session.query(
            Student.program,
            func.count(Student.id).label('count')
        ).filter(Student.program.isnot(None)).group_by(Student.program).all()

        # Status distribution
        status_stats = db.session.query(
            Student.status,
            func.count(Student.id).label('count')
        ).group_by(Student.status).all()

        return jsonify({
            'total_students': total_students,
            'gender_distribution': {gender: count for gender, count in gender_stats},
            'program_distribution': {program: count for program, count in program_stats},
            'status_distribution': {status: count for status, count in status_stats}
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@students_bp.route('/programs', methods=['GET'])
@jwt_required()
def get_programs():
    """Get list of all programs"""
    try:
        programs = db.session.query(Student.program)\
                           .filter(Student.program.isnot(None))\
                           .distinct()\
                           .order_by(Student.program)\
                           .all()

        return jsonify({
            'programs': [program[0] for program in programs]
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500

def log_action(user_id, action, details):
    """Helper function to log user actions"""
    try:
        log_entry = AuditLog(
            user_id=user_id,
            action=action,
            details=details,
            ip_address=request.remote_addr,
            user_agent=request.headers.get('User-Agent')
        )
        db.session.add(log_entry)
        db.session.commit()
    except Exception as e:
        print(f"Failed to log action: {e}")
        db.session.rollback()