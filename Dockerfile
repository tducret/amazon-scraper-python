FROM python:3

# This dockerfile allows you to use the amzon2csv.py command very easily

# You can build the docker image with the command :
# docker build --no-cache -t amazon2csv .

# You can create a container with :
# docker run -it --rm --name amazon2csv amazon2csv

RUN pip3 install -U --no-cache-dir amazonscraper

ENTRYPOINT [ "amazon2csv.py" ]