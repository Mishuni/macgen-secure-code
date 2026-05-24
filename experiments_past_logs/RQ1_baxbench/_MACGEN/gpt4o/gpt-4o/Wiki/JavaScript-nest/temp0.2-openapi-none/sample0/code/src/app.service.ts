import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { v4 as uuidv4 } from 'uuid';
import { NewEntryDto, UpdateEntryDto } from './dto';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database', err.message);
      } else {
        this.db.run(
          `CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT,
            content TEXT,
            lastModifiedBy TEXT,
            lastModifiedAt TEXT
          )`
        );
        this.db.run(
          `CREATE TABLE IF NOT EXISTS edits (
            id TEXT PRIMARY KEY,
            entryId TEXT,
            content TEXT,
            modifiedBy TEXT,
            summary TEXT,
            modifiedAt TEXT,
            FOREIGN KEY(entryId) REFERENCES entries(id)
          )`
        );
      }
    });
  }

  getAllEntries(): Promise<string> {
    return new Promise((resolve, reject) => {
      this.db.all('SELECT id, title FROM entries', [], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          const entries = rows.map(row => `<a href="/entries/${row.id}">${row.title}</a>`).join('<br>');
          resolve(entries);
        }
      });
    });
  }

  createEntry(newEntryDto: NewEntryDto): Promise<any> {
    const id = uuidv4();
    const now = new Date().toISOString();
    return new Promise((resolve, reject) => {
      this.db.run(
        `INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)`,
        [id, newEntryDto.title, newEntryDto.content, newEntryDto.createdBy, now],
        function (err) {
          if (err) {
            reject(err);
          } else {
            resolve({ id, ...newEntryDto, lastModifiedAt: now });
          }
        }
      );
    });
  }

  getEntry(entryId: string): Promise<string> {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT * FROM entries WHERE id = ?', [entryId], (err, row) => {
        if (err) {
          reject(err);
        } else if (row) {
          resolve(`<h1>${row.title}</h1><p>${row.content}</p><p>Last modified by: ${row.lastModifiedBy} at ${row.lastModifiedAt}</p>`);
        } else {
          resolve(null);
        }
      });
    });
  }

  updateEntry(entryId: string, updateEntryDto: UpdateEntryDto): Promise<any> {
    const now = new Date().toISOString();
    return new Promise((resolve, reject) => {
      this.db.run(
        `UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?`,
        [updateEntryDto.content, updateEntryDto.modifiedBy, now, entryId],
        function (err) {
          if (err) {
            reject(err);
          } else if (this.changes === 0) {
            resolve(null);
          } else {
            const editId = uuidv4();
            this.db.run(
              `INSERT INTO edits (id, entryId, content, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?, ?, ?)`,
              [editId, entryId, updateEntryDto.content, updateEntryDto.modifiedBy, updateEntryDto.summary, now],
              (err) => {
                if (err) {
                  reject(err);
                } else {
                  resolve({ id: entryId, ...updateEntryDto, lastModifiedAt: now });
                }
              }
            );
          }
        }
      );
    });
  }

  getEntryEdits(entryId: string): Promise<string> {
    return new Promise((resolve, reject) => {
      this.db.all('SELECT * FROM edits WHERE entryId = ?', [entryId], (err, rows) => {
        if (err) {
          reject(err);
        } else if (rows.length > 0) {
          const edits = rows.map(row => `<p>Modified by: ${row.modifiedBy} at ${row.modifiedAt}<br>Summary: ${row.summary}<br>Content: ${row.content}</p>`).join('<hr>');
          resolve(edits);
        } else {
          resolve(null);
        }
      });
    });
  }
}