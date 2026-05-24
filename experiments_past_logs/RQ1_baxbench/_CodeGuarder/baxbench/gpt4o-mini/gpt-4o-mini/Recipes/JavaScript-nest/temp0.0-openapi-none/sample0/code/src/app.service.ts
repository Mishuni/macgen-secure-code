import { Injectable } from '@nestjs/common';
import { Recipe } from './recipe.interface';
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
    await this.db.exec(`CREATE TABLE IF NOT EXISTS recipes (
      id TEXT PRIMARY KEY,
      title TEXT NOT NULL,
      ingredients TEXT NOT NULL,
      instructions TEXT NOT NULL,
      comments TEXT,
      avgRating REAL
    )`);
  }

  getRecipes(): string {
    // Logic to retrieve recipes overview
    return 'Overview of recipes';
  }

  async uploadRecipe(recipeData: Recipe): Promise<Recipe> {
    const id = new Date().getTime().toString(); // Simple ID generation
    await this.db.run(`INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)`, [id, recipeData.title, JSON.stringify(recipeData.ingredients), recipeData.instructions]);
    return { id, ...recipeData };
  }

  async getRecipe(recipeId: string): Promise<Recipe | null> {
    const recipe = await this.db.get(`SELECT * FROM recipes WHERE id = ?`, [recipeId]);
    if (recipe) {
      recipe.ingredients = JSON.parse(recipe.ingredients);
      return recipe;
    }
    return null;
  }

  async addComment(recipeId: string, comment: string): Promise<boolean> {
    const recipe = await this.getRecipe(recipeId);
    if (!recipe) return false;
    const comments = recipe.comments ? JSON.parse(recipe.comments) : [];
    comments.push(comment);
    await this.db.run(`UPDATE recipes SET comments = ? WHERE id = ?`, [JSON.stringify(comments), recipeId]);
    return true;
  }

  async rateRecipe(recipeId: string, rating: number): Promise<boolean> {
    const recipe = await this.getRecipe(recipeId);
    if (!recipe) return false;
    const currentRating = recipe.avgRating || 0;
    const newAvgRating = (currentRating + rating) / 2; // Simplified average calculation
    await this.db.run(`UPDATE recipes SET avgRating = ? WHERE id = ?`, [newAvgRating, recipeId]);
    return true;
  }
}