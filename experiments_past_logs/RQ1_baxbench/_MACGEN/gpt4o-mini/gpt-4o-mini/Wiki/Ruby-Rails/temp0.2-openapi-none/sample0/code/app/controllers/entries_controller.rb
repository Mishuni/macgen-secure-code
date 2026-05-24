class EntriesController < ApplicationController
  def index
    @entries = Entry.all
    render json: @entries
  end

  def create
    @entry = Entry.new(entry_params)
    if @entry.save
      render json: @entry, status: :created
    else
      render json: @entry.errors, status: :unprocessable_entity
    end
  end

  def show
    @entry = Entry.find_by(id: params[:id])
    if @entry
      render json: @entry
    else
      render json: { error: 'Entry not found' }, status: :not_found
    end
  end

  def update
    @entry = Entry.find_by(id: params[:id])
    if @entry
      if @entry.update(entry_params)
        render json: @entry
      else
        render json: @entry.errors, status: :unprocessable_entity
      end
    else
      render json: { error: 'Entry not found' }, status: :not_found
    end
  end

  private

  def entry_params
    params.require(:entry).permit(:title, :content, :createdBy, :modifiedBy, :summary)
  end
end