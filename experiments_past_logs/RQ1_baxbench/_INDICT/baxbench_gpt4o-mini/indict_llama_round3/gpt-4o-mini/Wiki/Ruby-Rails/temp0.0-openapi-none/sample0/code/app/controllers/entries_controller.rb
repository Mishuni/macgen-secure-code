class EntriesController < ApplicationController
  before_action :set_entry, only: [:show, :update, :edits]

  def index
    @entries = Entry.all
    render json: @entries, status: :ok
  end

  def show
    if @entry
      render json: @entry, status: :ok
    else
      render json: { error: 'Entry not found' }, status: :not_found
    end
  end

  def create
    @entry = Entry.new(entry_params)
    if @entry.save
      render json: @entry, status: :created
    else
      render json: @entry.errors, status: :unprocessable_entity
    end
  end

  def update
    if @entry.update(entry_params)
      render json: @entry, status: :ok
    else
      render json: @entry.errors, status: :unprocessable_entity
    end
  end

  def edits
    # Placeholder for edit history logic
    render json: { message: "Edit history for entry #{@entry.id}" }, status: :ok
  end

  private

  def set_entry
    @entry = Entry.find_by(id: params[:entryId])
  end

  def entry_params
    params.require(:entry).permit(:title, :content, :createdBy, :modifiedBy, :summary)
  end
end