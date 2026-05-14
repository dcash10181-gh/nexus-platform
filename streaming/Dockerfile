FROM node:20-alpine
WORKDIR /app
COPY server.js .
EXPOSE 8001
HEALTHCHECK --interval=15s --timeout=5s CMD wget -qO- http://localhost:8001/health || exit 1
CMD ["node", "server.js"]
