import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { NewEntryDto, UpdateEntryDto } from './dto';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database', err);
      } else {
        this.db.run(
          `CREATE TABLE IF NOT EXISTS entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL,
            lastModifiedBy TEXT,
            lastModifiedAt TEXT
          )`,
          (err) => {
            if (err) {
              console.error('Error creating table', err);
            }
          },
        );
      }
    });
  }

  getEntries(): Promise<any[]> {
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

  createEntry(newEntryDto: NewEntryDto): Promise<any> {
    return new Promise((resolve, reject) => {
      const { title, content, createdBy } = newEntryDto;
      const id = require('uuid').v4();
      const lastModifiedAt = new Date().toISOString();
      this.db.run(
        `INSERT INTO entries (id, title, content, lastModifiedBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)`,
        [id, title, content, createdBy, lastModifiedAt],
        function (err) {
          if (err) {
            reject(err);
          } else {
            resolve({ id, title, content, lastModifiedBy: createdBy, lastModifiedAt });
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

  updateEntry(entryId: string, updateEntryDto: UpdateEntryDto): Promise<any> {
    return new Promise((resolve, reject) => {
      const { content, modifiedBy } = updateEntryDto;
      const lastModifiedAt = new Date().toISOString();
      this.db.run(
        `UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?`,
        [content, modifiedBy, lastModifiedAt, entryId],
        function (err) {
          if (err) {
            reject(err);
          } else {
            resolve({ id: entryId, content, lastModifiedBy: modifiedBy, lastModifiedAt });
          }
        },
      );
    });
  }

  getEntryEdits(entryId: string): Promise<any[]> {
    // Placeholder for edit history retrieval logic
    return Promise.resolve([]);
  }
}