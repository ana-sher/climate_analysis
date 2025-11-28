FROM public.ecr.aws/lambda/python:3.11

COPY requirements-lambda.txt .
RUN pip install --prefer-binary -r requirements-lambda.txt

COPY src /var/task/src
ENV PYTHONPATH="/var/task/src"
CMD ["api.handler"]