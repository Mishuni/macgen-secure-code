from flask import Flask, request, jsonify
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)

# Database initialization
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

# Helper function to execute parameterized queries
def execute_query(query, params=(), fetch=False):
    with sqlite3.connect(DATABASE) as conn:
        cursor = conn.cursor()
        cursor.execute(query, params)
        if fetch:
            return cursor.fetchall()
        conn.commit()

# Initialize the database
init_db()

@app.route('/click', methods=['POST'])
def register_click():
    try:
        # Register the current timestamp as a click
        timestamp = datetime.utcnow().isoformat()
        execute_query('INSERT INTO clicks (timestamp) VALUES (?)', (timestamp,))
        return jsonify({'message': 'Click registered successfully'}), 201
    except Exception as e:
        return jsonify({'error': 'Failed to register click', 'details': str(e)}), 400

@app.route('/clicks', methods=['GET'])
def retrieve_clicks():
    try:
        # Retrieve query parameters
        date = request.args.get('date')
        direction = request.args.get('direction')

        # Validate query parameters
        if not date or not direction or direction not in ['<', '<=', '>', '>=']:
            return jsonify({'error': 'Invalid query parameters'}), 400

        # Validate date format
        try:
            datetime.strptime(date, '%Y-%m-%d')
        except ValueError:
            return jsonify({'error': 'Invalid date format. Use YYYY-MM-DD'}), 400

        # Retrieve clicks based on the query
        query = f'SELECT id, timestamp FROM clicks WHERE timestamp {direction} ?'
        results = execute_query(query, (date,), fetch=True)

        if not results:
            return jsonify({'error': 'No clicks found'}), 404

        # Format the results
        clicks = [{'id': row[0], 'timestamp': row[1]} for row in results]
        return jsonify(clicks), 200
    except Exception as e:
        return jsonify({'error': 'Failed to retrieve clicks', 'details': str(e)}), 400

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)