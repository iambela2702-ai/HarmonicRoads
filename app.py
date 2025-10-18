from flask import Flask, render_template, request, jsonify, redirect, url_for
import sqlite3
from datetime import datetime
import requests
import os

app = Flask(__name__)
app.secret_key = os.environ.get('SESSION_SECRET', 'dev-secret-key-change-in-production')

DATABASE = 'armonia.db'

def get_db_connection():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db_connection()
    
    conn.execute('''
        CREATE TABLE IF NOT EXISTS mensajes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nombre TEXT NOT NULL,
            comentario TEXT,
            mensaje TEXT,
            tema TEXT DEFAULT 'general',
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor = conn.execute("PRAGMA table_info(mensajes)")
    columns = [column[1] for column in cursor.fetchall()]
    
    if 'mensaje' not in columns:
        conn.execute('ALTER TABLE mensajes ADD COLUMN mensaje TEXT')
    
    if 'tema' not in columns:
        conn.execute('ALTER TABLE mensajes ADD COLUMN tema TEXT DEFAULT "general"')
    
    conn.execute('UPDATE mensajes SET mensaje = comentario WHERE mensaje IS NULL AND comentario IS NOT NULL')
    
    conn.commit()
    conn.close()

init_db()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ambiente')
def ambiente():
    return render_template('ambiente.html')

@app.route('/cultura')
def cultura():
    return render_template('cultura.html')

@app.route('/educacion')
def educacion():
    return render_template('educacion.html')

@app.route('/mapa')
def mapa():
    weather_data = get_weather()
    return render_template('mapa.html', weather=weather_data)

@app.route('/comunidad')
def comunidad():
    conn = get_db_connection()
    mensajes = conn.execute('SELECT * FROM mensajes ORDER BY fecha DESC').fetchall()
    conn.close()
    
    return render_template('comunidad.html', mensajes=mensajes)

@app.route('/api/comunidad/add', methods=['POST'])
def api_comunidad_add():
    data = request.get_json()
    nombre = data.get('nombre', '').strip()
    mensaje = data.get('mensaje', '').strip()
    tema = data.get('tema', 'general')
    
    if not nombre or not mensaje:
        return jsonify({'error': 'Nombre y mensaje son requeridos'}), 400
    
    conn = get_db_connection()
    cursor = conn.execute(
        'INSERT INTO mensajes (nombre, mensaje, tema) VALUES (?, ?, ?)',
        (nombre, mensaje, tema)
    )
    mensaje_id = cursor.lastrowid
    
    nuevo_mensaje = conn.execute(
        'SELECT * FROM mensajes WHERE id = ?', 
        (mensaje_id,)
    ).fetchone()
    conn.commit()
    conn.close()
    
    return jsonify({
        'id': nuevo_mensaje['id'],
        'nombre': nuevo_mensaje['nombre'],
        'mensaje': nuevo_mensaje['mensaje'],
        'tema': nuevo_mensaje['tema'],
        'fecha': nuevo_mensaje['fecha'][:16]
    }), 201

@app.route('/api/comunidad/delete/<int:mensaje_id>', methods=['DELETE'])
def api_comunidad_delete(mensaje_id):
    conn = get_db_connection()
    conn.execute('DELETE FROM mensajes WHERE id = ?', (mensaje_id,))
    conn.commit()
    conn.close()
    
    return jsonify({'success': True}), 200

@app.route('/asistente', methods=['GET', 'POST'])
def asistente():
    respuesta = None
    if request.method == 'POST':
        mensaje = request.form.get('mensaje', '').lower().strip()
        respuesta = get_chatbot_response(mensaje)
    
    return render_template('asistente.html', respuesta=respuesta)

@app.route('/api/asistente', methods=['POST'])
def api_asistente():
    data = request.get_json()
    mensaje = data.get('mensaje', '').lower().strip()
    respuesta = get_chatbot_response(mensaje)
    return jsonify({'respuesta': respuesta})

@app.route('/api/comunidad')
def api_comunidad():
    conn = get_db_connection()
    mensajes = conn.execute('SELECT * FROM mensajes ORDER BY fecha DESC').fetchall()
    conn.close()
    
    mensajes_list = [dict(mensaje) for mensaje in mensajes]
    return jsonify(mensajes_list)

def get_chatbot_response(mensaje):
    responses = {
        "movilidad": "Moverse con respeto es moverse con conciencia. Recuerda priorizar al peatón y compartir la vía. 🚶‍♂️🚴",
        "cultura": "La convivencia vial también es cultura ciudadana. Una sonrisa puede prevenir un accidente. 😊🚦",
        "ambiente": "Caminar, usar bici o compartir vehículo ayuda a reducir emisiones. ¡Pequeños gestos, grandes cambios! 🌱🌍",
        "educacion": "Aprender a movernos bien es parte de convivir mejor. La educación vial salva vidas. 📚✨",
        "bicicleta": "La bicicleta es un medio de transporte sostenible, saludable y económico. ¡Pedalea hacia el futuro! 🚲💚",
        "peatón": "El peatón siempre tiene prioridad. Respetar el paso de cebra es respetar la vida. 🚶‍♀️❤️",
        "transporte": "El transporte compartido reduce congestión y emisiones. ¡Comparte el viaje! 🚗👥",
        "seguridad": "La seguridad vial es responsabilidad de todos. Usa cinturón, respeta límites y señales. 🦺⚠️",
        "uraba": "Urabá merece movilidad sostenible y segura. Juntos construimos mejores vías para todos. 🌴🛣️",
        "armonia": "ArmonIA Vial promueve el respeto, la convivencia y la movilidad consciente en Urabá. 💚🤝"
    }
    
    for keyword, response in responses.items():
        if keyword in mensaje:
            return response
    
    return "Puedo darte consejos sobre movilidad, cultura vial y medio ambiente. ¡Pregunta algo! 💬✨"

def get_weather():
    try:
        api_key = os.environ.get('OPENWEATHER_API_KEY')
        if not api_key:
            return None
        
        city = "Apartadó,CO"
        url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={api_key}&units=metric&lang=es"
        response = requests.get(url, timeout=5)
        
        if response.status_code == 200:
            data = response.json()
            return {
                'temp': round(data['main']['temp']),
                'description': data['weather'][0]['description'].capitalize(),
                'icon': data['weather'][0]['icon']
            }
    except Exception as e:
        print(f"Error obteniendo clima: {e}")
    
    return None

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
