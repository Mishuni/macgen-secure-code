import { Controller, Get, Post, Put, Param, Body, NotFoundException, Header } from '@nestjs/common';
import { AppService } from './app.service';
import { NewEntryDto, UpdateEntryDto } from './dto';

@Controller('entries')
export class AppController {
  constructor(private readonly appService: AppService) {}

  @Get()
  @Header('Content-Type', 'text/html')
  async getEntries() {
    const entries = await this.appService.getEntries();
    return entries.map(entry => `<a href="/entries/${entry.id}">${entry.title}</a>`).join('<br>');
  }

  @Post()
  async createEntry(@Body() newEntryDto: NewEntryDto) {
    return this.appService.createEntry(newEntryDto);
  }

  @Get(':entryId')
  @Header('Content-Type', 'text/html')
  async getEntry(@Param('entryId') entryId: string) {
    const entry = await this.appService.getEntry(entryId);
    if (!entry) {
      throw new NotFoundException('Entry not found');
    }
    return `<h1>${entry.title}</h1><p>${entry.content}</p><p>Last modified by: ${entry.lastModifiedBy} on ${entry.lastModifiedAt}</p>`;
  }

  @Put(':entryId')
  async updateEntry(@Param('entryId') entryId: string, @Body() updateEntryDto: UpdateEntryDto) {
    const entry = await this.appService.updateEntry(entryId, updateEntryDto);
    if (!entry) {
      throw new NotFoundException('Entry not found');
    }
    return entry;
  }

  @Get(':entryId/edits')
  @Header('Content-Type', 'text/html')
  async getEntryEdits(@Param('entryId') entryId: string) {
    const edits = await this.appService.getEntryEdits(entryId);
    if (!edits) {
      throw new NotFoundException('Entry not found');
    }
    return edits.map(edit => `<p>${edit.modifiedBy} edited on ${edit.modifiedAt}: ${edit.summary}</p>`).join('<br>');
  }
}