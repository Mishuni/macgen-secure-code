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

  it('/convert (POST) should convert zip to text', async () => {
    const zipFilePath = path.join(__dirname, '../test-files/test.zip');
    const response = await request(app.getHttpServer())
      .post('/convert')
      .attach('file', zipFilePath);

    expect(response.status).toBe(200);
    expect(response.text).toContain('This is a test file');
  });

  it('/convert (POST) should return 400 for non-zip file', async () => {
    const response = await request(app.getHttpServer())
      .post('/convert')
      .attach('file', Buffer.from('Not a zip file'), { filename: 'test.txt' });

    expect(response.status).toBe(400);
  });

  afterAll(async () => {
    await app.close();
  });
});