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
      CREATE TABLE IF NOT EXISTS recipes (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        ingredients TEXT NOT NULL,
        instructions TEXT NOT NULL,
        avgRating REAL
      );
    `);

    await db.exec(`
      CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipeId TEXT NOT NULL,
        comment TEXT NOT NULL,
        FOREIGN KEY (recipeId) REFERENCES recipes(id)
      );
    `);

    await db.exec(`
      CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipeId TEXT NOT NULL,
        rating INTEGER NOT NULL,
        FOREIGN KEY (recipeId) REFERENCES recipes(id)
      );
    `);

    this.db = db;
  }

  async getRecipesOverview(): Promise<string> {
    const recipes = await this.db.all('SELECT id, title FROM recipes');
    return JSON.stringify(recipes);
  }

  async uploadRecipe(title: string, ingredients: string[], instructions: string): Promise<object> {
    const id = crypto.randomUUID();
    const ingredientsStr = JSON.stringify(ingredients);

    await this.db.run(
      'INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)',
      [id, title, ingredientsStr, instructions],
    );

    return { id, title, ingredients, instructions };
  }

  async getRecipe(recipeId: string): Promise<string | null> {
    const recipe = await this.db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);
    if (!recipe) {
      return null;
    }

    const comments = await this.db.all('SELECT comment FROM comments WHERE recipeId = ?', [recipeId]);
    const ratings = await this.db.all('SELECT rating FROM ratings WHERE recipeId = ?', [recipeId]);

    recipe.comments = comments.map((c) => c.comment);
    recipe.avgRating = ratings.length
      ? ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length
      : null;

    return JSON.stringify(recipe);
  }

  async addComment(recipeId: string, comment: string): Promise<object | null> {
    const recipe = await this.db.get('SELECT id FROM recipes WHERE id = ?', [recipeId]);
    if (!recipe) {
      return null;
    }

    await this.db.run('INSERT INTO comments (recipeId, comment) VALUES (?, ?)', [recipeId, comment]);
    return { recipeId, comment };
  }

  async addRating(recipeId: string, rating: number): Promise<object | null> {
    const recipe = await this.db.get('SELECT id FROM recipes WHERE id = ?', [recipeId]);
    if (!recipe) {
      return null;
    }

    await this.db.run('INSERT INTO ratings (recipeId, rating) VALUES (?, ?)', [recipeId, rating]);
    return { recipeId, rating };
  }
}