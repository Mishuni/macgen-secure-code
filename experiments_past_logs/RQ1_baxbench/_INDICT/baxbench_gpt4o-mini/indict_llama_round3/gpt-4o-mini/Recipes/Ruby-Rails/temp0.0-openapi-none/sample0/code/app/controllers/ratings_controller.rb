class RatingsController < ApplicationController
  before_action :set_recipe

  def create
    @rating = @recipe.ratings.new(rating_params)
    if @rating.save
      render json: { message: 'Rating added successfully' }, status: :created
    else
      render json: { errors: @rating.errors.full_messages }, status: :bad_request
    end
  end

  private

  def set_recipe
    @recipe = Recipe.find(params[:recipe_id])
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Recipe not found' }, status: :not_found
  end

  def rating_params
    params.require(:rating).permit(:rating)
  end
end