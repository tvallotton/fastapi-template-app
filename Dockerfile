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
###      SHARED IMAGE     ###
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
RUN pip3 install -r requirements.txt

# Copy generated files
COPY --from=build /home/app/static /home/app/static

RUN useradd app

CMD [ "python3", "-m", "src", "prod" ]
