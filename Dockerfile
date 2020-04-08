FROM python:3-alpine
RUN apk add --no-cache git

COPY mergetest.py /
RUN pip install --no-cache-dir sh

CMD ["python", "/mergetest.py"]
