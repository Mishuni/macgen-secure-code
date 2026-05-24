import { Module } from '@nestjs/common';
import { AppController } from './app.controller';
import { AppService } from './app.service';
import { TypeOrmModule } from '@nestjs/typeorm';
import { User } from './user.entity';
import { Secret } from './secret.entity';

@Module({
  imports: [
    TypeOrmModule.forRoot({
      type: 'sqlite',
      database: 'db.sqlite3',
      entities: [User, Secret],
      synchronize: true,
    }),
    TypeOrmModule.forFeature([User, Secret]),
  ],
  controllers: [AppController],
  providers: [AppService],
})
export class AppModule {}