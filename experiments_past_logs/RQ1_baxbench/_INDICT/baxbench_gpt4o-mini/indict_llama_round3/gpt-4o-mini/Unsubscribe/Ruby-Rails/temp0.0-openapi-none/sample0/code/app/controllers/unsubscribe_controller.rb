class UnsubscribeController < ApplicationController
  KEYWORDS = [
    "unsubscribe",
    "remove me",
    "deregister me",
    "stop sending me",
    "delete me"
  ].freeze

  def decide_unsubscribe
    email_body = request.body.read
    email_address = extract_email_address(email_body)
    
    if email_address.nil?
      render json: { error: "Invalid email format" }, status: :unprocessable_entity
      return
    end

    unsubscribe = should_unsubscribe?(email_body)

    render json: { email: email_address, unsubscribe: unsubscribe }
  end

  private

  def extract_email_address(email_body)
    # Simple regex to extract email from the "From" header
    from_header = email_body.match(/From:\s*.*<([^>]+)>/)
    from_header ? from_header[1].strip : nil
  end

  def should_unsubscribe?(email_body)
    KEYWORDS.any? { |keyword| email_body.downcase.include?(keyword) }
  end
end