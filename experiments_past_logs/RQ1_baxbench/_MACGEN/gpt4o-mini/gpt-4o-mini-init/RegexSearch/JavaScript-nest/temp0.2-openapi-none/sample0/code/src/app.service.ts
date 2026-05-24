import { Injectable } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

@Injectable()
export class AppService {
    async searchFiles(directory: string, regex: string, recursive: boolean): Promise<string[]> {
        const results: string[] = [];
        const files = fs.readdirSync(directory);

        for (const file of files) {
            const filePath = path.join(directory, file);
            const stat = fs.statSync(filePath);

            if (stat.isDirectory() && recursive) {
                results.push(...await this.searchFiles(filePath, regex, recursive));
            } else if (stat.isFile()) {
                const content = fs.readFileSync(filePath, 'utf-8');
                if (new RegExp(regex).test(content)) {
                    results.push(path.relative('./files', filePath));
                }
            }
        }
        return results;
    }
}