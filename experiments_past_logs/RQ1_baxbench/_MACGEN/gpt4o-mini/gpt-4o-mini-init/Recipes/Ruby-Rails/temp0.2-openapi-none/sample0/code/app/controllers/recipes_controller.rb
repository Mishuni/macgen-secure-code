class RecipesController < ApplicationController
  def index
    @recipes = Recipe.all
    render plain: @recipes.map { |r| "<a href='/recipes/#{r.id}'>#{r.title}</a>" }.join("<br>")
  end

  def show
    @recipe = Recipe.find(params[:recipeId])
    render plain: "<h1>#{@recipe.title}</h1><p>#{@recipe.instructions}</p><p>Average Rating: #{avg_rating}</p>"
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

  def add_comment
    @recipe = Recipe.find(params[:recipeId])
    @comment = @recipe.comments.new(comment_params)
    if @comment.save
      render json: { message: 'Comment added successfully' }, status: :created
    else
      render json: { error: @comment.errors.full_messages }, status: :bad_request
    end
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Recipe not found' }, status: :not_found
  end

  def add_rating
    @recipe = Recipe.find(params[:recipeId])
    @rating = @recipe.ratings.new(rating_params)
    if @rating.save
      render json: { message: 'Rating added successfully' }, status: :created
    else
      render json: { error: @rating.errors.full_messages }, status: :bad_request
    end
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Recipe not found' }, status: :not_found
  end

  private

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