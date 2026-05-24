import { Controller, Get, Post, Body, Param, Put, HttpException, HttpStatus } from '@nestjs/common';
import { AppService } from './app.service';
import { NewEntry, UpdateEntry } from './entry.schema';

@Controller('entries')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  async getEntries() {
    return this.appService.getAllEntries();
  }

  @Post()
  async createEntry(@Body() newEntry: NewEntry) {
    // Input validation
    if (!newEntry.title || !newEntry.content || !newEntry.createdBy) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }
    
    // Input sanitization
    newEntry.title = newEntry.title.replace(/</g, "&lt;").replace(/>/g, "&gt;");
    newEntry.content = newEntry.content.replace(/</g, "&lt;").replace(/>/g, "&gt;");

    return this.appService.createEntry(newEntry);
  }

  @Get(':entryId')
  async getEntry(@Param('entryId') entryId: string) {
    const entry = await this.appService.getEntry(entryId);
    if (!entry) {
      throw new HttpException('Entry not found', HttpStatus.NOT_FOUND);
    }
    return entry;
  }

  @Put(':entryId')
  async updateEntry(@Param('entryId') entryId: string, @Body() updateEntry: UpdateEntry) {
    // Input validation
    if (!updateEntry.content || !updateEntry.modifiedBy) {
      throw new HttpException('Invalid input', HttpStatus.BAD_REQUEST);
    }

    // Input sanitization
    updateEntry.content = updateEntry.content.replace(/</g, "&lt;").replace(/>/g, "&gt;");

    const entry = await this.appService.updateEntry(entryId, updateEntry);
    if (!entry) {
      throw new HttpException('Entry not found', HttpStatus.NOT_FOUND);
    }
    return entry;
  }
}