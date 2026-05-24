import { Injectable } from '@nestjs/common';
import * as sqlite3 from 'sqlite3';
import { open } from 'sqlite';

@Injectable()
export class AppService {
  private db: sqlite3.Database;

  constructor() {
    this.initializeDatabase();
  }

  private async initializeDatabase() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });
    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS recipes (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        ingredients TEXT NOT NULL,
        instructions TEXT NOT NULL
      );
      CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipeId TEXT NOT NULL,
        comment TEXT NOT NULL,
        FOREIGN KEY (recipeId) REFERENCES recipes(id)
      );
      CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipeId TEXT NOT NULL,
        rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
        FOREIGN KEY (recipeId) REFERENCES recipes(id)
      );
    `);
  }

  async getRecipes() {
    const recipes = await this.db.all('SELECT id, title FROM recipes');
    return recipes;
  }

  async uploadRecipe(recipeData: { title: string; ingredients: string[]; instructions: string }) {
    const id = new Date().getTime().toString(); // Simple unique ID generation
    await this.db.run('INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)', [id, recipeData.title, JSON.stringify(recipeData.ingredients), recipeData.instructions]);
    return { id, ...recipeData };
  }

  async getRecipe(recipeId: string) {
    const recipe = await this.db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);
    if (recipe) {
      const comments = await this.db.all('SELECT comment FROM comments WHERE recipeId = ?', [recipeId]);
      const ratings = await this.db.all('SELECT rating FROM ratings WHERE recipeId = ?', [recipeId]);
      const avgRating = ratings.length > 0 ? ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length : null;
      return { ...recipe, comments, avgRating };
    }
    return null;
  }

  async addComment(recipeId: string, comment: string) {
    const result = await this.db.run('INSERT INTO comments (recipeId, comment) VALUES (?, ?)', [recipeId, comment]);
    return result.changes > 0;
  }

  async rateRecipe(recipeId: string, rating: number) {
    const result = await this.db.run('INSERT INTO ratings (recipeId, rating) VALUES (?, ?)', [recipeId, rating]);
    return result.changes > 0;
  }
}