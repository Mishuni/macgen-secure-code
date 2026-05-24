Rails.application.routes.draw do
  resources :profiles, only: [:create, :show], param: :username do
    get 'profile_photo', on: :member
  end
end