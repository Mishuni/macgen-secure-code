class ApplicationController < ActionController::API
  before_action :sanitize_params

  private

  def sanitize_params
    params.each do |key, value|
      params[key] = ActionController::Base.helpers.sanitize(value) if value.is_a?(String)
    end
  end
end