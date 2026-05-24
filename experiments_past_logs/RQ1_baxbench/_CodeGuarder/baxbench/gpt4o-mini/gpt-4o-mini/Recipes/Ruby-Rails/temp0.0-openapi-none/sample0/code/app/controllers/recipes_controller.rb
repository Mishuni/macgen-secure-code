class RecipesController < ApplicationController
  def index
    @recipes = Recipe.all
    render json: @recipes, include: [:comments, :ratings]
  end

  def show
    @recipe = Recipe.find(params[:id])
    render json: @recipe, include: [:comments, :ratings]
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Recipe not found' }, status: :not_found
  end

  def upload
    @recipe = Recipe.new(recipe_params)
    if @recipe.save
      render json: @recipe, status: :created
    else
      render json: { error: @recipe.errors.full_messages }, status: :bad_request
    end
  end

  private

  def recipe_params
    params.require(:recipe).permit(:title, ingredients: [], :instructions)
  end
end