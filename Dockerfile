FROM python:3.11.9

WORKDIR /app
COPY ./requirements.txt /app
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . /app
ENV PYTHONPATH="/app/src"
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]