FROM python:3.9
WORKDIR /code
COPY . .
RUN pip install flask gunicorn requests
EXPOSE 7860
CMD ["gunicorn", "-b", "0.0.0.0:7860", "app:app"]