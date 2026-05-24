import { Controller, Get, Post, Body, Param, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Recipe } from './recipe.interface';

@Controller('recipes')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getRecipes(): string {
    return this.appService.getRecipes();
  }

  @Post('upload')
  async uploadRecipe(@Body() recipeData: Recipe): Promise<Recipe> {
    if (!recipeData.title || !recipeData.ingredients || !recipeData.instructions) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }
    return this.appService.uploadRecipe(recipeData);
  }

  @Get(':recipeId')
  async getRecipe(@Param('recipeId') recipeId: string): Promise<Recipe> {
    const recipe = await this.appService.getRecipe(recipeId);
    if (!recipe) {
      throw new HttpException('Recipe not found', HttpStatus.NOT_FOUND);
    }
    return recipe;
  }

  @Post(':recipeId/comments')
  async addComment(@Param('recipeId') recipeId: string, @Body() commentData: { comment: string }): Promise<void> {
    if (!commentData.comment) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }
    const result = await this.appService.addComment(recipeId, commentData.comment);
    if (!result) {
      throw new HttpException('Recipe not found', HttpStatus.NOT_FOUND);
    }
  }

  @Post(':recipeId/ratings')
  async rateRecipe(@Param('recipeId') recipeId: string, @Body() ratingData: { rating: number }): Promise<void> {
    if (ratingData.rating < 1 || ratingData.rating > 5) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }
    const result = await this.appService.rateRecipe(recipeId, ratingData.rating);
    if (!result) {
      throw new HttpException('Recipe not found', HttpStatus.NOT_FOUND);
    }
  }
}