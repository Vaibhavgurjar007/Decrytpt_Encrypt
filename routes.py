from flask import Blueprint, request, jsonify, flash, redirect, url_for, send_file
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.security import generate_password_hash, check_password_hash
from models import db, User, File
from flask_mail import Message
from io import BytesIO
from utils import allowed_file, send_verification_email, save_file, get_file_path

main = Blueprint('main', __name__)

@main.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    hashed_password = generate_password_hash(data['password'], method='sha256')
    user = User(username=data['username'], email=data['email'], password=hashed_password, user_type='client')
    db.session.add(user)
    db.session.commit()

    send_verification_email(user)

    return jsonify({'message': 'User registered. Verification email sent.'})

@main.route('/verify_email/<token>', methods=['GET'])
def verify_email(token):
    user = User.verify_reset_token(token)
    if user is None:
        flash('The verification link is invalid or has expired.', 'warning')
        return redirect(url_for('main.login'))
    # Mark user as verified, e.g., by adding a `verified` field to User model
    # user.verified = True
    # db.session.commit()
    return jsonify({'message': 'Email verified!'})

@main.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    user = User.query.filter_by(email=data['email']).first()
    if user and check_password_hash(user.password, data['password']):
        login_user(user, remember=True)
        return jsonify({'message': 'Logged in successfully!'})
    return jsonify({'message': 'Login failed. Check email and/or password.'}), 401

@main.route('/upload', methods=['POST'])
@login_required
def upload():
    if current_user.user_type != 'ops':
        return jsonify({'message': 'Unauthorized access'}), 403

    if 'file' not in request.files:
        return jsonify({'message': 'No file part in the request'}), 400

    file = request.files['file']
    if file.filename == '':
        return jsonify({'message': 'No selected file'}), 400

    if file and allowed_file(file.filename):
        file_path = save_file(file)
        new_file = File(filename=file.filename, data=file.read(), user_id=current_user.id)
        db.session.add(new_file)
        db.session.commit()
        return jsonify({'message': 'File uploaded successfully!'})

    return jsonify({'message': 'Invalid file type'}), 400

@main.route('/files', methods=['GET'])
@login_required
def list_files():
    files = File.query.all()
    return jsonify([{'filename': file.filename, 'upload_date': file.date_uploaded} for file in files])

@main.route('/download/<int:file_id>', methods=['GET'])
@login_required
def download(file_id):
    file = File.query.get_or_404(file_id)
    return send_file(
        BytesIO(file.data),
        as_attachment=True,
        attachment_filename=file.filename,
        mimetype='application/octet-stream'
    )
