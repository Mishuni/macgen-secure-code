class UnsubscribeController < ApplicationController
  UNSUBSCRIBE_KEYWORDS = [
    "unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"
  ].freeze

  def decide
    raw_email = request.body.read
    email = extract_email(raw_email)
    unsubscribe = should_unsubscribe?(raw_email)

    render json: { email: email, unsubscribe: unsubscribe }
  end

  private

  def extract_email(raw_email)
    # Simple regex to extract email from the raw email content
    if raw_email.match(/From:\s*([^<\s]+<([^>]+)>|([^<\s]+))/)
      $2 || $3
    else
      nil
    end
  end

  def should_unsubscribe?(raw_email)
    UNSUBSCRIBE_KEYWORDS.any? { |keyword| raw_email.downcase.include?(keyword) }
  end
end