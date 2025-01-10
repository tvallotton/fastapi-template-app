#############################
###      BUILD IMAGE      ###
#############################
FROM rust:1.81.0 as build
WORKDIR /home/app
RUN cargo install sqlx-cli@0.8.2 --no-default-features --features native-tls,postgres
RUN apt-get update
RUN apt-get install nodejs npm -y
COPY . .
# Generate output files
RUN npx --yes tailwindcss -i ./static/styles/input.css -o ./static/styles/output.css

#############################
###      POETRY IMAGE     ###
#############################
FROM python:3.12.8 as requirements
WORKDIR /home/app
RUN pip3 install pipx
RUN pipx install poetry
RUN /root/.local/bin/poetry self add poetry-plugin-export
COPY ./pyproject.toml ./pyproject.toml
COPY ./poetry.lock ./poetry.lock
# Create the requirements.txt file
RUN /root/.local/bin/poetry export --without-hashes > requirements.txt 

#############################
###      Prod IMAGE     ###
#############################
FROM python:3.12.8 as prod
WORKDIR /home/app

RUN apt-get update
RUN apt-get install locales cron nginx -y
RUN sed -i 's/^# *\(es_CL.UTF-8\)/\1/' /etc/locale.gen
RUN locale-gen
ENV LANG es_CL.UTF-8
ENV LANGUAGE es_CL:es
ENV LC_ALL es_CL.UTF-8
COPY . .

# Copy sqlx binary
COPY --from=build /usr/local/cargo/bin/sqlx /usr/local/bin/sqlx

# Copy tailwindcss build
COPY --from=build /home/app/static /home/app/static

# Copy requirements.txt
COPY --from=requirements /home/app/requirements.txt /home/app/requirements.txt

RUN pip install -r requirements.txt

RUN useradd app

CMD [ "python", "-m", "src", "prod" ]
