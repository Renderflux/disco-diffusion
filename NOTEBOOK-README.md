## 🙏 Credits/Contributions
- Inspired from [alembics Notebook](https://colab.research.google.com/github/alembics/disco-diffusion/blob/main/Disco_Diffusion.ipynb) and others.

- Contributions welcomed at [https://github.com/entmike/disco-diffusion-1](https://github.com/entmike/disco-diffusion-1)

- Questions?  Feedback?  Please hunt me down on Discord (`entmike#1926`), or open an Issue in GitHub!

## Links
- [Zippy's DD Cheatsheet](https://docs.google.com/document/d/1l8s7uS2dGqjztYSjPpzlmXLjl5PM3IGkRWI3IiCuK7g)

- [EZ Charts](https://docs.google.com/document/d/1ORymHm0Te18qKiHnhcdgGp-WSt8ZkLZvow3raiu2DVU)


## Changes/Enhancements
- **July 12, 2022**
 13 new CLIP models and many more diffusion models have been updated in the entmike/disco-diffusion-1 GitHub fork and entmike/disco-diffusion-1 docker image.  If you use RunPod, entmike/disco-diffusion-1:runpod has the models pre-baked into them as well.

  CLIP
  -  ViTB32_laion2b_e16
  -  ViTB32_laion400m_e31
  -  ViTB32_laion400m_e32
  -  ViTB32quickgelu_laion400m_e31
  -  ViTB32quickgelu_laion400m_e32
  -  ViTB16_laion400m_e31
  -  ViTB16_laion400m_e32
  -  RN50_yffcc15m
  -  RN50_cc12m
  -  RN50_quickgelu_yfcc15m
  -  RN50_quickgelu_cc12m
  -  RN101_yfcc15m
  -  RN101_quickgelu_yfcc15m

  Diffusion
  Pixel Art  (Credit https://github.com/KaliYuga-ai/Pixel-Art-Diffusion/blob/e037fd58e2aef58f28d7511ea6dcb184e898e39f/Pixel_Art_Diffusion_v1_0.ipynb)
  - pixel_art_diffusion_hard_256
  - pixel_art_diffusion_soft_256
  - pixelartdiffusion_expanded
  - pixelartdiffusion4k
  - PADexpanded
  - watercolordiffusion
  - watercolordiffusion_2
  - PulpSciFiDiffusion
  - lsun_uncond_100M_1200K_bs128
  Comic Faces  (Credit: https://huggingface.co/spaces/Gradio-Blocks/clip-guided-faces/blob/main/app.py)
  - 256x256_openai_comics_faces_by_alex_spirin_084000
  Ukiyoe  (Credit: https://huggingface.co/thegenerativegeneration/ukiyoe-diffusion-256/tree/main)
  - ukiyoe_diffusion_256_022000.pt
  Liminal Spaces (Back Rooms, according to my kids) (Credit: https://colab.research.google.com/drive/11Bs4wCs9R84DVAwDb3MkvDAd8V_Mw1e6?usp=sharing)
  - liminal_diffusion 
- **July 9, 2022**
  - Catch up some DD 5.3 features from alembics
  - Horizontal and Vertical symmetry functionality by nshepperd. Symmetry transformation_steps by huemin (https://twitter.com/huemin_art). Symmetry integration into Disco Diffusion by Dmitrii Tochilkin (https://twitter.com/cut_pow)
- **May 28, 2022**
  - Turbo Mode after frame 10 fixed.  (https://github.com/entmike/disco-diffusion-1/issues/8)
- **May 20, 2022**
  - Voronoi Diagram introduced as an alternative to perlin noise and init_image as a starting point.  To use, set `init_generator` to `voronoi` (Default is `perlin` to honor default noise behavior)  `voronoi_points` controls how many regions the voronoi procedure creates.  You can also optionally control the palette by specifying a different file in `voronoi_palette`.  Refer to the 2 example yaml files in the new `palettes` folder.  There are currently two modes (`generated` and `static`.)  For static, you specify all your values in the yaml file as in the example in `static.yaml`.  For randomly generated color ranges, refer to `default.yaml` to see how you can control what random color hue ranges will be picked.
  - Other minor bug fixes and code cleanup.
- **May 16, 2022**
  - `prompt_salad` feature implemented.  Make Mad Libs out of a `prompt_salad_template`!
- **May 14, 2022**
  - Make this README shared across notebooks (`NOTEBOOK-README.md`)
- **May 13, 2022**
  - Implement (very) experimental vertical symmetry.  (Credit: **`aztec_man#3032`** on Discord)
  - Add GPU detection warning for T4 and V100 GPUs.  (I cannot implement the `!pip install torch==1.10.2 torchvision==0.11.3 -q` patch because it breaks `pytorch3d`, sorry guys, I'll keep trying to find another solution.
- **May 11, 2022**
  - Discord link fixed
- **May 10, 2022**
  - Fix, then break, then fix again, pytorch3d and 3d animations
- **May 6, 2022**
  - Twilio SMS alerts (optional, disabled by default)
- **May 5, 2022**
  - sqlite3 DB support to store your params and images for future query/display/searching.
- **May 4, 2022**
  - Add fallback URLs to model downloads
  - Add `init_images` and `images_out` parameters to control directory locations
  - Add `save_metadata` (Default = `False`) parameter to optionally embed DD params into your .PNGs
  - Add `multiplier` support.
- **May 3, 2022**
  - Add Symmetry Parameters
  - Modifier Support for Art Studies!
- **May 2, 2022**
  - Add initial support for YAML load/export
  - Add initial logging support

- **April 2022**
  - All functions moved to `dd.py` that are not needed in the Notebook to reduce clutter and hopefully improve readibility.

  - All other Git repos that used to get cloned and dumped in your Google Drive are now referenced as pip packages.

## Command-Line Support

  After running the **Set Up Environment** cell, from your Google Colab Terminal you can run your Disco Diffusion workload from a terminal or make a `bash` script to do multiple different batches.  Example:

  ```bash
  cd /content/gdrive/MyDrive/disco-diffusion-1
  python disco.py --steps=50 --batch_name="CommandLineBatch" --RN50=False \
  --text_prompts='{"0":["A beautiful painting of a dolphin","ocean theme"]}'
  ```
## YAML Support from Terminal

  Use a YAML file to save/change your settings.  (See `examples/configs/lighthouse.yml` for an example structure.)
   ```bash
   cd /content/gdrive/MyDrive/disco-diffusion-1
   python disco.py --config_file=examples/configs/lighthouse.yml
   ```