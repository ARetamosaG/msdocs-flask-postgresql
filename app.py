import os
from datetime import datetime
import logging

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

#

# Contexto global para todas las plantillas
@app.context_processor
def inject_now():
    return {'now': datetime.now()}

@app.route('/')
def index():
    return render_template('base.html')

@app.route('/api/get-image-data', methods=['GET'])
@csrf.exempt
def get_image_data():
    # Obtener parámetros de filtrado
    username = request.args.get('username')
    filename = request.args.get('filename')
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    sort_by = request.args.get('sort_by', 'date-desc')
    page = int(request.args.get('page', 1))
    per_page = int(request.args.get('per_page', 10))
    
    # Construir la consulta base
    query = ImageView.query
    
    # Aplicar filtros si existen
    if username:
        query = query.filter(ImageView.username.ilike(f'%{username}%'))
    if filename:
        query = query.filter(ImageView.filename.ilike(f'%{filename}%'))
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d')
            query = query.filter(ImageView.processed_date >= from_date)
        except ValueError:
            pass
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d')
            # Añadir un día completo para incluir todo el día final
            to_date = to_date.replace(hour=23, minute=59, second=59)
            query = query.filter(ImageView.processed_date <= to_date)
        except ValueError:
            pass
    
    # Aplicar ordenamiento
    if sort_by == 'date-desc':
        query = query.order_by(ImageView.processed_date.desc())
    elif sort_by == 'date-asc':
        query = query.order_by(ImageView.processed_date.asc())
    elif sort_by == 'username':
        query = query.order_by(ImageView.username)
    elif sort_by == 'filename':
        query = query.order_by(ImageView.filename)
    else:
        query = query.order_by(ImageView.processed_date.desc())
    
    # Paginación
    total_items = query.count()
    total_pages = (total_items + per_page - 1) // per_page  # Techo de la división
    
    # Obtener los elementos de la página actual
    items = query.offset((page - 1) * per_page).limit(per_page).all()
    
    # Convertir elementos a diccionarios
    data = [item.to_dict() for item in items]
    
    return jsonify({
        'success': True,
        'data': data,
        'pagination': {
            'current_page': page,
            'per_page': per_page,
            'total_items': total_items,
            'total_pages': total_pages
        }
    })

@app.route('/api/upload-image-data', methods=['POST'])
@csrf.exempt
def upload_image_data():
    data = request.json

    # Comprobar posibles errores:
    if data is None:
        return jsonify({"success": False, "message": "No se recibió JSON válido"}), 400
    
    # Extraer datos principales
    username = data.get('username')
    filename = data.get('fileName')
    timestamp = data.get('timestamp')

    # Comprobar más posibles errores:
    if not (username and filename and timestamp):
        return jsonify({"success": False, "message": "Faltan campos obligatorios"}), 400
    
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
    
    # Comprobar más errores:
    try:
        processed_date = datetime.strptime(timestamp, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"success": False, "message": "Formato de fecha inválido"}), 400

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
        print("ERROR AL GUARDAR EN BD:", e)
        app.logger.error("Error al guardar los datos: %s", str(e))
        return jsonify({"success": False, "message": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)