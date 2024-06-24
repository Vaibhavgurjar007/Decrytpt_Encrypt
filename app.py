from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_mail import Mail
from flask_login import LoginManager
from config import Config
from models import db, login_manager
from routes import main

app = Flask(__name__)
app.config.from_object(Config)

# Initialize database
db.init_app(app)

# Initialize mail
mail = Mail(app)

# Initialize login manager
login_manager.init_app(app)

# Register blueprints
app.register_blueprint(main)

# Create database tables
with app.app_context():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True)
