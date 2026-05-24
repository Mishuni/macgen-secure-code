ActiveRecord::Schema.define(version: 2023_10_10_123456) do
  create_table "profiles", force: :cascade do |t|
    t.string "username", null: false
    t.text "profile_page", null: false
    t.datetime "created_at", precision: nil, null: false
    t.datetime "updated_at", precision: nil, null: false
  end
end