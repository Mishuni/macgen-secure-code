import { Controller, Get, Post, Body, Param, Put } from '@nestjs/common';
import { EntriesService } from './entries.service';
import { NewEntry, UpdateEntry } from './entry.dto';

@Controller('entries')
export class EntriesController {
  constructor(private readonly entriesService: EntriesService) {}

  @Get()
  getAllEntries() {
    return this.entriesService.getAllEntries();
  }

  @Post()
  createEntry(@Body() newEntry: NewEntry) {
    return this.entriesService.createEntry(newEntry);
  }

  @Get(':entryId')
  getEntry(@Param('entryId') entryId: string) {
    return this.entriesService.getEntry(entryId);
  }

  @Put(':entryId')
  updateEntry(@Param('entryId') entryId: string, @Body() updateEntry: UpdateEntry) {
    return this.entriesService.updateEntry(entryId, updateEntry);
  }
}