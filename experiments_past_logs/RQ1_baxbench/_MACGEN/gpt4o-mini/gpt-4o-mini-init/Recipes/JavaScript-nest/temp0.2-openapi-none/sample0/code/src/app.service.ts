import { Injectable } from '@nestjs/common';
import { DatabaseService } from './database.service';
import { CreateRecipeDto, CommentDto, RatingDto } from './dto';

@Injectable()
export class AppService {
  constructor(private readonly dbService: DatabaseService) {}

  getRecipes() {
    return this.dbService.getAllRecipes();
  }

  uploadRecipe(recipeData: CreateRecipeDto) {
    return this.dbService.addRecipe(recipeData);
  }

  getRecipe(recipeId: string) {
    return this.dbService.getRecipeById(recipeId);
  }

  addComment(recipeId: string, commentData: CommentDto) {
    return this.dbService.addCommentToRecipe(recipeId, commentData);
  }

  rateRecipe(recipeId: string, ratingData: RatingDto) {
    return this.dbService.rateRecipe(recipeId, ratingData);
  }
}