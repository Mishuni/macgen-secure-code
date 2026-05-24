import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';
import { Recipe } from './recipe.interface';

@Injectable()
export class AppService {
  constructor(private readonly databaseService: DatabaseService) {}

  async getRecipes() {
    return this.databaseService.getRecipes();
  }

  async uploadRecipe(recipe: Recipe) {
    return this.databaseService.uploadRecipe(recipe);
  }

  async getRecipe(recipeId: string) {
    return this.databaseService.getRecipe(recipeId);
  }

  async addComment(recipeId: string, comment: string) {
    return this.databaseService.addComment(recipeId, comment);
  }

  async rateRecipe(recipeId: string, rating: number) {
    return this.databaseService.rateRecipe(recipeId, rating);
  }
}