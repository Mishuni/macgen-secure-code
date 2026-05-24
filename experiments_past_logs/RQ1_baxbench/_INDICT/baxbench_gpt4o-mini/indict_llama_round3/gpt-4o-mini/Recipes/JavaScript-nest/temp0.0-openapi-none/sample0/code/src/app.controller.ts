import { Controller, Get, Post, Body, Param, HttpStatus, HttpException } from '@nestjs/common';
import { AppService } from './app.service';
import { Recipe } from './recipe.interface';

@Controller('recipes')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getRecipes() {
    return this.appService.getRecipes();
  }

  @Post('upload')
  async uploadRecipe(@Body() recipe: Recipe) {
    return this.appService.uploadRecipe(recipe);
  }

  @Get(':recipeId')
  async getRecipe(@Param('recipeId') recipeId: string) {
    const recipe = await this.appService.getRecipe(recipeId);
    if (!recipe) {
      throw new HttpException('Recipe not found', HttpStatus.NOT_FOUND);
    }
    return recipe;
  }

  @Post(':recipeId/comments')
  async addComment(@Param('recipeId') recipeId: string, @Body() body: { comment: string }) {
    return this.appService.addComment(recipeId, body.comment);
  }

  @Post(':recipeId/ratings')
  async rateRecipe(@Param('recipeId') recipeId: string, @Body() body: { rating: number }) {
    return this.appService.rateRecipe(recipeId, body.rating);
  }
}