FROM entmike/disco-diffusion-1:runpod

ADD worker.py worker.py
ADD worker-requirements.txt worker-requirements.txt
RUN pip install -r worker-requirements.txt

CMD ["python", "worker.py"]