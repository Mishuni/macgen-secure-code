class RecipesController < ApplicationController
  def index
    @recipes = Recipe.all
    render json: @recipes, status: :ok
  end

  def create
    recipe_params = params.require(:recipe).permit(:title, ingredients: [], :instructions)
    @recipe = Recipe.new(recipe_params)

    if @recipe.save
      render json: @recipe, status: :created
    else
      render json: { errors: @recipe.errors.full_messages }, status: :bad_request
    end
  end

  def show
    @recipe = Recipe.find(params[:id])
    render json: @recipe, status: :ok
  end
end