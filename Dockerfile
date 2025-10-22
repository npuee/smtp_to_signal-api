FROM python:latest
# Or any preferred Python version.

EXPOSE 8025
WORKDIR /app
ADD app/main.py .
ADD app/settings.json .
ADD requirements.txt .

# Install dependencies
RUN pip install --upgrade pip
RUN pip install -r requirements.txt

CMD ["python3","-u", "main.py"] 
