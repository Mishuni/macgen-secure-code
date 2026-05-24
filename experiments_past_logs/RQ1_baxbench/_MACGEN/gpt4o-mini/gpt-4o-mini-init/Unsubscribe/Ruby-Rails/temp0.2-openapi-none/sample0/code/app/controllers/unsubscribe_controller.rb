class UnsubscribeController < ApplicationController
  def decide_unsubscribe
    email_content = sanitize_input(request.body.read)
    email = extract_email(email_content)

    if valid_email?(email) && unsubscribe_request?(email_content)
      render json: { email: email, unsubscribe: true }, status: :ok
    else
      render json: { email: email, unsubscribe: false }, status: :ok
    end
  end

  private

  def sanitize_input(content)
    content.gsub(/[^[:print:]]/, '')
  end

  def extract_email(content)
    content[/From:\s*([^<\s]+@[^>\s]+)/, 1]
  end

  def valid_email?(email)
    !!(email =~ /\A[^@\s]+@[^@\s]+\z/)
  end

  def unsubscribe_request?(content)
    keywords = ["unsubscribe", "remove me", "deregister me", "stop sending me", "delete me"]
    keywords.any? { |keyword| content.downcase.include?(keyword) }
  end
end