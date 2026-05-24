class EntriesController < ApplicationController
  before_action :set_entry, only: [:show, :update, :edits]

  # GET /entries
  def index
    entries = Entry.select(:id, :title).map do |entry|
      { id: entry.id, title: entry.title, link: entry_url(entry) }
    end
    render json: entries, status: :ok
  end

  # POST /entries
  def create
    entry = Entry.new(entry_params)
    if entry.save
      render json: entry, status: :created
    else
      render json: { errors: entry.errors.full_messages }, status: :unprocessable_entity
    end
  end

  # GET /entries/:id
  def show
    render json: @entry, status: :ok
  end

  # PUT /entries/:id
  def update
    if @entry.update(update_params)
      render json: @entry, status: :ok
    else
      render json: { errors: @entry.errors.full_messages }, status: :unprocessable_entity
    end
  end

  # GET /entries/:id/edits
  def edits
    # Placeholder for edit history (not implemented in this example)
    render json: { message: "Edit history not implemented" }, status: :ok
  end

  private

  def set_entry
    @entry = Entry.find(params[:id])
  end

  def entry_params
    params.require(:entry).permit(:title, :content, :created_by)
  end

  def update_params
    params.require(:entry).permit(:content, :modified_by)
  end
end