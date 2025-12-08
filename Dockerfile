FROM python:3.11.9

RUN apt-get update && apt-get install -y \
    gdal-bin \
    libgdal-dev \
    && apt-get clean

ENV CPLUS_INCLUDE_PATH=/usr/include/gdal
ENV C_INCLUDE_PATH=/usr/include/gdal

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir numpy>=1.26
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /app
ENV PYTHONPATH="/app/src"
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]