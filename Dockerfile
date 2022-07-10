FROM entmike/disco-diffusion-1:runpod

ADD worker.py worker.py

CMD ["python", "worker.py"]