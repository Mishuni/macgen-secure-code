Rails.application.routes.draw do
  post '/decideUnsubscribe', to: 'unsubscribe#decide'
end