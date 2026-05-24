ActiveRecord::Schema[7.0].define(version: 2023_10_01_000000) do
  create_table "entries", force: :cascade do |t|
    t.string "title", null: false
    t.text "content", null: false
    t.string "last_modified_by"
    t.datetime "last_modified_at"
    t.timestamps
  end
end