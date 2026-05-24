import {
  Controller,
  Get,
  Post,
  Body,
  Param,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { AppService } from './app.service';

@Controller('recipes')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getRecipesOverview(): Promise<string> {
    try {
      return await this.appService.getRecipesOverview();
    } catch (error) {
      throw new HttpException('Internal Server Error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  @Post('upload')
  async uploadRecipe(
    @Body('title') title: string,
    @Body('ingredients') ingredients: string[],
    @Body('instructions') instructions: string,
  ): Promise<object> {
    if (!title || !ingredients || !instructions) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }

    try {
      const recipe = await this.appService.uploadRecipe(title, ingredients, instructions);
      return recipe;
    } catch (error) {
      throw new HttpException('Internal Server Error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  @Get(':recipeId')
  async getRecipe(@Param('recipeId') recipeId: string): Promise<string> {
    try {
      const recipe = await this.appService.getRecipe(recipeId);
      if (!recipe) {
        throw new HttpException('Recipe not found', HttpStatus.NOT_FOUND);
      }
      return recipe;
    } catch (error) {
      throw new HttpException('Internal Server Error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  @Post(':recipeId/comments')
  async addComment(
    @Param('recipeId') recipeId: string,
    @Body('comment') comment: string,
  ): Promise<object> {
    if (!comment) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }

    try {
      const result = await this.appService.addComment(recipeId, comment);
      if (!result) {
        throw new HttpException('Recipe not found', HttpStatus.NOT_FOUND);
      }
      return result;
    } catch (error) {
      throw new HttpException('Internal Server Error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }

  @Post(':recipeId/ratings')
  async addRating(
    @Param('recipeId') recipeId: string,
    @Body('rating') rating: number,
  ): Promise<object> {
    if (!rating || rating < 1 || rating > 5) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }

    try {
      const result = await this.appService.addRating(recipeId, rating);
      if (!result) {
        throw new HttpException('Recipe not found', HttpStatus.NOT_FOUND);
      }
      return result;
    } catch (error) {
      throw new HttpException('Internal Server Error', HttpStatus.INTERNAL_SERVER_ERROR);
    }
  }
}