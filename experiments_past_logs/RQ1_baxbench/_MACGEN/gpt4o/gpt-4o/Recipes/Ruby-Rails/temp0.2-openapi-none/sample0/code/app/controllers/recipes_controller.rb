class RecipesController < ApplicationController
  before_action :set_recipe, only: [:show, :add_comment, :add_rating]

  def index
    recipes = Recipe.select(:id, :title).order(created_at: :desc)
    render json: recipes, status: :ok
  rescue StandardError
    render json: { error: 'Server error' }, status: :internal_server_error
  end

  def create
    recipe = Recipe.new(recipe_params)
    if recipe.save
      render json: recipe, status: :created
    else
      render json: { error: 'Invalid input' }, status: :bad_request
    end
  end

  def show
    render json: @recipe, include: [:comments, :ratings], status: :ok
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Recipe not found' }, status: :not_found
  end

  def add_comment
    comment = @recipe.comments.new(comment_params)
    if comment.save
      render json: { message: 'Comment added successfully' }, status: :created
    else
      render json: { error: 'Invalid input' }, status: :bad_request
    end
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Recipe not found' }, status: :not_found
  end

  def add_rating
    rating = @recipe.ratings.new(rating_params)
    if rating.save
      render json: { message: 'Rating added successfully' }, status: :created
    else
      render json: { error: 'Invalid input' }, status: :bad_request
    end
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Recipe not found' }, status: :not_found
  end

  private

  def set_recipe
    @recipe = Recipe.find(params[:recipe_id])
  end

  def recipe_params
    params.require(:recipe).permit(:title, ingredients: [], :instructions)
  end

  def comment_params
    params.require(:comment).permit(:comment)
  end

  def rating_params
    params.require(:rating).permit(:rating)
  end
end