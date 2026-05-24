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
            comments TEXT,
            avgRating REAL
          )`,
          (err) => {
            if (err) {
              console.error('Error creating table', err.message);
            }
          },
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

  uploadRecipe(recipeData: any): Promise<any> {
    return new Promise((resolve, reject) => {
      const { title, ingredients, instructions } = recipeData;
      const id = uuidv4();
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
        },
      );
    });
  }

  getRecipe(recipeId: string): Promise<string | null> {
    return new Promise((resolve, reject) => {
      this.db.get('SELECT * FROM recipes WHERE id = ?', [recipeId], (err, row) => {
        if (err) {
          reject(err);
        } else if (row) {
          const recipeHtml = `
            <h1>${row.title}</h1>
            <h2>Ingredients</h2>
            <ul>${JSON.parse(row.ingredients).map((ing: string) => `<li>${ing}</li>`).join('')}</ul>
            <h2>Instructions</h2>
            <p>${row.instructions}</p>
            <h2>Comments</h2>
            <p>${row.comments || 'No comments yet'}</p>
            <h2>Average Rating</h2>
            <p>${row.avgRating || 'Not rated yet'}</p>
          `;
          resolve(recipeHtml);
        } else {
          resolve(null);
        }
      });
    });
  }

  addComment(recipeId: string, commentData: any): Promise<boolean> {
    return new Promise((resolve, reject) => {
      const { comment } = commentData;
      this.db.get('SELECT comments FROM recipes WHERE id = ?', [recipeId], (err, row) => {
        if (err) {
          reject(err);
        } else if (row) {
          const comments = row.comments ? JSON.parse(row.comments) : [];
          comments.push({ comment });
          this.db.run(
            'UPDATE recipes SET comments = ? WHERE id = ?',
            [JSON.stringify(comments), recipeId],
            function (err) {
              if (err) {
                reject(err);
              } else {
                resolve(true);
              }
            },
          );
        } else {
          resolve(false);
        }
      });
    });
  }

  rateRecipe(recipeId: string, ratingData: any): Promise<boolean> {
    return new Promise((resolve, reject) => {
      const { rating } = ratingData;
      this.db.get('SELECT avgRating FROM recipes WHERE id = ?', [recipeId], (err, row) => {
        if (err) {
          reject(err);
        } else if (row) {
          const newAvgRating = row.avgRating ? (row.avgRating + rating) / 2 : rating;
          this.db.run(
            'UPDATE recipes SET avgRating = ? WHERE id = ?',
            [newAvgRating, recipeId],
            function (err) {
              if (err) {
                reject(err);
              } else {
                resolve(true);
              }
            },
          );
        } else {
          resolve(false);
        }
      });
    });
  }
}