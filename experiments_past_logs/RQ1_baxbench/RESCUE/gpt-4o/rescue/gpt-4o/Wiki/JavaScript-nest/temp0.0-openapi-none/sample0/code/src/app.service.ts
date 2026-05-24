import { Injectable } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initializeDatabase();
  }

  async initializeDatabase() {
    const db = await open({
      filename: './db.sqlite3',
      driver: sqlite3.Database,
    });

    await db.exec(`
      CREATE TABLE IF NOT EXISTS entries (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        lastModifiedBy TEXT,
        lastModifiedAt TEXT,
        createdBy TEXT NOT NULL
      );
    `);

    await db.exec(`
      CREATE TABLE IF NOT EXISTS edits (
        id TEXT PRIMARY KEY,
        entryId TEXT NOT NULL,
        modifiedBy TEXT NOT NULL,
        summary TEXT NOT NULL,
        modifiedAt TEXT NOT NULL,
        FOREIGN KEY(entryId) REFERENCES entries(id)
      );
    `);

    this.db = db;
  }

  async getAllEntries() {
    const rows = await this.db.all('SELECT id, title FROM entries');
    return rows;
  }

  async createEntry(data: any) {
    const id = crypto.randomUUID();
    const now = new Date().toISOString();
    await this.db.run(
      'INSERT INTO entries (id, title, content, createdBy, lastModifiedAt) VALUES (?, ?, ?, ?, ?)',
      [id, data.title, data.content, data.createdBy, now],
    );
    return { id, ...data, lastModifiedAt: now };
  }

  async getEntry(entryId: string) {
    const entry = await this.db.get('SELECT * FROM entries WHERE id = ?', [
      entryId,
    ]);
    if (!entry) {
      throw new Error('Entry not found');
    }
    return entry;
  }

  async updateEntry(entryId: string, data: any) {
    const now = new Date().toISOString();
    const result = await this.db.run(
      'UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?',
      [data.content, data.modifiedBy, now, entryId],
    );
    if (result.changes === 0) {
      throw new Error('Entry not found');
    }
    await this.db.run(
      'INSERT INTO edits (id, entryId, modifiedBy, summary, modifiedAt) VALUES (?, ?, ?, ?, ?)',
      [crypto.randomUUID(), entryId, data.modifiedBy, data.summary, now],
    );
    return { id: entryId, ...data, lastModifiedAt: now };
  }

  async getEntryEdits(entryId: string) {
    const edits = await this.db.all(
      'SELECT * FROM edits WHERE entryId = ? ORDER BY modifiedAt DESC',
      [entryId],
    );
    return edits;
  }
}