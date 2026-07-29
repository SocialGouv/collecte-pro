FROM node:20-alpine as node

WORKDIR /app

COPY . .

RUN npm run build-all

FROM python:3.14
WORKDIR /app
COPY --from=node /app /app

RUN rm .env
RUN pip install -r requirements.txt

CMD ["/bin/bash", "-c", "/app/start_container.sh"]
