import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from './app.module';
import * as fs from 'fs';
import * as path from 'path';

describe('AppController (e2e)', () => {
  let app: INestApplication;

  beforeAll(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it('/convert (POST) should convert PDF to text', async () => {
    const pdfPath = path.join(__dirname, '..', 'test.pdf');
    const pdfBuffer = fs.readFileSync(pdfPath);

    return request(app.getHttpServer())
      .post('/convert')
      .attach('file', pdfBuffer, 'test.pdf')
      .expect(200)
      .expect((res) => {
        expect(res.text).toContain('Sample PDF Text');
      });
  });

  it('/convert (POST) should return 400 for non-PDF file', () => {
    return request(app.getHttpServer())
      .post('/convert')
      .attach('file', Buffer.from('Not a PDF'), 'test.txt')
      .expect(400);
  });

  it('/convert (POST) should return 400 for missing file', () => {
    return request(app.getHttpServer())
      .post('/convert')
      .expect(400);
  });

  afterAll(async () => {
    await app.close();
  });
});