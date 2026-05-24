import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
    private readonly baseDir = path.resolve(__dirname, '../data');

    async searchFiles(searchContent?: string, searchFilename?: string, searchDir?: string) {
        const results: string[] = [];
        const searchPath = searchDir ? path.join(this.baseDir, searchDir) : this.baseDir;

        if (!fs.existsSync(searchPath) || !fs.lstatSync(searchPath).isDirectory()) {
            throw new Error('Invalid directory specified');
        }

        const files = fs.readdirSync(searchPath);

        for (const file of files) {
            const filePath = path.join(searchPath, file);
            if (fs.lstatSync(filePath).isDirectory()) {
                // Recursively search in subdirectories
                const subDirResults = await this.searchFiles(searchContent, searchFilename, path.join(searchDir || '', file));
                results.push(...subDirResults);
            } else {
                if (searchFilename && !file.includes(searchFilename)) {
                    continue;
                }
                if (searchContent) {
                    const fileContent = fs.readFileSync(filePath, 'utf-8');
                    if (fileContent.includes(searchContent)) {
                        results.push(filePath);
                    }
                } else {
                    results.push(filePath);
                }
            }
        }

        return { files: results };
    }
}