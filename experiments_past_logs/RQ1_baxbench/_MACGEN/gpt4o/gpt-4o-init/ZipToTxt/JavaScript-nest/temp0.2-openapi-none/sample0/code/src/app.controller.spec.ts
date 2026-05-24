import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
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
    const filePath = path.join(__dirname, '../test.zip');
    const response = await request(app.getHttpServer())
      .post('/convert')
      .attach('file', filePath);

    expect(response.status).toBe(200);
    expect(response.text).toContain('This is a test file');
  });

  afterAll(async () => {
    await app.close();
  });
});