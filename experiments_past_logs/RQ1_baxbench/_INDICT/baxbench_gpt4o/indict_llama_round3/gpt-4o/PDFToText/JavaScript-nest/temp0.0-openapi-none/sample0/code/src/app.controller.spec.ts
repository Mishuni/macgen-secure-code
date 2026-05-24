import { Test, TestingModule } from '@nestjs/testing';
import * as request from 'supertest';
import { INestApplication } from '@nestjs/common';
import { AppModule } from './app.module';
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

  it('/convert (POST)', async () => {
    const pdfPath = path.join(__dirname, '..', 'test.pdf');
    const response = await request(app.getHttpServer())
      .post('/convert')
      .attach('file', pdfPath);

    expect(response.status).toBe(200);
    expect(response.text).toContain('Sample PDF Content');
  });

  afterAll(async () => {
    await app.close();
  });
});