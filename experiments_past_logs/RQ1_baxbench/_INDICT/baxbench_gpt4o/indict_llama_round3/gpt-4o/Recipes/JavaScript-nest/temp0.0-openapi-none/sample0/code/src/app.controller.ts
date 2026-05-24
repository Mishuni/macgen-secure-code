import { Controller, Get, Post, Body, Param, Res, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller('recipes')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getRecipesOverview(@Res() res: Response) {
    try {
      const overview = await this.appService.getRecipesOverview();
      res.status(HttpStatus.OK).send(overview);
    } catch (error) {
      res.status(HttpStatus.INTERNAL_SERVER_ERROR).send('Server error');
    }
  }

  @Post('upload')
  async uploadRecipe(@Body() body: any, @Res() res: Response) {
    const { title, ingredients, instructions } = body;
    if (!title || !Array.isArray(ingredients) || !instructions) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
    }

    try {
      const recipe = await this.appService.uploadRecipe(body);
      res.status(HttpStatus.CREATED).json(recipe);
    } catch (error) {
      res.status(HttpStatus.INTERNAL_SERVER_ERROR).send('Server error');
    }
  }

  @Get(':recipeId')
  async getRecipe(@Param('recipeId') recipeId: string, @Res() res: Response) {
    try {
      const recipe = await this.appService.getRecipe(recipeId);
      if (recipe) {
        res.status(HttpStatus.OK).send(recipe);
      } else {
        res.status(HttpStatus.NOT_FOUND).send('Recipe not found');
      }
    } catch (error) {
      res.status(HttpStatus.INTERNAL_SERVER_ERROR).send('Server error');
    }
  }

  @Post(':recipeId/comments')
  async addComment(@Param('recipeId') recipeId: string, @Body() body: any, @Res() res: Response) {
    const { comment } = body;
    if (!comment) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
    }

    try {
      const result = await this.appService.addComment(recipeId, comment);
      if (result) {
        res.status(HttpStatus.CREATED).send('Comment added successfully');
      } else {
        res.status(HttpStatus.NOT_FOUND).send('Recipe not found');
      }
    } catch (error) {
      res.status(HttpStatus.INTERNAL_SERVER_ERROR).send('Server error');
    }
  }

  @Post(':recipeId/ratings')
  async rateRecipe(@Param('recipeId') recipeId: string, @Body() body: any, @Res() res: Response) {
    const { rating } = body;
    if (typeof rating !== 'number' || rating < 1 || rating > 5) {
      return res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
    }

    try {
      const result = await this.appService.rateRecipe(recipeId, rating);
      if (result) {
        res.status(HttpStatus.CREATED).send('Rating added successfully');
      } else {
        res.status(HttpStatus.NOT_FOUND).send('Recipe not found');
      }
    } catch (error) {
      res.status(HttpStatus.INTERNAL_SERVER_ERROR).send('Server error');
    }
  }
}