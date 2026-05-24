FROM co1lin/cweval
RUN source ~/miniforge3/bin/activate; conda activate cweval; \
    pip install dnspython Cerberus Werkzeug fire asteval email-validator sympy \
    py-bcrypt lxml cryptography Flask-Limiter Flask-Cors passlib argon2-cffi pycryptodome publicsuffix2 simpleeval PyJWT bleach
    
RUN sudo apt-get update && sudo apt-get install -y libjansson-dev nlohmann-json3-dev libtinyxml2-dev libjsoncpp-dev libxml2-dev libcjson-dev libcurl4-openssl-dev libjson-c-dev libbsd-dev libcrypt-dev libhtml-parser-perl build-essential cmake
RUN sudo apt-get install -y libssl-dev
RUN git clone https://github.com/trusch/libbcrypt.git /tmp/libbcrypt && \
    cd /tmp/libbcrypt && cmake . && make && sudo make install && \
    sudo ldconfig
RUN sudo ln -s /usr/lib/x86_64-linux-gnu/libcurl.so /usr/lib/libcurl.so
COPY cleanup_bcrypt.py /tmp/cleanup_bcrypt.py
RUN source ~/miniforge3/bin/activate; conda activate cweval; conda run -n cweval python /tmp/cleanup_bcrypt.py \
 && conda run -n cweval pip uninstall -y bcrypt py-bcrypt || true \
 && conda run -n cweval pip install --no-cache-dir \
      dnspython Cerberus Werkzeug fire email-validator lxml \
#  && conda run -n cweval pip install --no-cache-dir "bcrypt==4.1.2" "cffi>=1.15"
 && conda run -n cweval pip install --no-cache-dir "bcrypt==4.0.1" "cffi>=1.15" \
 && conda run -n cweval pip install --no-cache-dir "multiprocess==0.70.16" \
 && conda run -n cweval pip install --no-cache-dir "wrapt_timeout_decorator==1.3.3" \
 && conda run -n cweval pip install --no-cache-dir tldextract html-sanitizer validators

SHELL ["/bin/bash", "-lc"]
WORKDIR /home/ubuntu/CWEval  
RUN source .env || true; \
    go env -w CGO_ENABLED=1; \
    go get \
      golang.org/x/crypto@v0.29.0 \
      golang.org/x/sys@latest \
      github.com/golang-jwt/jwt/v5@latest \
      github.com/ChrisTrenkamp/goxpath@latest \
      github.com/mattn/go-sqlite3@latest && \
    go mod tidy && \
    go mod download all

RUN mkdir -p third_party && \
    git clone --branch v0.3.1 https://github.com/Thalhammer/jwt-cpp.git third_party/jwt-cpp

RUN sudo apt-get update && sudo apt-get install -y --no-install-recommends nodejs npm && \
    sudo rm -rf /var/lib/apt/lists/* && \
    (command -v node >/dev/null 2>&1 || sudo ln -s /usr/bin/nodejs /usr/bin/node) || true

WORKDIR /home/ubuntu/CWEval
ENV npm_config_loglevel=warn \
    npm_config_fund=false \
    npm_config_audit=false \
    PYTHON=/usr/bin/python3

RUN if [ -f package-lock.json ]; then \
        npm ci --omit=dev && \
        npm i --no-audit --no-fund --progress=false he mathjs js-yaml@3.14.1; \
    else \
        if [ ! -f package.json ]; then npm init -y >/dev/null 2>&1; fi; \
        npm i --no-audit --no-fund --progress=false \
          validator sqlite3 bcrypt jsdom xpath jsonwebtoken he mathjs js-yaml@3.14.1; \
    fi

COPY benchmark /home/ubuntu/CWEval/benchmark
COPY cweval/commons.py /home/ubuntu/CWEval/cweval/commons.py
COPY cweval/run_tests.py /home/ubuntu/CWEval/cweval/run_tests.py
COPY cweval/evaluate.py /home/ubuntu/CWEval/cweval/evaluate.py
COPY run_evals.sh /home/ubuntu/CWEval/run_evals.sh
RUN sudo chmod +x /home/ubuntu/CWEval/run_evals.sh

# RUN if [ -f package-lock.json ]; then \
#         npm ci --omit=dev && \
#         npm i --no-audit --no-fund --progress=false he mathjs; \
#     else \
#         if [ ! -f package.json ]; then npm init -y >/dev/null 2>&1; fi; \
#         npm i --no-audit --no-fund --progress=false \
#           validator sqlite3 bcrypt jsdom xpath jsonwebtoken he mathjs; \
#     fi


CMD ["zsh"]
