docker build -t entmike/disco-diffusion-1 \
    --build-arg model_path=/workspace/disco-diffusion-1/models \
    --build-arg base_image=pytorch/pytorch \
    --build-arg DD_VERSION=2.8 \
    -f Dockerfile .