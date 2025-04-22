git clone https://github.com/mletelle/audiomate.git
cd audiomate

# 1. (una sola vez) instalar nvidia-container-toolkit → ver sección 4
# 2. compilar imagen
make build        # ≡ docker compose build
# 3. levantar servicio
make up           # abrir http://localhost:8501
