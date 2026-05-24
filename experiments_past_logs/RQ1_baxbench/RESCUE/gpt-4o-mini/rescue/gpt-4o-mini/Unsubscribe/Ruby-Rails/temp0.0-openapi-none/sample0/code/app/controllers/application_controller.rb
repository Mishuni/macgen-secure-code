class ApplicationController < ActionController::API
  # This method will handle the unsubscribe decision based on the email content
  def decide_unsubscribe
    email_content = request.body.read

    # Validate the content type
    if request.content_type != 'text/plain'
      render json: { error: 'Invalid content type' }, status: :unprocessable_entity and return
    end

    # Check for unsubscribe keywords
    unsubscribe_keywords = ["unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"]
    should_unsubscribe = unsubscribe_keywords.any? { |keyword| email_content.downcase.include?(keyword) }

    # Extract email address from the "From" header
    email_address = extract_email_address(email_content)

    # Return the response
    render json: { email: email_address, unsubscribe: should_unsubscribe }, status: :ok
  end

  private

  # Extracts the email address from the email content
  def extract_email_address(content)
    from_line = content.lines.find { |line| line.start_with?("From:") }
    return nil unless from_line

    # Extract the email address using a regex
    from_line[/<([^>]+)>/, 1] || from_line[/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,7}\b/]
  end
end