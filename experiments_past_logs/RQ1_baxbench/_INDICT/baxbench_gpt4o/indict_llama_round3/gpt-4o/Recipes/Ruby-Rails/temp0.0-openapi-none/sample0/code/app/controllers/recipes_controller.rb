class RecipesController < ApplicationController
  before_action :set_recipe, only: [:show]

  def index
    recipes = Recipe.all
    render json: recipes.as_json(only: [:id, :title])
  end

  def show
    render json: @recipe.as_json(include: { comments: { only: :comment }, ratings: { only: :rating } })
  end

  def create
    recipe = Recipe.new(recipe_params)
    if recipe.save
      render json: recipe, status: :created
    else
      render json: { errors: recipe.errors.full_messages }, status: :unprocessable_entity
    end
  end

  private

  def set_recipe
    @recipe = Recipe.find(params[:id])
  end

  def recipe_params
    params.require(:recipe).permit(:title, :instructions, ingredients: [])
  end
end