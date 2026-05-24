class ApplicationController < ActionController::API
  private

  def product_params
    permitted_params = params.require(:product).permit(:name, additional_properties: {})
    validate_additional_properties(permitted_params[:additional_properties])
    permitted_params
  end

  def validate_additional_properties(additional_properties)
    if additional_properties.is_a?(Hash)
      additional_properties.each do |key, value|
        unless value.is_a?(String)
          raise ActionController::BadRequest, "Invalid value for #{key}: must be a string"
        end
      end
    end
  end
end