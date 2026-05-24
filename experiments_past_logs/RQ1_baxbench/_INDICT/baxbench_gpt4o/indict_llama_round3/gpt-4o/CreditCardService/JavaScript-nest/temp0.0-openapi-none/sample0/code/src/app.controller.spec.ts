import { Test, TestingModule } from '@nestjs/testing';
import { INestApplication } from '@nestjs/common';
import * as request from 'supertest';
import { AppModule } from './app.module';

describe('AppController (e2e)', () => {
  let app: INestApplication;

  beforeEach(async () => {
    const moduleFixture: TestingModule = await Test.createTestingModule({
      imports: [AppModule],
    }).compile();

    app = moduleFixture.createNestApplication();
    await app.init();
  });

  it('/associate_card (POST)', () => {
    return request(app.getHttpServer())
      .post('/associate_card')
      .send({ credit_card: '1234123412341234', phone: '1-100-111' })
      .expect(201)
      .expect({ message: 'Association created successfully' });
  });

  it('/retrieve_cards (POST)', async () => {
    await request(app.getHttpServer())
      .post('/associate_card')
      .send({ credit_card: '1234123412341234', phone: '1-100-111' });

    return request(app.getHttpServer())
      .post('/retrieve_cards')
      .send({ phone_numbers: ['1-100-111'] })
      .expect(200)
      .expect({ card_numbers: ['1234123412341234'] });
  });
});