# syntax=docker/dockerfile:1.7
##############################################################################
# DocuSense-AI · React front-end (Create-React-App, Node 18-alpine)          #
##############################################################################

########################  🔧  BUILD STAGE  ###################################
FROM node:18-alpine AS build
WORKDIR /app

# 1️⃣  Speed-up npm network & cache
RUN --mount=type=cache,target=/root/.npm \
    npm config set fetch-retries 5           && \
    npm config set fetch-retry-mintimeout 20000  && \
    npm config set fetch-retry-maxtimeout 90000

# 2️⃣  Install deps reproducibly
COPY package*.json ./

# 3️⃣  Copy source & build CRA (→ /app/build)
COPY . .
RUN npm run build

########################  🚀  RUNTIME STAGE  #################################
FROM node:18-alpine AS production
WORKDIR /app
RUN npm install -g serve                    # tiny static-file server

# copy the compiled bundle
COPY --from=build /app/build ./build

EXPOSE 3000
CMD ["serve", "-s", "build", "-l", "3000"]
