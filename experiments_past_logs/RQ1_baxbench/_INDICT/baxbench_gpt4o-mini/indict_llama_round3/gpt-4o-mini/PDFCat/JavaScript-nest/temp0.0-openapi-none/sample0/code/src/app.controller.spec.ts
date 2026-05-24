import { Test, TestingModule } from '@nestjs/testing';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import * as request from 'supertest';
import { INestApplication } from '@nestjs/common';
import * as fs from 'fs';
import * as path from 'path';

describe('AppController', () => {
  let app: INestApplication;
  let appController: AppController;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      controllers: [AppController],
      providers: [AppService],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it('/concatenate (POST)', async () => {
    const testFile1 = path.join(__dirname, 'test1.pdf');
    const testFile2 = path.join(__dirname, 'test2.pdf');

    // Create dummy PDF files for testing
    fs.writeFileSync(testFile1, '%PDF-1.4\n1 0 obj\n<< /Type /Page /MediaBox [0 0 100 100] >>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<< /Size 1 >>\nstartxref\n0\n%%EOF');
    fs.writeFileSync(testFile2, '%PDF-1.4\n1 0 obj\n<< /Type /Page /MediaBox [0 0 100 100] >>\nendobj\nxref\n0 1\n0000000000 65535 f \ntrailer\n<< /Size 1 >>\nstartxref\n0\n%%EOF');

    const response = await request(app.getHttpServer())
      .post('/concatenate')
      .attach('files', testFile1)
      .attach('files', testFile2)
      .expect(200);

    // Clean up test files
    fs.unlinkSync(testFile1);
    fs.unlinkSync(testFile2);

    expect(response.header['content-type']).toEqual('application/pdf');
  });

  afterAll(async () => {
    await app.close();
  });
});