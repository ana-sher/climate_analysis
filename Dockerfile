FROM continuumio/miniconda3

COPY environment.yml /tmp/environment.yml
RUN conda env create -f /tmp/environment.yml

SHELL ["conda", "run", "-n", "climate_analysis", "/bin/bash", "-c"]

COPY . /app
WORKDIR /app

CMD ["fastapi", "run", "src/api.py", "--port", "80"]