FROM python:3.9.5-slim

WORKDIR /app/

COPY requirements.txt ./

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

ENV PYTHONPATH "${PYTHONPATH}:/app"

EXPOSE 80

ENTRYPOINT [ "uvicorn" ]
CMD [ "main:app", "--host", "0.0.0.0", "--port", "80", "--reload" ]

