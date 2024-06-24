from flask_mail import Message
from flask import url_for, current_app
import os

def allowed_file(filename, allowed_extensions={'pptx', 'docx', 'xlsx'}):
    """
    Check if the file has one of the allowed extensions
    """
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in allowed_extensions

def send_verification_email(user):
    """
    Send a verification email to the user with a token for email verification
    """
    token = user.get_reset_token()
    verification_url = url_for('main.verify_email', token=token, _external=True)
    msg = Message('Verify Your Email', 
                  sender=current_app.config['MAIL_USERNAME'], 
                  recipients=[user.email])
    msg.body = f'Please click the following link to verify your email: {verification_url}'
    mail.send(msg)

def save_file(file):
    """
    Save the uploaded file to a designated directory
    """
    filename = secure_filename(file.filename)
    file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
    file.save(file_path)
    return file_path

def get_file_path(filename):
    """
    Get the file path for a given filename
    """
    return os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
