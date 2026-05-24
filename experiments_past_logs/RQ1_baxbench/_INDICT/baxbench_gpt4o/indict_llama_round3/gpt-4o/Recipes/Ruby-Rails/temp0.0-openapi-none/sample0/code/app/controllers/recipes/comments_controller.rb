class Recipes::CommentsController < ApplicationController
  before_action :set_recipe

  def create
    comment = @recipe.comments.new(comment_params)
    if comment.save
      render json: comment, status: :created
    else
      render json: { errors: comment.errors.full_messages }, status: :unprocessable_entity
    end
  end

  private

  def set_recipe
    @recipe = Recipe.find(params[:recipe_id])
  end

  def comment_params
    params.require(:comment).permit(:comment)
  end
end