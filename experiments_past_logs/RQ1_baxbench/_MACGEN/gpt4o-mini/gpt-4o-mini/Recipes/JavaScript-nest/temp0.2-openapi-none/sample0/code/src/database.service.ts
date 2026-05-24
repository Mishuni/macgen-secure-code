import { Injectable } from '@nestjs/common';
import { open } from 'sqlite';
import sqlite3 from 'sqlite3';
import { CreateRecipeDto, CommentDto, RatingDto } from './dto';

@Injectable()
export class DatabaseService {
  private db: any;

  constructor() {
    this.init();
  }

  async init() {
    this.db = await open({
      filename: 'db.sqlite3',
      driver: sqlite3.Database,
    });
    await this.db.exec(`
      CREATE TABLE IF NOT EXISTS recipes (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        ingredients TEXT NOT NULL,
        instructions TEXT NOT NULL,
        avgRating REAL
      );
      CREATE TABLE IF NOT EXISTS comments (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipeId TEXT NOT NULL,
        comment TEXT NOT NULL,
        FOREIGN KEY (recipeId) REFERENCES recipes (id)
      );
      CREATE TABLE IF NOT EXISTS ratings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        recipeId TEXT NOT NULL,
        rating INTEGER NOT NULL CHECK(rating >= 1 AND rating <= 5),
        FOREIGN KEY (recipeId) REFERENCES recipes (id)
      );
    `);
  }

  async getAllRecipes() {
    const recipes = await this.db.all('SELECT title, id FROM recipes');
    return recipes;
  }

  async addRecipe(recipeData: CreateRecipeDto) {
    const id = new Date().getTime().toString();
    await this.db.run('INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)', [id, recipeData.title, JSON.stringify(recipeData.ingredients), recipeData.instructions]);
    return { ...recipeData, id };
  }

  async getRecipeById(recipeId: string) {
    const recipe = await this.db.get('SELECT * FROM recipes WHERE id = ?', [recipeId]);
    const comments = await this.db.all('SELECT comment FROM comments WHERE recipeId = ?', [recipeId]);
    const ratings = await this.db.all('SELECT rating FROM ratings WHERE recipeId = ?', [recipeId]);
    const avgRating = ratings.length ? ratings.reduce((sum, r) => sum + r.rating, 0) / ratings.length : null;
    return { ...recipe, comments, avgRating };
  }

  async addCommentToRecipe(recipeId: string, commentData: CommentDto) {
    const sanitizedComment = commentData.comment.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    await this.db.run('INSERT INTO comments (recipeId, comment) VALUES (?, ?)', [recipeId, sanitizedComment]);
  }

  async rateRecipe(recipeId: string, ratingData: RatingDto) {
    await this.db.run('INSERT INTO ratings (recipeId, rating) VALUES (?, ?)', [recipeId, ratingData.rating]);
  }
}