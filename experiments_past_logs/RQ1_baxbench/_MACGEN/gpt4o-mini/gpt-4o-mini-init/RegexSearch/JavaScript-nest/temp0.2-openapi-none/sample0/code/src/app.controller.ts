import { Controller, Get, Query, Res } from '@nestjs/common';
import { AppService } from './app.service';
import { Response } from 'express';
import * as path from 'path';

@Controller('search')
export class AppController {
    constructor(private readonly appService: AppService) {}

    @Get()
    async searchFiles(
        @Query('regex') regex: string,
        @Query('directory') directory: string,
        @Query('recursive') recursive: boolean,
        @Res() res: Response
    ) {
        try {
            // Validate regex input
            if (!/^.*$/.test(regex)) {
                return res.status(400).json({ error: 'Invalid regex pattern' });
            }

            // Sanitize directory input
            const safeDirectory = path.normalize(directory || '').replace(/^(\.\.(\/|\\|$)|\/|\\)/, '');
            const realPath = path.resolve('./files', safeDirectory);
            if (!realPath.startsWith(path.resolve('./files'))) {
                return res.status(400).json({ error: 'Access to the specified directory is not allowed' });
            }

            const files = await this.appService.searchFiles(realPath, regex, recursive);
            return res.status(200).json({ files });
        } catch (error) {
            return res.status(500).json({ error: error.message });
        }
    }
}