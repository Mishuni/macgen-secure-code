import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { open } from 'sqlite';
import { Recipe } from './recipe.interface';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class DatabaseService {
  private db: Database;

  constructor() {
    this.init();
  }

  async init() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: Database,
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

  async uploadRecipe(recipe: Recipe) {
    const id = uuidv4(); // Use UUID for unique ID generation
    await this.db.run('INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)', [id, recipe.title, JSON.stringify(recipe.ingredients), recipe.instructions]);
    return { id, ...recipe };
  }

  async getRecipe(recipeId: string) {
    const recipe = await this.db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);
    if (recipe) {
      const comments = await this.db.all('SELECT comment FROM comments WHERE recipeId = ?', [recipeId]);
      const ratings = await this.db.all('SELECT rating FROM ratings WHERE recipeId = ?', [recipeId]);
      const avgRating = ratings.length ? ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length : null;
      return { ...recipe, comments, avgRating };
    }
    return null;
  }

  async addComment(recipeId: string, comment: string) {
    if (!comment || typeof comment !== 'string') {
      throw new Error('Invalid comment');
    }
    await this.db.run('INSERT INTO comments (recipeId, comment) VALUES (?, ?)', [recipeId, comment]);
  }

  async rateRecipe(recipeId: string, rating: number) {
    if (rating < 1 || rating > 5) {
      throw new Error('Invalid rating');
    }
    await this.db.run('INSERT INTO ratings (recipeId, rating) VALUES (?, ?)', [recipeId, rating]);
  }
}