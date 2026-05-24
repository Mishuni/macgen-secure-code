class RatingsController < ApplicationController
  def create
    @recipe = Recipe.find(params[:recipe_id])
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

  def rating_params
    params.require(:rating).permit(:value)
  end
end