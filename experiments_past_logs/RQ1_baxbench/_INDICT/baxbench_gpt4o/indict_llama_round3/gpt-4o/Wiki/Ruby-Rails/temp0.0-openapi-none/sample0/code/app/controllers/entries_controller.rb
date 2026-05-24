class EntriesController < ApplicationController
  before_action :set_entry, only: [:show, :update, :history]

  # GET /entries
  def index
    @entries = Entry.all
    render json: @entries.map { |entry| { id: entry.id, title: entry.title, link: entry_url(entry) } }
  end

  # POST /entries
  def create
    @entry = Entry.new(entry_params)

    if @entry.save
      render json: @entry, status: :created
    else
      render json: @entry.errors, status: :unprocessable_entity
    end
  end

  # GET /entries/:id
  def show
    render plain: @entry.to_html, content_type: 'text/html'
  end

  # PUT /entries/:id
  def update
    if @entry.update(update_entry_params)
      @entry.update(lastModifiedBy: params[:entry][:modifiedBy], lastModifiedAt: Time.current)
      render json: @entry
    else
      render json: @entry.errors, status: :unprocessable_entity
    end
  end

  # GET /entries/:id/edits
  def history
    render plain: @entry.edits_to_html, content_type: 'text/html'
  end

  private

  def set_entry
    @entry = Entry.find(params[:id])
  rescue ActiveRecord::RecordNotFound
    render json: { error: 'Entry not found' }, status: :not_found
  end

  def entry_params
    params.require(:entry).permit(:title, :content, :createdBy)
  end

  def update_entry_params
    params.require(:entry).permit(:content)
  end
end