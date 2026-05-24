# javascript
sudo apt-get update
sudo apt-get install -y ca-certificates curl gnupg liblua5.3-dev
sudo mkdir -p /etc/apt/keyrings
curl -fsSL https://deb.nodesource.com/gpgkey/nodesource-repo.gpg.key | sudo gpg --dearmor -o /etc/apt/keyrings/nodesource.gpg
echo "deb [signed-by=/etc/apt/keyrings/nodesource.gpg] https://deb.nodesource.com/node_20.x nodistro main" | sudo tee /etc/apt/sources.list.d/nodesource.list
sudo apt-get update
# sudo apt-get install nodejs -y
# sudo apt install golang-go -y
# sudo npm install -g @babel/core @babel/cli @babel/preset-react
# sudo npm install --save-dev @babel/cli @babel/preset-react
# ruby
# sudo apt-get install ruby-full -y

# java
sudo apt-get install default-jdk -y

# go
# follow https://go.dev/doc/install
# rm -rf /usr/local/go && tar -C /usr/local -xzf go1.24.3.linux-amd64.tar.gz
# export PATH=$PATH:/usr/local/go/bin
# go version
# go get golang.org/x/crypto/blake2b@v0.29.0
# go mod tidy

# --- build essentials for CGO + sqlite3 (go-sqlite3) ---
sudo apt-get update
sudo apt-get install -y build-essential pkg-config gcc g++ make libsqlite3-dev

# --- go install (use tarball only; remove apt golang-go to avoid conflicts) ---
sudo rm -rf /usr/local/go
sudo tar -C /usr/local -xzf go1.24.3.linux-amd64.tar.gz

# persist PATH
if ! grep -q '/usr/local/go/bin' ~/.bashrc; then
  echo 'export PATH=$PATH:/usr/local/go/bin' >> ~/.bashrc
fi
source ~/.bashrc

go version

# match docker
go env -w CGO_ENABLED=1


go get ...
go mod tidy
go mod download all
# go.mod  repo
go get \
  golang.org/x/crypto@v0.29.0 \
  golang.org/x/sys@latest \
  github.com/golang-jwt/jwt/v5@latest \
  github.com/ChrisTrenkamp/goxpath@latest \
  github.com/mattn/go-sqlite3@latest

go mod tidy
go mod download all



## C
sudo apt-get install -y libjansson-dev nlohmann-json3-dev libtinyxml2-dev libjsoncpp-dev libxml2-dev libcjson-dev libcurl4-openssl-dev libjson-c-dev libbsd-dev libcrypt-dev

## CPP
# git clone https://github.com/Thalhammer/jwt-cpp.git third_party/jwt-cpp
# sudo apt-get install -y libssl-dev