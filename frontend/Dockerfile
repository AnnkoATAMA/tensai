FROM oven/bun:latest

WORKDIR /frontend

COPY package.json bun.lockb ./

RUN bun install

COPY . .

CMD ["bun", "run", "dev", "--host", "0.0.0.0"]
