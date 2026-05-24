class ConvertController < ApplicationController
  def create
    uploaded_file = params[:file]

    # Validate file type
    raise 'Invalid file type' unless uploaded_file.content_type == 'application/zip'
    raise 'File too large' if uploaded_file.size > 5.megabytes

    # Process the zip file
    service = ZipToTextService.new(uploaded_file)
    text_content = service.convert

    render plain: text_content, status: :ok
  rescue => e
    render json: { error: e.message }, status: :bad_request
  end
end