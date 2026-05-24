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
    try {
      const recipe = await this.appService.uploadRecipe(body);
      res.status(HttpStatus.CREATED).json(recipe);
    } catch (error) {
      res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
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
    try {
      await this.appService.addComment(recipeId, body.comment);
      res.status(HttpStatus.CREATED).send('Comment added successfully');
    } catch (error) {
      if (error.message === 'Recipe not found') {
        res.status(HttpStatus.NOT_FOUND).send('Recipe not found');
      } else {
        res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
      }
    }
  }

  @Post(':recipeId/ratings')
  async rateRecipe(@Param('recipeId') recipeId: string, @Body() body: any, @Res() res: Response) {
    try {
      await this.appService.rateRecipe(recipeId, body.rating);
      res.status(HttpStatus.CREATED).send('Rating added successfully');
    } catch (error) {
      if (error.message === 'Recipe not found') {
        res.status(HttpStatus.NOT_FOUND).send('Recipe not found');
      } else {
        res.status(HttpStatus.BAD_REQUEST).send('Invalid input');
      }
    }
  }
}