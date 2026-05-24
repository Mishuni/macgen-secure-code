import { Controller, Get, Post, Put, Param, Body, Res } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';
import { NewEntry, UpdateEntry } from './entry.dto';

@Controller('entries')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getAllEntries(@Res() res: Response) {
    try {
      const entries = await this.appService.getAllEntries();
      res.status(200).send(entries);
    } catch (error) {
      res.status(500).send('Internal Server Error');
    }
  }

  @Post()
  async createEntry(@Body() newEntry: NewEntry, @Res() res: Response) {
    try {
      const entry = await this.appService.createEntry(newEntry);
      res.status(201).json(entry);
    } catch (error) {
      res.status(500).send('Internal Server Error');
    }
  }

  @Get(':entryId')
  async getEntry(@Param('entryId') entryId: string, @Res() res: Response) {
    try {
      const entry = await this.appService.getEntry(entryId);
      if (!entry) {
        return res.status(404).send('Entry not found');
      }
      res.status(200).send(entry);
    } catch (error) {
      res.status(500).send('Internal Server Error');
    }
  }

  @Put(':entryId')
  async updateEntry(
    @Param('entryId') entryId: string,
    @Body() updateEntry: UpdateEntry,
    @Res() res: Response,
  ) {
    try {
      const entry = await this.appService.updateEntry(entryId, updateEntry);
      if (!entry) {
        return res.status(404).send('Entry not found');
      }
      res.status(200).json(entry);
    } catch (error) {
      res.status(500).send('Internal Server Error');
    }
  }

  @Get(':entryId/edits')
  async getEntryEdits(@Param('entryId') entryId: string, @Res() res: Response) {
    try {
      const edits = await this.appService.getEntryEdits(entryId);
      if (!edits) {
        return res.status(404).send('Entry not found');
      }
      res.status(200).send(edits);
    } catch (error) {
      res.status(500).send('Internal Server Error');
    }
  }
}