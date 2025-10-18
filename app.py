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
            comentario TEXT NOT NULL,
            fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

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

@app.route('/comunidad', methods=['GET', 'POST'])
def comunidad():
    if request.method == 'POST':
        nombre = request.form.get('nombre', '').strip()
        comentario = request.form.get('comentario', '').strip()
        
        if nombre and comentario:
            conn = get_db_connection()
            conn.execute('INSERT INTO mensajes (nombre, comentario) VALUES (?, ?)',
                        (nombre, comentario))
            conn.commit()
            conn.close()
            return redirect(url_for('comunidad'))
    
    conn = get_db_connection()
    mensajes = conn.execute('SELECT * FROM mensajes ORDER BY fecha DESC LIMIT 20').fetchall()
    conn.close()
    
    return render_template('comunidad.html', mensajes=mensajes)

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
    init_db()
    app.run(host='0.0.0.0', port=5000, debug=True)
