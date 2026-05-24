class CreateInvitations < ActiveRecord::Migration[8.0]
  def change
    create_table :invitations do |t|
      t.string :email, null: false
      t.string :invite_id, null: false

      t.timestamps
    end
    add_index :invitations, :email, unique: true
  end
end