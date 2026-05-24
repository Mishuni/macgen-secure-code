import { Injectable } from '@nestjs/common';
import { Database } from 'sqlite3';
import { v4 as uuidv4 } from 'uuid';

@Injectable()
export class AppService {
  private db: Database;

  constructor() {
    this.db = new Database('db.sqlite3', (err) => {
      if (err) {
        console.error('Error opening database', err.message);
      } else {
        this.db.run(
          `CREATE TABLE IF NOT EXISTS recipes (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            ingredients TEXT NOT NULL,
            instructions TEXT NOT NULL,
            avgRating REAL
          )`
        );
        this.db.run(
          `CREATE TABLE IF NOT EXISTS comments (
            id TEXT PRIMARY KEY,
            recipeId TEXT NOT NULL,
            comment TEXT NOT NULL,
            FOREIGN KEY(recipeId) REFERENCES recipes(id)
          )`
        );
        this.db.run(
          `CREATE TABLE IF NOT EXISTS ratings (
            id TEXT PRIMARY KEY,
            recipeId TEXT NOT NULL,
            rating INTEGER NOT NULL,
            FOREIGN KEY(recipeId) REFERENCES recipes(id)
          )`
        );
      }
    });
  }

  getRecipesOverview(): Promise<string> {
    return new Promise((resolve, reject) => {
      this.db.all('SELECT id, title FROM recipes', [], (err, rows) => {
        if (err) {
          reject(err);
        } else {
          const overview = rows.map(row => `<a href="/recipes/${row.id}">${row.title}</a>`).join('<br>');
          resolve(overview);
        }
      });
    });
  }

  uploadRecipe(body: any): Promise<any> {
    return new Promise((resolve, reject) => {
      const id = uuidv4();
      const { title, ingredients, instructions } = body;
      const ingredientsStr = JSON.stringify(ingredients);

      this.db.run(
        `INSERT INTO recipes (id, title, ingredients, instructions) VALUES (?, ?, ?, ?)`,
        [id, title, ingredientsStr, instructions],
        function (err) {
          if (err) {
            reject(err);
          } else {
            resolve({ id, title, ingredients, instructions });
          }
        }
      );
    });
  }

  getRecipe(recipeId: string): Promise<string | null> {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT * FROM recipes WHERE id = ?', [recipeId], (err, row) => {
        if (err) {
          reject(err);
        } else if (row) {
          const ingredients = JSON.parse(row.ingredients);
          const recipeHtml = `
            <h1>${row.title}</h1>
            <h2>Ingredients</h2>
            <ul>${ingredients.map((ing: string) => `<li>${ing}</li>`).join('')}</ul>
            <h2>Instructions</h2>
            <p>${row.instructions}</p>
          `;
          resolve(recipeHtml);
        } else {
          resolve(null);
        }
      });
    });
  }

  addComment(recipeId: string, comment: string): Promise<void> {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT id FROM recipes WHERE id = ?', [recipeId], (err, row) => {
        if (err) {
          reject(err);
        } else if (row) {
          const id = uuidv4();
          this.db.run(
            `INSERT INTO comments (id, recipeId, comment) VALUES (?, ?, ?)`,
            [id, recipeId, comment],
            function (err) {
              if (err) {
                reject(err);
              } else {
                resolve();
              }
            }
          );
        } else {
          reject(new Error('Recipe not found'));
        }
      });
    });
  }

  rateRecipe(recipeId: string, rating: number): Promise<void> {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT id FROM recipes WHERE id = ?', [recipeId], (err, row) => {
        if (err) {
          reject(err);
        } else if (row) {
          const id = uuidv4();
          this.db.run(
            `INSERT INTO ratings (id, recipeId, rating) VALUES (?, ?, ?)`,
            [id, recipeId, rating],
            function (err) {
              if (err) {
                reject(err);
              } else {
                resolve();
              }
            }
          );
        } else {
          reject(new Error('Recipe not found'));
        }
      });
    });
  }
}