import wget, os
from loguru import logger
from pydotted import pydot
import hashlib
import ipywidgets as widgets
from IPython import display


def loadModels2(folders=pydot({"model_path": "models"})):
    """Downloads models required to use Disco Diffusion

    Args:
        folders (JSON): Folder parameters (e.g. `{"model_path":"path/to/download/models"}`)
    """
    # Download models if not present

    models_config = [
        {
            "file": f"{folders.model_path}/ukiyoe_diffusion_256_022000.pt",
            "hash": "b0b9626fbc6c43ea7eb074134612381a794c5407abb4debc8ba6ccb37386e769",
            "sources": [{"url": "https://huggingface.co/thegenerativegeneration/ukiyoe-diffusion-256/resolve/main/ukiyoe_diffusion_256_022000.pt"}],
        },
        {
            "file": f"{folders.model_path}/PADexpanded.pt",
            "hash": "a73b40556634034bf43b5a716b531b46fb1ab890634d854f5bcbbef56838739a",
            "sources": [{"url": "https://huggingface.co/KaliYuga/PADexpanded/resolve/main/PADexpanded.pt"}],
        },
        {
            "file": f"{folders.model_path}/pixelartdiffusion4k.pt",
            "hash": "a1ba4f13f6dabb72b1064f15d8ae504d98d6192ad343572cc416deda7cccac30",
            "sources": [{"url": "https://huggingface.co/KaliYuga/pixelartdiffusion4k/resolve/main/pixelartdiffusion4k.pt"}],
        },
        {
            "file": f"{folders.model_path}/watercolordiffusion.pt",
            "hash": "a3e6522f0c8f278f90788298d66383b11ac763dd5e0d62f8252c962c23950bd6",
            "sources": [{"url": "https://huggingface.co/KaliYuga/watercolordiffusion/resolve/main/watercolordiffusion.pt"}],
        },
        {
            "file": f"{folders.model_path}/watercolordiffusion_2.pt",
            "hash": "49c281b6092c61c49b0f1f8da93af9b94be7e0c20c71e662e2aa26fee0e4b1a9",
            "sources": [{"url": "https://huggingface.co/KaliYuga/watercolordiffusion_2/resolve/main/watercolordiffusion_2.pt"}],
        },
        {
            "file": f"{folders.model_path}/PulpSciFiDiffusion.pt",
            "hash": "b79e62613b9f50b8a3173e5f61f0320c7dbb16efad42a92ec94d014f6e17337f",
            "sources": [{"url": "https://huggingface.co/KaliYuga/PulpSciFiDiffusion/resolve/main/PulpSciFiDiffusion.pt"}],
        },
        {
            "file": f"{folders.model_path}/liminal_diffusion.pt",
            "hash": "2eb25fb3a13a92df27cb69046a518901dcd5b1eff3ffe5d2575a35ee75b4da9f",
            "sources": [{"url": "https://huggingface.co/BrainArtLabs/liminal_diffusion/resolve/main/liminal_diffusion.pt"}],
        },
        {
            "file": f"{folders.model_path}/rn50-quickgelu-yfcc15m-455df137.pt",
            "hash": "455df13750cec2d6bb5e578fa84fb59a63d40e9fdbae58e7e7155672e46dc578",
            "sources": [{"url": "https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/rn50-quickgelu-yfcc15m-455df137.pt"}],
        },
        {
            "file": f"{folders.model_path}/rn50-quickgelu-cc12m-f000538c.pt",
            "hash": "f000538c6c3c33c07e4fad5619f1b3d4cd591864dd3143778896112d1bf4fa7d",
            "sources": [{"url": "https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/rn50-quickgelu-cc12m-f000538c.pt"}],
        },
        {
            "file": f"{folders.model_path}/rn101-quickgelu-yfcc15m-3e04b30e.pt",
            "hash": "3e04b30eb7070e69b78db2c33f12a48cfa1f697691ed198d61fb2abbb48db5a3",
            "sources": [{"url": "https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/rn101-quickgelu-yfcc15m-3e04b30e.pt"}],
        },
        {
            "file": f"{folders.model_path}/vit_b_32-laion2b_e16-af8dbd0c.pth",
            "hash": "af8dbd0c4bf1654db018a2a70fd839c3a6e79d2fdac33303f06d0d8aae16a65c",
            "sources": [{"url": "https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/vit_b_32-laion2b_e16-af8dbd0c.pth"}],
        },
        {
            "file": f"{folders.model_path}/vit_b_32-quickgelu-laion400m_e31-d867053b.pt",
            "hash": "d867053b2301634007ed9af230bfb1a217ec634f6c0329f04092133ae5c4b89e",
            "sources": [{"url": "https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/vit_b_32-quickgelu-laion400m_e31-d867053b.pt"}],
        },
        {
            "file": f"{folders.model_path}/vit_b_32-quickgelu-laion400m_e32-46683a32.pt",
            "hash": "46683a32721d5c68911153698992361285d20ca690bb4f317c11e45c03d798fa",
            "sources": [{"url": "https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/vit_b_32-quickgelu-laion400m_e32-46683a32.pt"}],
        },
        {
            "file": f"{folders.model_path}/vit_b_16-laion400m_e31-00efa78f.pt",
            "hash": "00efa78fe761eb607926704cfee46a4305ce2bf63af6ab50f1eeba2ef71da988",
            "sources": [{"url": "https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/vit_b_16-laion400m_e31-00efa78f.pt"}],
        },
        {
            "file": f"{folders.model_path}/vit_b_16-laion400m_e32-55e67d44.pt",
            "hash": "55e67d44b44d9e39aaf299a5c616aaf10a655879d6bd5854027b4a254aa2e7d5",
            "sources": [{"url": "wget https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/vit_b_16-laion400m_e32-55e67d44.pt"}],
        },
        {
            "file": f"{folders.model_path}/vit_b_16_plus_240-laion400m_e31-8fb26589.pt",
            "hash": "8fb26589b9a8bab2e7a683d280e48df89b8e742f3a82132707282620b36facba",
            "sources": [{"url": "https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/vit_b_16_plus_240-laion400m_e31-8fb26589.pt"}],
        },
        {
            "file": f"{folders.model_path}/vit_b_16_plus_240-laion400m_e32-699c4b84.pt",
            "hash": "699c4b843885d82733517f36f0911d7e1b360bcc1314dda81d8c56c76fe9524d",
            "sources": [{"url": "https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/vit_b_16_plus_240-laion400m_e32-699c4b84.pt"}],
        },
        {
            "file": f"{folders.model_path}/vit_l_14-laion400m_e31-69988bb6.pt",
            "hash": "69988bb6afa2b63291087c61464b3138660b2861fea5ec4682e107d194d9aaa3",
            "sources": [{"url": "https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/vit_l_14-laion400m_e31-69988bb6.pt"}],
        },
        {
            "file": f"{folders.model_path}/vit_l_14-laion400m_e32-3d133497.pt",
            "hash": "3d133497672c345f50dec98ebc674bb74c14b4f3aa0f3088f7cefe7e05a10a60",
            "sources": [{"url": "https://github.com/mlfoundations/open_clip/releases/download/v0.2-weights/vit_l_14-laion400m_e32-3d133497.pt"}],
        },
    ]

    modelProgress = widgets.IntProgress(
        value=0, min=0, max=len(models_config), bar_style="info", orientation="horizontal", description="Downloading"  # 'success', 'info', 'warning', 'danger' or ''
    )

    print("Making sure required models are downloaded")
    try:
        display(modelProgress)
    except:
        logger.info("Downloading...")

    ## TODO: Make this show incremental progress
    ## TODO: Make this download in parallel

    for m in models_config:
        if not os.path.exists(f'{m["file"]}'):
            downloaded = False
            for source in m["sources"]:
                if not downloaded:
                    url = source["url"]
                    try:
                        logger.info(f'🌍 (First time setup): Downloading model from {url} to {m["file"]}')
                        wget.download(url, m["file"])
                        print("")
                        with open(m["file"], "rb") as f:
                            bytes = f.read()  # read entire file as bytes
                            readable_hash = hashlib.sha256(bytes).hexdigest()
                            if readable_hash == m["hash"]:
                                logger.success(f"✅ SHA-256 hash matches: {readable_hash}")
                                modelProgress.value = modelProgress.value + 1
                                downloaded = True
                            else:
                                logger.error(f"🛑 Wrong hash! '{readable_hash}' instead of '{m['hash']}'")
                                os.remove(m["file"])
                                raise Exception("Bad hash")
                    except:
                        logger.error(f"Download failed.  Fallback URLs will be attempted until exhausted.")
            if downloaded == False:
                logger.error(f"🛑 Could NOT download {m['file']} from any sources! 🛑")
        else:
            modelProgress.value = modelProgress.value + 1
            logger.success(f'✅ Model already downloaded: {m["file"]}')


def main():
    loadModels2(pydot({"model_path": "models"}))


if __name__ == "__main__":
    main()
