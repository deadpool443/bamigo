FROM python:3.11.9
WORKDIR  /main
RUN pip install virtualenv
RUN virtualenv venv
COPY . /main
RUN pip install winregistry
RUN /app/venv/bin/pip install --no-cache-dir -r requirements.txt
EXPOSE 5000
ENTRYPOINT ["/bin/bash", "-c", "source venv/bin/activate && exec python main.py"]
