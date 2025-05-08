import os
from datetime import datetime

from flask import Flask, redirect, render_template, request, send_from_directory, url_for, jsonify
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect


app = Flask(__name__, static_folder='static')
csrf = CSRFProtect(app)

# WEBSITE_HOSTNAME exists only in production environment
if 'WEBSITE_HOSTNAME' not in os.environ:
    # local development, where we'll use environment variables
    print("Loading config.development and environment variables from .env file.")
    app.config.from_object('azureproject.development')
else:
    # production
    print("Loading config.production.")
    app.config.from_object('azureproject.production')

app.config.update(
    SQLALCHEMY_DATABASE_URI=app.config.get('DATABASE_URI'),
    SQLALCHEMY_TRACK_MODIFICATIONS=False,
)

# Initialize the database connection
db = SQLAlchemy(app)

# Enable Flask-Migrate commands "flask db init/migrate/upgrade" to work
migrate = Migrate(app, db)

# The import must be done after db initialization due to circular import issue
from models import ImageView

# Contexto global para todas las plantillas
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/api/upload-image-data', methods=['POST'])
@csrf.exempt
def upload_image_data():
    data = request.json
    
    # Extraer datos principales
    username = data.get('username')
    filename = data.get('fileName')
    timestamp = data.get('timestamp')
    
    # Extraer estadísticas de color
    pixel_stats = data.get('pixelStats', {})
    red_pixels = 0
    green_pixels = 0
    blue_pixels = 0
    other_pixels = 0
    
    # Analizar las estadísticas de colores para clasificarlos
    for color_key, count in pixel_stats.items():
        if color_key.startswith('R7') or color_key.startswith('R6'):
            red_pixels += count
        elif color_key.startswith('G7') or color_key.startswith('G6'):
            green_pixels += count
        elif color_key.startswith('B7') or color_key.startswith('B6'):
            blue_pixels += count
        else:
            other_pixels += count
    
    # Crear nuevo registro en la base de datos
    new_image_view = ImageView(
        username=username,
        filename=filename,
        processed_date=datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S'),
        red_pixels=red_pixels,
        green_pixels=green_pixels,
        blue_pixels=blue_pixels,
        other_pixels=other_pixels
    )
    
    try:
        db.session.add(new_image_view)
        db.session.commit()
        return jsonify({"success": True, "message": "Data saved successfully"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)