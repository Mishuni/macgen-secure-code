import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { NewEntry, UpdateEntry } from './entry.schema';

@Injectable()
export class DatabaseService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3');
    this.db.serialize(() => {
      this.db.run(`CREATE TABLE IF NOT EXISTS entries (
        id TEXT PRIMARY KEY,
        title TEXT,
        content TEXT,
        lastModifiedBy TEXT,
        lastModifiedAt TEXT
      )`);
    });
  }

  async getAllEntries() {
    return new Promise((resolve, reject) => {
      this.db.all('SELECT id, title FROM entries', [], (err, rows) => {
        if (err) reject(err);
        resolve(rows);
      });
    });
  }

  async createEntry(newEntry: NewEntry) {
    return new Promise((resolve, reject) => {
      const id = new Date().toISOString();
      const stmt = this.db.prepare('INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)');
      stmt.run(id, newEntry.title, newEntry.content, newEntry.createdBy, new Date().toISOString(), (err) => {
        if (err) reject(err);
        resolve({ id, ...newEntry });
      });
      stmt.finalize();
    });
  }

  async getEntry(entryId: string) {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT * FROM entries WHERE id = ?', [entryId], (err, row) => {
        if (err) reject(err);
        resolve(row);
      });
    });
  }

  async updateEntry(entryId: string, updateEntry: UpdateEntry) {
    return new Promise((resolve, reject) => {
      const stmt = this.db.prepare('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?');
      stmt.run(updateEntry.content, updateEntry.modifiedBy, new Date().toISOString(), entryId, (err) => {
        if (err) reject(err);
        resolve({ id: entryId, ...updateEntry });
      });
      stmt.finalize();
    });
  }

  async getEntryEdits(entryId: string) {
    // Placeholder for edit history logic
    return Promise.resolve('Edit history not implemented');
  }
}