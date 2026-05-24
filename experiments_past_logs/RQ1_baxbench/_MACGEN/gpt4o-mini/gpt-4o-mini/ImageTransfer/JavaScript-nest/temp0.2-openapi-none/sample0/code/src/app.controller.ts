import { Controller, Post, UploadedFile, UseInterceptors, Get, Param, Res, BadRequestException } from '@nestjs/common';
import { FileInterceptor } from '@nestjs/platform-express';
import { join } from 'path';
import { v4 as uuidv4 } from 'uuid';
import { Response } from 'express';
import * as fs from 'fs';

@Controller('images')
export class AppController {
    private readonly imagesDir = './uploads';

    constructor() {
        if (!fs.existsSync(this.imagesDir)) {
            fs.mkdirSync(this.imagesDir);
        }
    }

    @Post('upload')
    @UseInterceptors(FileInterceptor('file'))
    async uploadImage(@UploadedFile() file: Express.Multer.File) {
        const allowedTypes = ['image/jpeg', 'image/png', 'image/gif', 'image/webp', 'image/svg+xml'];
        if (!allowedTypes.includes(file.mimetype)) {
            throw new BadRequestException('Invalid file type');
        }
        const filePath = join(this.imagesDir, `${uuidv4()}.jpg`); // Ensure the extension matches the file type
        fs.writeFileSync(filePath, file.buffer);
        return { id: filePath }; // Return the file path as the identifier
    }

    @Get(':imageId')
    async getImage(@Param('imageId') imageId: string, @Res() res: Response) {
        const filePath = join(this.imagesDir, imageId);
        if (!fs.existsSync(filePath)) {
            return res.status(404).json({ error: 'Image not found' });
        }
        res.set('Content-Disposition', 'inline');
        return res.sendFile(filePath);
    }
}