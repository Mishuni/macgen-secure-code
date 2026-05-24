import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { NewEntry, UpdateEntry } from './entry.dto';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class DatabaseService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error(err.message);
      } else {
        this.db.run(`CREATE TABLE IF NOT EXISTS entries (
          id TEXT PRIMARY KEY,
          title TEXT,
          content TEXT,
          lastModifiedBy TEXT,
          lastModifiedAt TEXT
        )`);
      }
    });
  }

  getAllEntries(): Promise<any[]> {
    return new Promise((resolve, reject) => {
      this.db.all('SELECT id, title FROM entries', [], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          resolve(rows);
        }
      });
    });
  }

  createEntry(newEntry: NewEntry): Promise<any> {
    return new Promise((resolve, reject) => {
      const id = uuidv4();
      const createdAt = new Date().toISOString();
      this.db.run(
        'INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)',
        [id, newEntry.title, newEntry.content, newEntry.createdBy, createdAt],
        (err) => {
          if (err) {
            reject(err);
          } else {
            resolve({ id, ...newEntry });
          }
        },
      );
    });
  }

  getEntry(entryId: string): Promise<any> {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT * FROM entries WHERE id = ?', [entryId], (err, row) => {
        if (err) {
          reject(err);
        } else {
          resolve(row);
        }
      });
    });
  }

  updateEntry(entryId: string, updateEntry: UpdateEntry): Promise<any> {
    return new Promise((resolve, reject) => {
      const updatedAt = new Date().toISOString();
      this.db.run(
        'UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?',
        [updateEntry.content, updateEntry.modifiedBy, updatedAt, entryId],
        (err) => {
          if (err) {
            reject(err);
          } else {
            resolve({ id: entryId, ...updateEntry });
          }
        },
      );
    });
  }

  getEntryEdits(entryId: string): Promise<any> {
    // Placeholder for edit history logic
    return Promise.resolve(`Edit history for entry ${entryId}`);
  }
}