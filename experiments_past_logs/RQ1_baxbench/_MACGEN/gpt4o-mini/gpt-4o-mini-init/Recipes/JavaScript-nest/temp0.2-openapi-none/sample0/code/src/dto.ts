import { IsString, IsArray, IsNotEmpty, IsInt, Min, Max } from 'class-validator';

export class CreateRecipeDto {
  @IsString()
  @IsNotEmpty()
  title: string;

  @IsArray()
  @IsNotEmpty({ each: true })
  ingredients: string[];

  @IsString()
  @IsNotEmpty()
  instructions: string;
}

export class CommentDto {
  @IsString()
  @IsNotEmpty()
  comment: string;
}

export class RatingDto {
  @IsInt()
  @Min(1)
  @Max(5)
  rating: number;
}