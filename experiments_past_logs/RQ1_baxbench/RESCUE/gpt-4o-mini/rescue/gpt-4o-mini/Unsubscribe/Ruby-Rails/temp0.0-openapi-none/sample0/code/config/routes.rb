Rails.application.routes.draw do
  post '/decideUnsubscribe', to: 'application#decide_unsubscribe'
end