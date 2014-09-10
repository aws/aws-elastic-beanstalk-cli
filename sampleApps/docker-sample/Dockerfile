FROM aws_beanstalk/ubuntu:12.04

# Add sample application
ADD application.py /tmp/application.py

EXPOSE 8000

# Run it
ENTRYPOINT ["python", "/tmp/application.py"]
