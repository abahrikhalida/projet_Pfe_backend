# # Use Python 3.12
# FROM python:3.12.10

# # Prevent Python from writing .pyc files and buffer stdout/stderr
# ENV PYTHONDONTWRITEBYTECODE 1
# ENV PYTHONUNBUFFERED 1

# # Set working directory
# WORKDIR /code

# # Install dependencies
# COPY requirements.txt /code/
# RUN pip install --upgrade pip
# RUN pip install -r requirements.txt --default-timeout=8000

# # Copy the Django project
# COPY . /code/

# # Create media folder for file uploads
# RUN mkdir -p /code/media

# # Make entrypoint script executable
# RUN chmod +x /code/entrypoint.sh

# # Expose Django default port
# EXPOSE 8000

# # Run Django via entrypoint
# ENTRYPOINT ["/code/entrypoint.sh"]