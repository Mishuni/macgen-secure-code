class CommentsController < ApplicationController
  def create
    @recipe = Recipe.find(params[:recipe_id])
    comment_params = params.require(:comment).permit(:comment)
    @comment = @recipe.comments.build(comment_params)

    if @comment.save
      render json: { message: 'Comment added successfully' }, status: :created
    else
      render json: { errors: @comment.errors.full_messages }, status: :bad_request
    end
  end
end