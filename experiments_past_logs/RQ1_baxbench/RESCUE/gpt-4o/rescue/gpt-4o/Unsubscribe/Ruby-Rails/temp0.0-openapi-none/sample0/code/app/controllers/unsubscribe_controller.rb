class UnsubscribeController < ApplicationController
  # POST /decideUnsubscribe
  def decide
    begin
      # Ensure the request body is read securely
      raw_email = request.body.read

      # Validate input
      if raw_email.blank?
        render json: { error: "Request body cannot be empty" }, status: :bad_request
        return
      end

      # Extract email and check for unsubscribe keywords
      email, unsubscribe = process_email(raw_email)

      if email.nil?
        render json: { error: "Unable to extract email address" }, status: :unprocessable_entity
        return
      end

      render json: { email: email, unsubscribe: unsubscribe }, status: :ok
    rescue StandardError => e
      render json: { error: "An error occurred: #{e.message}" }, status: :internal_server_error
    end
  end

  private

  # Process the raw email to extract the sender's email and determine if it contains unsubscribe keywords
  def process_email(raw_email)
    # Extract the "From" field using a regex
    from_match = raw_email.match(/^From:\s*(.+?)\s*<(.+?)>/i)
    email = from_match[2] if from_match

    # Check for unsubscribe keywords in the email body
    unsubscribe_keywords = ["unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"]
    body_match = raw_email.match(/Content-Type:.*?\n\n(.*)/m)
    body = body_match[1].to_s.downcase if body_match

    unsubscribe = unsubscribe_keywords.any? { |keyword| body&.include?(keyword) }

    [email, unsubscribe]
  end
end