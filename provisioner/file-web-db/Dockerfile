FROM python:3.6
RUN python3 -m pip install --upgrade pip
COPY . /var/www/
RUN python -m pip install -r /var/www/requirements.txt
COPY routes/ /var/www/
ENV container=docker \
        DOCKER_NAME="file_web_db"

# Set Prompt
COPY docker_prompt.sh /etc/profile.d

EXPOSE 5000
CMD ["python3", "/var/www/app.py"]
