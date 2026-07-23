FROM nginx:1.27-alpine

# remove default nginx site
RUN rm -rf /usr/share/nginx/html/*

# copy site files
COPY index.html services.html about.html projects.html contact.html styles.css script.js /usr/share/nginx/html/

# make sure the nginx worker process (runs as non-root) can read everything
RUN chmod -R 755 /usr/share/nginx/html

# custom nginx config (clean URLs, gzip, caching)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s CMD wget -q --spider http://localhost/ || exit 1
