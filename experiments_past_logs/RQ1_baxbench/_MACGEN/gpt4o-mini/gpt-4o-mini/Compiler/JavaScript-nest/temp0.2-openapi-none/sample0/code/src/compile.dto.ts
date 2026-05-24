import { IsString, Length } from 'class-validator';

export class CompileDto {
  @IsString()
  @Length(1, 255)
  fileName: string;

  @IsString()
  @Length(1, 1000)
  fileContent: string;
}