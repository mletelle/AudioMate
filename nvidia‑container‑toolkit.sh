# 0) driver propietario ya instalado (>= 535)
sudo apt-get update && sudo apt-get install -y curl gnupg lsb-release

# 1) repos oficiales de NVIDIA
curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | \
     sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit.gpg

distribution=$(. /etc/os-release; echo $ID$VERSION_ID)
curl -s -L https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
     sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit.gpg] https://#' | \
     sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

# 2) instalación del toolkit
sudo apt-get update
sudo apt-get install -y nvidia-container-toolkit
# 3) reiniciar Docker
sudo systemctl restart docker

# 4) prueba rápida
docker run --rm --gpus all nvidia/cuda:12.3.1-base nvidia-smi
