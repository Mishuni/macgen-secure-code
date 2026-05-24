import {
  Controller,
  Get,
  Post,
  Put,
  Param,
  Body,
  HttpException,
  HttpStatus,
} from '@nestjs/common';
import { AppService } from './app.service';

@Controller('entries')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getAllEntries() {
    return await this.appService.getAllEntries();
  }

  @Post()
  async createEntry(@Body() body: any) {
    if (!body.title || !body.content || !body.createdBy) {
      throw new HttpException(
        'Missing required fields: title, content, createdBy',
        HttpStatus.BAD_REQUEST,
      );
    }
    return await this.appService.createEntry(body);
  }

  @Get(':entryId')
  async getEntry(@Param('entryId') entryId: string) {
    if (!entryId) {
      throw new HttpException('Entry ID is required', HttpStatus.BAD_REQUEST);
    }
    return await this.appService.getEntry(entryId);
  }

  @Put(':entryId')
  async updateEntry(@Param('entryId') entryId: string, @Body() body: any) {
    if (!entryId) {
      throw new HttpException('Entry ID is required', HttpStatus.BAD_REQUEST);
    }
    if (!body.content || !body.modifiedBy || !body.summary) {
      throw new HttpException(
        'Missing required fields: content, modifiedBy, summary',
        HttpStatus.BAD_REQUEST,
      );
    }
    return await this.appService.updateEntry(entryId, body);
  }

  @Get(':entryId/edits')
  async getEntryEdits(@Param('entryId') entryId: string) {
    if (!entryId) {
      throw new HttpException('Entry ID is required', HttpStatus.BAD_REQUEST);
    }
    return await this.appService.getEntryEdits(entryId);
  }
}