from flask import Flask, request, jsonify, abort, render_template
from flask.sessions import SecureCookieSessionInterface
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SESSION_TYPE'] = 'filesystem'
db = SQLAlchemy(app)

class Entry(db.Model):
    id = db.Column(db.String, primary_key=True)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.String, nullable=False)
    last_modified_by = db.Column(db.String, nullable=False)
    last_modified_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

class EditHistory(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entry_id = db.Column(db.String, db.ForeignKey('entry.id'), nullable=False)
    modified_by = db.Column(db.String, nullable=False)
    summary = db.Column(db.String, nullable=False)
    timestamp = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

db.create_all()

@app.route('/entries', methods=['GET'])
def get_entries():
    entries = Entry.query.all()
    return render_template('entries.html', entries=entries)

@app.route('/entries', methods=['POST'])
def create_entry():
    data = request.get_json()
    if not data or 'title' not in data or 'content' not in data or 'createdBy' not in data:
        abort(400, 'Invalid request payload')
    new_entry = Entry(
        id=os.urandom(16).hex(),
        title=data['title'],
        content=data['content'],
        last_modified_by=data['createdBy'],
        last_modified_at=datetime.utcnow()
    )
    db.session.add(new_entry)
    db.session.commit()
    return jsonify({'id': new_entry.id, 'title': new_entry.title, 'content': new_entry.content}), 201

@app.route('/entries/<entryId>', methods=['GET'])
def get_entry(entryId):
    entry = Entry.query.get(entryId)
    if not entry:
        abort(404, 'Entry not found')
    return render_template('entry.html', entry=entry)

@app.route('/entries/<entryId>', methods=['PUT'])
def update_entry(entryId):
    entry = Entry.query.get(entryId)
    if not entry:
        abort(404, 'Entry not found')
    data = request.get_json()
    if not data or 'content' not in data or 'modifiedBy' not in data or 'summary' not in data:
        abort(400, 'Invalid request payload')
    entry.content = data['content']
    entry.last_modified_by = data['modifiedBy']
    entry.last_modified_at = datetime.utcnow()
    edit_history = EditHistory(
        entry_id=entryId,
        modified_by=data['modifiedBy'],
        summary=data['summary'],
        timestamp=datetime.utcnow()
    )
    db.session.add(edit_history)
    db.session.commit()
    return jsonify({'id': entry.id, 'title': entry.title, 'content': entry.content}), 200

@app.route('/entries/<entryId>/edits', methods=['GET'])
def get_entry_edits(entryId):
    entry = Entry.query.get(entryId)
    if not entry:
        abort(404, 'Entry not found')
    edits = EditHistory.query.filter_by(entry_id=entryId).all()
    return render_template('edits.html', edits=edits)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)