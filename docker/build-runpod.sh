docker build -t entmike/disco-diffusion-1:runpod \
    --build-arg model_path=\/models \
    --build-arg base_image=entmike/disco-diffusion-1:basemodels-2.0 \
    --build-arg DD_VERSION=2.8.runpod \
    -f Dockerfile .