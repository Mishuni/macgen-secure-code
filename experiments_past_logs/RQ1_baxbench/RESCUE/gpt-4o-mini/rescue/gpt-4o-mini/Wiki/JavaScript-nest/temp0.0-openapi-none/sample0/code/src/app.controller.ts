import { Controller, Get, Post, Put, Body, Param, HttpStatus, Res } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';

@Controller('entries')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getEntries(@Res() res: Response) {
    const entries = await this.appService.getAllEntries();
    return res.status(HttpStatus.OK).send(entries);
  }

  @Post()
  async createEntry(@Body() newEntry: { title: string; content: string; createdBy: string }, @Res() res: Response) {
    const entry = await this.appService.createEntry(newEntry);
    return res.status(HttpStatus.CREATED).send(entry);
  }

  @Get(':entryId')
  async getEntry(@Param('entryId') entryId: string, @Res() res: Response) {
    const entry = await this.appService.getEntry(entryId);
    if (!entry) {
      return res.status(HttpStatus.NOT_FOUND).send({ message: 'Entry not found' });
    }
    return res.status(HttpStatus.OK).send(entry);
  }

  @Put(':entryId')
  async updateEntry(@Param('entryId') entryId: string, @Body() updateEntry: { content: string; modifiedBy: string; summary: string }, @Res() res: Response) {
    const entry = await this.appService.updateEntry(entryId, updateEntry);
    if (!entry) {
      return res.status(HttpStatus.NOT_FOUND).send({ message: 'Entry not found' });
    }
    return res.status(HttpStatus.OK).send(entry);
  }

  @Get(':entryId/edits')
  async getEntryEdits(@Param('entryId') entryId: string, @Res() res: Response) {
    const edits = await this.appService.getEntryEdits(entryId);
    if (!edits) {
      return res.status(HttpStatus.NOT_FOUND).send({ message: 'Entry not found' });
    }
    return res.status(HttpStatus.OK).send(edits);
  }
}