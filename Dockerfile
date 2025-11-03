FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    libgeos-dev \
    binutils \
    libproj-dev \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY . /app

RUN pip install --no-cache-dir -r requirements.txt

# Correct Linux paths for ARM containers
ENV GEOS_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu/libgeos_c.so
ENV GDAL_LIBRARY_PATH=/usr/lib/aarch64-linux-gnu/libgdal.so
ENV PROJ_LIB=/usr/share/proj

EXPOSE 8000
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
