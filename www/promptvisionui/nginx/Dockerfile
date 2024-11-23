FROM nginx:stable-alpine

# Remove the default Nginx configuration
RUN rm /etc/nginx/conf.d/default.conf

# Copy custom Nginx configuration
COPY nginx.conf /etc/nginx/nginx.conf

# Create directory for static files
RUN mkdir -p /usr/share/nginx/html/_next/static

# Copy static files from the Next.js service
COPY --from=promptvisionui-nextjs /app/.next/static /usr/share/nginx/html/_next/static