class ApplicationController < ActionController::API
  before_action :sanitize_params

  private

  def sanitize_params
    if params[:entry]
      params[:entry][:content] = ActionController::Base.helpers.sanitize(params[:entry][:content]) if params[:entry][:content]
      params[:entry][:title] = ActionController::Base.helpers.sanitize(params[:entry][:title]) if params[:entry][:title]
    end
  end
end