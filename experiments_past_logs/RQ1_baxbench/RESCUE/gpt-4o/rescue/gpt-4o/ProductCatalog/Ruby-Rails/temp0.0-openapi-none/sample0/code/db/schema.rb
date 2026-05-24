ActiveRecord::Schema.define(version: 2023_10_10_123456) do
  create_table "products", force: :cascade do |t|
    t.string "name", null: false
    t.json "additional_properties", default: {}, null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end
end