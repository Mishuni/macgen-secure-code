Rails.application.routes.draw do
  post '/decideUnsubscribe', to: 'unsubscribe#decide_unsubscribe'
end