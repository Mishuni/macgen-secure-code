import { Controller, Get, Post, Put, Param, Body, NotFoundException } from '@nestjs/common';
import { AppService } from './app.service';
import { NewEntryDto, UpdateEntryDto } from './dto';

@Controller('entries')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getAllEntries(): Promise<string> {
    return this.appService.getAllEntries();
  }

  @Post()
  async createEntry(@Body() newEntryDto: NewEntryDto): Promise<any> {
    return this.appService.createEntry(newEntryDto);
  }

  @Get(':entryId')
  async getEntry(@Param('entryId') entryId: string): Promise<string> {
    const entry = await this.appService.getEntry(entryId);
    if (!entry) {
      throw new NotFoundException('Entry not found');
    }
    return entry;
  }

  @Put(':entryId')
  async updateEntry(@Param('entryId') entryId: string, @Body() updateEntryDto: UpdateEntryDto): Promise<any> {
    const entry = await this.appService.updateEntry(entryId, updateEntryDto);
    if (!entry) {
      throw new NotFoundException('Entry not found');
    }
    return entry;
  }

  @Get(':entryId/edits')
  async getEntryEdits(@Param('entryId') entryId: string): Promise<string> {
    const edits = await this.appService.getEntryEdits(entryId);
    if (!edits) {
      throw new NotFoundException('Entry not found');
    }
    return edits;
  }
}