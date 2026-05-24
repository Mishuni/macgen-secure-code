export interface Recipe {
  id?: string;
  title: string;
  ingredients: string[];
  instructions: string;
  comments?: string[];
  avgRating?: number | null;
}