import { Controller, Get, Post, Body, Param, UsePipes, ValidationPipe } from '@nestjs/common';
import { AppService } from './app.service';
import { CreateRecipeDto, CommentDto, RatingDto } from './dto';

@Controller('recipes')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  getRecipes() {
    return this.appService.getRecipes();
  }

  @Post('upload')
  @UsePipes(new ValidationPipe())
  uploadRecipe(@Body() recipeData: CreateRecipeDto) {
    return this.appService.uploadRecipe(recipeData);
  }

  @Get(':recipeId')
  getRecipe(@Param('recipeId') recipeId: string) {
    return this.appService.getRecipe(recipeId);
  }

  @Post(':recipeId/comments')
  @UsePipes(new ValidationPipe())
  addComment(@Param('recipeId') recipeId: string, @Body() commentData: CommentDto) {
    return this.appService.addComment(recipeId, commentData);
  }

  @Post(':recipeId/ratings')
  @UsePipes(new ValidationPipe())
  rateRecipe(@Param('recipeId') recipeId: string, @Body() ratingData: RatingDto) {
    return this.appService.rateRecipe(recipeId, ratingData);
  }
}