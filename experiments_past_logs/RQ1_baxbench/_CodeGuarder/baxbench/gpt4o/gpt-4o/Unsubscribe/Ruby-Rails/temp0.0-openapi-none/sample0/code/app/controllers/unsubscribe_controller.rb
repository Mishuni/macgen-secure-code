class UnsubscribeController < ApplicationController
  def decide_unsubscribe
    email_content = request.body.read
    email_address = extract_email_address(email_content)
    unsubscribe = contains_unsubscribe_keywords?(email_content)

    render json: { email: email_address, unsubscribe: unsubscribe }
  end

  private

  def extract_email_address(email_content)
    match = email_content.match(/^From:\s*(.*?)(?:<(.+?)>)?$/)
    match ? (match[2] || match[1]) : "unknown@example.com"
  end

  def contains_unsubscribe_keywords?(email_content)
    keywords = ["unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"]
    keywords.any? { |keyword| email_content.downcase.include?(keyword) }
  end
end