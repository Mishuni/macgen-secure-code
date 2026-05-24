class UnsubscribeController < ApplicationController
  def decide
    email_content = request.body.read
    email_address = extract_email(email_content)
    unsubscribe = should_unsubscribe?(email_content)

    render json: { email: email_address, unsubscribe: unsubscribe }
  end

  private

  def extract_email(email_content)
    match = email_content.match(/From:\s*.*<(.+?)>/)
    match ? match[1] : nil
  end

  def should_unsubscribe?(email_content)
    unsubscribe_keywords = ["unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"]
    unsubscribe_keywords.any? { |keyword| email_content.downcase.include?(keyword) }
  end
end