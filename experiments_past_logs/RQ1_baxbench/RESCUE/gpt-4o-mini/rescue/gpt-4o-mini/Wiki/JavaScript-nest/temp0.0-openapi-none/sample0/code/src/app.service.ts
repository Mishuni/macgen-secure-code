import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { open } from 'sqlite';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.initDatabase();
  }

  private async initDatabase() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: require('sqlite3').Database,
    });
    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS entries (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        content TEXT NOT NULL,
        createdBy TEXT NOT NULL,
        lastModifiedBy TEXT,
        lastModifiedAt TEXT
      );
      CREATE TABLE IF NOT EXISTS edits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        entryId TEXT NOT NULL,
        modifiedBy TEXT NOT NULL,
        summary TEXT,
        content TEXT NOT NULL,
        FOREIGN KEY (entryId) REFERENCES entries (id)
      );
    `);
  }

  async getAllEntries() {
    return await this.db.all('SELECT id, title FROM entries');
  }

  async createEntry(newEntry: { title: string; content: string; createdBy: string }) {
    const id = new Date().toISOString();
    await this.db.run('INSERT INTO entries (id, title, content, createdBy) VALUES (?, ?, ?, ?)', [id, newEntry.title, newEntry.content, newEntry.createdBy]);
    return { id, ...newEntry };
  }

  async getEntry(entryId: string) {
    return await this.db.get('SELECT * FROM entries WHERE id = ?', [entryId]);
  }

  async updateEntry(entryId: string, updateEntry: { content: string; modifiedBy: string; summary: string }) {
    const entry = await this.getEntry(entryId);
    if (!entry) return null;

    await this.db.run('UPDATE entries SET content = ?, lastModifiedBy = ?, lastModifiedAt = ? WHERE id = ?', [updateEntry.content, updateEntry.modifiedBy, new Date().toISOString(), entryId]);
    await this.db.run('INSERT INTO edits (entryId, modifiedBy, summary, content) VALUES (?, ?, ?, ?)', [entryId, updateEntry.modifiedBy, updateEntry.summary, updateEntry.content]);
    return { ...entry, content: updateEntry.content, lastModifiedBy: updateEntry.modifiedBy, lastModifiedAt: new Date().toISOString() };
  }

  async getEntryEdits(entryId: string) {
    return await this.db.all('SELECT * FROM edits WHERE entryId = ?', [entryId]);
  }
}