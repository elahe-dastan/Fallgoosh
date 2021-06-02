# 1. Stage for building the app for developement usage (Docker compose or simple docker build command)
FROM golang:1.16-alpine AS build

ARG GOPROXY

ENV GO111MODULE=on \
    GOOS=linux \
    GOARCH=amd64 \
    GOPROXY=$GOPROXY

RUN mkdir -p /src

WORKDIR /src

COPY go.mod go.sum /src/
RUN go env -w GOPROXY=https://repo.snapp.tech/repository/goproxy/ && \
    go env -w GONOSUMDB="gitlab.snapp.ir" && \
    go mod download

COPY . /src
RUN CGO_ENABLED=0 go build -a -installsuffix cgo

# 2. Stage for running the app build in stage 1 for using in developement (docker compose or simple docker build)
FROM alpine:3.11

ENV TZ=Asia/Tehran \
    PATH="/app:${PATH}"

RUN apk add --update tzdata ca-certificates bash && \
    cp --remove-destination /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo "${TZ}" > /etc/timezone && \
    mkdir -p /app && \
    chgrp -R 0 /app && \
    chmod -R g=u /app

WORKDIR /app

COPY --from=build /src/streamer /app

CMD ["./streamer"]

# 3. Stage used for production use. The build steps is done in the projects CI/CD with the steps outside of this
# dockerfile
FROM alpine:3.11 AS prod-build

ENV TZ=Asia/Tehran \
    PATH="/app:${PATH}"

RUN echo "https://repo.snapp.tech/repository/alpine/v3.11/main" > /etc/apk/repositories && \
    echo "https://repo.snapp.tech/repository/alpine/v3.11/community" >> /etc/apk/repositories && \
    apk add --update tzdata ca-certificates bash && \
    cp --remove-destination /usr/share/zoneinfo/${TZ} /etc/localtime && \
    echo "${TZ}" > /etc/timezone && \
    mkdir -p /app && \
    chgrp -R 0 /app && \
    chmod -R g=u /app

WORKDIR /app

COPY --from=build /src/streamer /app

CMD ["./streamer"]
