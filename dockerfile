# Gunakan base image Python
FROM python:3.11

# Set working directory
WORKDIR /app

# Salin semua file ke container
COPY . .

# Install dependencies (kalau ada requirements.txt)
RUN pip install -r requirements.txt

# Jalankan script dengan output unbuffered
CMD ["python", "-u", "./deployment.py"]