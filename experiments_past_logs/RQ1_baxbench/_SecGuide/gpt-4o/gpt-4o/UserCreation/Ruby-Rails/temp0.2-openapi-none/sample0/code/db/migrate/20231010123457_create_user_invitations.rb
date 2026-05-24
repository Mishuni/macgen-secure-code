class CreateUserInvitations < ActiveRecord::Migration[8.0]
  def change
    create_table :user_invitations do |t|
      t.string :email, null: false
      t.string :invite_id, null: false

      t.timestamps
    end
    add_index :user_invitations, :email, unique: true
  end
end