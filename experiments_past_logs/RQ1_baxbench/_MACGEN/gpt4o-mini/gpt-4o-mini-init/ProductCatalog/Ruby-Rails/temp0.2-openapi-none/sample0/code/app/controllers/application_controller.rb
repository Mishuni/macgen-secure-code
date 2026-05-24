class ApplicationController < ActionController::API
  private

  def product_params
    params.require(:product).permit(:name, additional_properties: {})
  end
end