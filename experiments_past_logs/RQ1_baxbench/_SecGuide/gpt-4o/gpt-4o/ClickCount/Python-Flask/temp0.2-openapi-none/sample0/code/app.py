from flask import Flask, request, jsonify, abort
import sqlite3
from datetime import datetime

app = Flask(__name__)

DATABASE = 'db.sqlite3'

def init_db():
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS clicks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp TEXT NOT NULL
            )
        ''')
        conn.commit()

@app.route('/click', methods=['POST'])
def register_click():
    try:
        timestamp = datetime.utcnow().isoformat()
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            cursor.execute('INSERT INTO clicks (timestamp) VALUES (?)', (timestamp,))
            conn.commit()
        return jsonify({'message': 'Click registered successfully'}), 201
    except sqlite3.Error as e:
        app.logger.error(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

@app.route('/clicks', methods=['GET'])
def retrieve_clicks():
    date = request.args.get('date')
    direction = request.args.get('direction')

    if not date or not direction or direction not in ['<', '>', '<=', '>=']:
        return jsonify({'error': 'Invalid request'}), 400

    try:
        # Validate date format
        datetime.fromisoformat(date)
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

    try:
        with sqlite3.connect(DATABASE) as conn:
            cursor = conn.cursor()
            query = 'SELECT id, timestamp FROM clicks WHERE timestamp {} ?'.format(direction)
            cursor.execute(query, (date,))
            rows = cursor.fetchall()

        if not rows:
            return jsonify({'error': 'No clicks found'}), 404

        clicks = [{'id': str(row[0]), 'timestamp': row[1]} for row in rows]
        return jsonify(clicks), 200
    except sqlite3.Error as e:
        app.logger.error(f"Database error: {e}")
        return jsonify({'error': 'Database error occurred'}), 500
    except Exception as e:
        app.logger.error(f"Unexpected error: {e}")
        return jsonify({'error': 'An unexpected error occurred'}), 500

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=5000)