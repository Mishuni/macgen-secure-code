class RecipesController < ApplicationController
  def index
    recipes = Recipe.select(:id, :title).order(created_at: :desc)
    render json: recipes
  end

  def create
    recipe = Recipe.new(recipe_params)
    if recipe.save
      render json: recipe, status: :created
    else
      render json: { errors: recipe.errors.full_messages }, status: :unprocessable_entity
    end
  end

  def show
    recipe = Recipe.find(params[:id])
    render json: recipe
  end

  private

  def recipe_params
    params.require(:recipe).permit(:title, :instructions, ingredients: [])
  end
end