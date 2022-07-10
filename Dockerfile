FROM entmike/disco-diffusion-1:runpod

ADD worker.py worker.py

RUN pip install -r worker-requirements.txt

CMD ["python", "worker.py"]