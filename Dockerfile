FROM python:3.5-alpine  AS build-env

# This dockerfile allows you to use the amzon2csv.py command very easily

# You can build the docker image with the command :
# docker build --no-cache -t amazon2csv .

# You can create a container and use the command with :
# docker run -it --rm amazon2csv --keywords="Python programming" --maxproductnb=2

RUN pip install -U --no-cache-dir --target /app amazonscraper \
&& find /app | grep -E "(__pycache__|\.pyc|\.pyo$)" | xargs rm -rf

FROM gcr.io/distroless/python3

COPY --from=build-env /app /app

ENV PYTHONPATH=/app
ENV LC_ALL=C.UTF-8
ENV LANG=C.UTF-8

ENTRYPOINT ["python", "/app/bin/amazon2csv.py"]