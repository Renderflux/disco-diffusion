import argparse
import traceback
from typing import Union
from dd import str2bool, str2json, get_param as gp
from yaml import dump, full_load
from loguru import logger
from pydotted import pydot
import argparse
import dd
from deepdiff import DeepHash


def parse(a=None):
    parser = argparse.ArgumentParser(description="Disco Diffusion")
    # Dummy args
    parser.add_argument("-f", "--f", help="a dummy argument to fool ipython", default="1")
    parser.add_argument("-i", "--ip", help="a dummy argument to fool ipython", default="1")
    parser.add_argument("-s", "--stdin", help="a dummy argument to fool ipython", default="1")
    parser.add_argument("-c", "--control", help="a dummy argument to fool ipython", default="1")
    parser.add_argument("-b", "--hb", help="a dummy argument to fool ipython", default="1")
    parser.add_argument("-K", "--Session.key", help="a dummy argument to fool ipython", default="1")
    parser.add_argument("-S", "--Session.signature_scheme", help="a dummy argument to fool ipython", default="1")
    parser.add_argument("-l", "--shell", help="a dummy argument to fool ipython", default="1")
    parser.add_argument("-t", "--transport", help="a dummy argument to fool ipython", default="1")
    parser.add_argument("-o", "--iopub", help="a dummy argument to fool ipython", default="1")
    # Real Args
    parser.add_argument("--db", help="SQLite DB path", required=False, default=gp("db", None))
    parser.add_argument("--steps", type=int, help="Number of steps", required=False, default=gp("steps", 250))
    parser.add_argument("--batch_name", help="Batch Name", required=False, default=gp("batch_name", "TimeToDisco"))
    parser.add_argument("--images_out", help="Images out directory", required=False, default=gp("images_out", "images_out"))
    parser.add_argument("--model_path", help="Models directory", required=False, default=gp("model_path", "models"))
    parser.add_argument("--init_images", help="Init Images directory", required=False, default=gp("init_images", "init_images"))
    parser.add_argument("--save_metadata", help="Save DD params to image", type=str2bool, default=gp("save_metadata", False))
    parser.add_argument("--useCPU", help="Use CPU", type=str2bool, default=gp("useCPU", False))
    parser.add_argument(
        "--text_prompts",
        help="Text Prompts",
        type=str2json,
        default=gp(
            "text_prompts",
            {
                0: [
                    "A beautiful painting of a singular lighthouse, shining its light across a tumultuous sea of blood by greg rutkowski and thomas kinkade, Trending on artstation.",
                    "yellow color scheme",
                ],
                100: ["This set of prompts start at frame 100", "This prompt has weight five:5"],
            },
        ),
        required=False,
    )
    parser.add_argument(
        "--modifiers",
        help="Modifiers",
        type=str2json,
        default=gp("modifiers", {}),
        required=False,
    )
    parser.add_argument(
        "--prompt_salad",
        help="Prompt Salad Mode",
        type=str2bool,
        default=gp("prompt_salad", False),
        required=False,
    )
    parser.add_argument(
        "--prompt_salad_path",
        help="Prompt Salad Path",
        default=gp("prompt_salad_path", "prompt_salad"),
        required=False,
    )
    parser.add_argument(
        "--prompt_salad_template",
        help="Prompt Salad Template",
        default=gp("prompt_salad_path", "{colors} {things} in the {custom/customword} shape of {shapes}, art by {artists}"),
        required=False,
    )
    parser.add_argument(
        "--prompt_salad_amount",
        help="Prompt Salad Amount",
        type=int,
        default=gp("prompt_salad_amount", 5),
        required=False,
    )
    parser.add_argument(
        "--multipliers",
        help="Multipliers",
        type=str2json,
        default=gp("multipliers", {}),
        required=False,
    )
    parser.add_argument("--image_prompts", help="Text Prompts", type=str2json, default=gp("image_prompts", {}), required=False)
    parser.add_argument("--cutout_debug", nargs="?", type=str2bool, const=True, default=gp("cutout_design", False), help="Cutout Debugger", required=False)
    parser.add_argument("--console_preview", nargs="?", type=str2bool, const=True, default=gp("console_preview", False), help="Console Preview", required=False)
    parser.add_argument("--console_preview_width", type=int, help="Console Preview Column Width", required=False, default=gp("console_preview_width", 80))
    parser.add_argument("--cuda_device", help="CUDA Device", required=False, default=gp("cuda_device", "cuda:0"))
    parser.add_argument("--simple_nvidia_smi_display", type=bool, help="Condensed nvidia-smi display", required=False, default=gp("simple_nvidia_smi_display", True))
    parser.add_argument("--use_checkpoint", nargs="?", type=str2bool, const=True, default=gp("use_checkpoint", True), help="Use Checkpoint", required=False)
    parser.add_argument("--ViTB32", help="Use VitB32 model", type=str2bool, default=gp("ViTB32", True))
    parser.add_argument("--ViTB16", help="Use VitB16 model", type=str2bool, default=gp("ViTB16", True))
    parser.add_argument("--ViTL14", help="Use VitL14 model", type=str2bool, default=gp("ViTL14", False))
    parser.add_argument("--ViTL14_336", help="Use VitL14x336 model", type=str2bool, default=gp("ViTL14_336", False))
    parser.add_argument("--RN50", help="Use RN50 model", type=str2bool, default=gp("RN50", True))
    parser.add_argument("--RN50x4", help="Use RN50x4 model", type=str2bool, default=gp("RN50x4", False))
    parser.add_argument("--RN50x16", help="Use RN50x16 model", type=str2bool, default=gp("RN50x16", False))
    parser.add_argument("--RN50x64", help="Use RN50x64 model", type=str2bool, default=gp("RN50x64", False))
    parser.add_argument("--RN101", help="Use RN101 model", type=str2bool, default=gp("RN101", False))
    parser.add_argument("--ViTB32_laion2b_e16", help="Use ViTB32_laion2b_e16 model", type=str2bool, default=gp("ViTB32_laion2b_e16", False))
    parser.add_argument("--ViTB32_laion400m_e31", help="Use ViTB32_laion400m_e31 model", type=str2bool, default=gp("ViTB32_laion400m_e31", False))
    parser.add_argument("--ViTB32_laion400m_e32", help="Use ViTB32_laion400m_e32 model", type=str2bool, default=gp("ViTB32_laion400m_e32", False))
    parser.add_argument("--ViTB32quickgelu_laion400m_e31", help="Use ViTB32quickgelu_laion400m_e31 model", type=str2bool, default=gp("ViTB32quickgelu_laion400m_e31", False))
    parser.add_argument("--ViTB32quickgelu_laion400m_e32", help="Use ViTB32quickgelu_laion400m_e32 model", type=str2bool, default=gp("ViTB32quickgelu_laion400m_e32", False))
    parser.add_argument("--ViTB16_laion400m_e31", help="Use ViTB16_laion400m_e31 model", type=str2bool, default=gp("ViTB16_laion400m_e31", False))
    parser.add_argument("--ViTB16_laion400m_e32", help="Use ViTB16_laion400m_e32 model", type=str2bool, default=gp("ViTB16_laion400m_e32", False))
    parser.add_argument("--RN50_yffcc15m", help="Use RN50_yffcc15m model", type=str2bool, default=gp("RN50_yffcc15m", False))
    parser.add_argument("--RN50_cc12m", help="Use RN50_cc12m model", type=str2bool, default=gp("RN50_cc12m", False))
    parser.add_argument("--RN50_quickgelu_yfcc15m", help="Use RN50_quickgelu_yfcc15m model", type=str2bool, default=gp("RN50_quickgelu_yfcc15m", False))
    parser.add_argument("--RN50_quickgelu_cc12m", help="Use RN50_quickgelu_cc12m model", type=str2bool, default=gp("RN50_quickgelu_cc12m", False))
    parser.add_argument("--RN101_yfcc15m", help="Use RN101_yfcc15m model", type=str2bool, default=gp("RN101_yfcc15m", False))
    parser.add_argument("--RN101_quickgelu_yfcc15m", help="Use RN101_quickgelu_yfcc15m model", type=str2bool, default=gp("RN101_quickgelu_yfcc15m", False))
    parser.add_argument(
        "--diffusion_model",
        help="Diffusion Model",
        default=gp("diffusion_model", "512x512_diffusion_uncond_finetune_008100"),
        choices=[
            "512x512_diffusion_uncond_finetune_008100",
            "256x256_diffusion_uncond",
            "pixel_art_diffusion_hard_256",
            "pixel_art_diffusion_soft_256",
            "pixelartdiffusion_expanded",
            "pixelartdiffusion4k",
            "PADexpanded",
            "watercolordiffusion",
            "watercolordiffusion_2",
            "PulpSciFiDiffusion",
            "256x256_openai_comics_faces_by_alex_spirin_084000",
            "lsun_uncond_100M_1200K_bs128",
            "ukiyoe_diffusion_256_022000.pt",
            "liminal_diffusion",
        ],
    )
    parser.add_argument("--use_secondary_model", help="Use RN101 model", type=str2bool, default=gp("use_secondary_model", True))
    parser.add_argument("--diffusion_sampling_mode", help="Diffusion Sampling Mode", default=gp("diffusion_sampling_mode", "ddim"), choices=["plms", "ddim"])
    parser.add_argument("--width_height", help="Width, Height", type=str2json, default=gp("width_height", [1280, 768]), required=False)
    parser.add_argument("--clip_guidance_scale", help="CLIP Guidance Scale", type=int, default=gp("clip_guidance_scale", 5000), required=False)
    parser.add_argument("--tv_scale", help="TV Scale", type=int, default=gp("tv_scale", 0), required=False)
    parser.add_argument("--range_scale", help="Range Scale", type=int, default=gp("range_scale", 150), required=False)
    parser.add_argument("--sat_scale", help="Saturation Scale", type=int, default=gp("sat_scale", 0), required=False)
    parser.add_argument("--cutn_batches", help="Cut Batches", type=int, default=gp("cutn_batches", 4), required=False)
    parser.add_argument("--skip_augs", help="Skip Augmentations", type=str2bool, default=gp("skip_augs", False), required=False)
    parser.add_argument("--init_image", help="Init Image", default=gp("init_image", None), required=False)
    parser.add_argument("--target_image", help="Target Image", default=gp("target_image", None), required=False)
    parser.add_argument("--init_scale", help="Init Scale", type=int, default=gp("range_scale", 1000), required=False)
    parser.add_argument("--target_scale", help="Target Scale", type=int, default=gp("target_scale", 20000), required=False)
    parser.add_argument("--skip_steps", help="Skip Steps", type=int, default=gp("skip_steps", 10), required=False)
    parser.add_argument("--animation_mode", help="Animation Mode", default=gp("animation_mode", "None"), choices=["None", "2D", "3D", "Video Input"], required=False)
    parser.add_argument("--video_init_path", help="Init Video Path", default=gp("video_init_path", "training.mp4"), required=False)
    parser.add_argument("--extract_nth_frame", help="Extract Nth Frame", type=int, default=gp("extract_nth_frame", 2), required=False)
    parser.add_argument("--video_init_seed_continuity", help="Init Video Seed Continuity", type=str2bool, default=gp("video_init_seed_continuity", True), required=False)
    parser.add_argument("--key_frames", help="Key Frames", type=str2bool, default=gp("key_frames", True), required=False)
    parser.add_argument("--max_frames", help="Max Frames", type=int, default=gp("max_frames", 10000), required=False)
    parser.add_argument("--interp_spline", help="Interp Spline", default=gp("interp_spline", "Linear"), choices=["Linear", "Quadratic", "Cubic"], required=False)
    parser.add_argument("--angle", help="Angle", default=gp("angle", "0:(0)"), required=False)
    parser.add_argument("--zoom", help="Zoom", default=gp("zoom", '"0: (1), 10: (1.05)"'), required=False)
    parser.add_argument("--translation_x", help="Translation X", default=gp("translation_x", "0: (0)"), required=False)
    parser.add_argument("--translation_y", help="Translation Y", default=gp("translation_y", "0: (0)"), required=False)
    parser.add_argument("--translation_z", help="Translation Z", default=gp("translation_z", "0: (10.0)"), required=False)
    parser.add_argument("--rotation_3d_x", help="Rotation 3D X", default=gp("rotation_3d_x", "0: (0)"), required=False)
    parser.add_argument("--rotation_3d_y", help="Rotation 3D Y", default=gp("rotation_3d_y", "0: (0)"), required=False)
    parser.add_argument("--rotation_3d_z", help="Rotation 3D Z", default=gp("rotation_3d_z", "0: (0)"), required=False)
    parser.add_argument("--midas_depth_model", help="MiDAS Depth Model", default=gp("midas_depth_model", "dpt_large"), required=False)
    parser.add_argument("--midas_weight", help="MiDAS Weight", type=float, default=gp("midas_weight", 0.3), required=False)
    parser.add_argument("--near_plane", help="Near Plane", type=int, default=gp("near_plane", 200), required=False)
    parser.add_argument("--far_plane", help="Far Plane", type=int, default=gp("far_plane", 10000), required=False)
    parser.add_argument("--fov", help="FOV", type=int, default=gp("fov", 40), required=False)
    parser.add_argument("--padding_mode", help="Padding Mode", default=gp("padding_mode", "border"), required=False)
    parser.add_argument("--sampling_mode", help="Sampling Mode", default=gp("sampling_mode", "bicubic"), required=False)
    parser.add_argument("--turbo_mode", help="Turbo Mode", type=str2bool, default=gp("turbo_mode", False), required=False)
    parser.add_argument("--turbo_steps", help="Turbo Steps", type=int, default=gp("turbo_steps", 3), required=False)
    parser.add_argument("--turbo_preroll", help="Turbo Pre-roll", type=int, default=gp("turbo_preroll", 10), required=False)
    parser.add_argument("--frames_scale", help="Frames Scale", type=int, default=gp("frames_scale", 1500), required=False)
    parser.add_argument("--frames_skip_steps", help="Frames Skip Steps", default=gp("frames_skip_steps", "60%"), required=False)
    parser.add_argument("--vr_mode", help="VR Mode", type=str2bool, default=gp("vr_mode", False), required=False)
    parser.add_argument("--vr_eye_angle", help="VR Eye Angle", type=float, default=gp("vr_eye_angle", 0.5), required=False)
    parser.add_argument("--vr_ipd", help="VR IPD", type=float, default=gp("vr_ipd", 5.0), required=False)
    parser.add_argument("--intermediate_saves", help="Intermediate Saves", type=int, default=gp("intermediate_saves", 0), required=False)
    parser.add_argument("--intermediates_in_subfolder", help="Intermediates in Subfolder", type=str2bool, default=gp("intermediates_in_subfolder", True), required=False)
    parser.add_argument("--init_generator", help="Init Generator", default=gp("init_generator", "perlin"), choices=["perlin", "voronoi"], required=False)
    parser.add_argument("--voronoi_points", help="Voronoi Points", default=gp("voronoi_points", 200), type=int, required=False)
    parser.add_argument("--voronoi_palette", help="Voronoi Palette", default=gp("voronoi_palette", "default.yaml"), required=False)
    parser.add_argument("--perlin_init", help="Perlin Init", type=str2bool, default=gp("perlin_init", False), required=False)
    parser.add_argument("--perlin_mode", help="Perlin Mode", default=gp("perlin_mode", "mixed"), choices=["mixed", "color", "gray"], required=False)
    parser.add_argument("--set_seed", help="Seed", default=gp("set_seed", "random_seed"), required=False)
    parser.add_argument("--eta", help="ETA", type=float, default=gp("eta", 0.8), required=False)
    parser.add_argument("--clamp_grad", help="Clamp Gradient", type=str2bool, default=gp("clamp_grad", True), required=False)
    parser.add_argument("--clamp_max", help="Clamp Max", type=float, default=gp("clamp_max", 0.05), required=False)
    parser.add_argument("--randomize_class", help="Randomize Class", type=str2bool, default=gp("randomize_class", True), required=False)
    parser.add_argument("--clip_denoised", help="Clip Denoised", type=str2bool, default=gp("clip_denoised", False), required=False)
    parser.add_argument("--fuzzy_prompt", help="Fuzzy Prompt", type=str2bool, default=gp("fuzzy_prompt", False), required=False)
    parser.add_argument("--rand_mag", help="Rand Mag", type=float, default=gp("rand_mag", 0.05), required=False)
    parser.add_argument("--n_batches", help="Number of Batches", type=int, default=gp("n_batches", 50), required=False)
    parser.add_argument("--display_rate", help="Display Rate", type=int, default=gp("display_rate", 50), required=False)
    parser.add_argument("--cut_overview", help="Cut Overview", default=gp("cut_overview", "[12]*400+[4]*600"), required=False)
    parser.add_argument("--cut_innercut", help="Cut Innercut", default=gp("cut_innercut", "[4]*400+[12]*600"), required=False)
    parser.add_argument("--cut_icgray_p", help="Cut IC Gray Power", default=gp("cut_icgray_p", "[0.2]*400+[0]*600"), required=False)
    # TODO: Check for regressions
    # parser.add_argument("--cut_ic_pow", help="Cut IC Power", default=gp("cut_ic_pow", "[1]*1000"), required=False)
    parser.add_argument("--cut_ic_pow", help="Cut IC Power", type=int, default=gp("cut_ic_pow", 1), required=False)
    parser.add_argument("--resume_run", help="Resume Run", type=str2bool, default=gp("resume_run", False), required=False)
    parser.add_argument("--run_to_resume", help="Run to Resume", default=gp("run_to_resume", "latest"), required=False)
    parser.add_argument("--resume_from_frame", help="Resume from Frame", default=gp("resume_from_frame", "latest"), required=False)
    parser.add_argument("--retain_overwritten_frames", help="Retain Overwritten Frames", type=str2bool, default=gp("retain_overwritten_frames", False), required=False)
    parser.add_argument("--skip_video_for_run_all", help="Skip Video Creation", type=str2bool, default=gp("skip_video_for_run_all", False), required=False)
    parser.add_argument("--check_model_SHA", help="Check Model Hash", type=str2bool, default=gp("check_model_SHA", False), required=False)
    # Deprecated Symmetry args
    # parser.add_argument("--symmetry_loss", help="(Deprecated) Symmetry Loss", type=str2bool, default=gp("symmetry_loss", False), required=False)
    # parser.add_argument("--symmetry_loss_scale", help="(Deprecated) Symmetry Loss Scale", type=int, default=gp("symmetry_loss_scale", 1500), required=False)
    # parser.add_argument("--symmetry_switch", help="(Deprecated) Symmetry Switch", type=int, default=gp("symmetry_switch", 40), required=False)
    # parser.add_argument("--v_symmetry_loss", help="(Deprecated) Vertical Symmetry Loss", type=str2bool, default=gp("v_symmetry_loss", False), required=False)
    # parser.add_argument("--v_symmetry_loss_scale", help="(Deprecated) Vertical Symmetry Loss Scale", type=int, default=gp("v_symmetry_loss_scale", 1500), required=False)
    # parser.add_argument("--v_symmetry_switch", help="(Deprecated) Vertical Symmetry Switch", type=int, default=gp("v_symmetry_switch", 40), required=False)
    # New Symmetry args
    parser.add_argument("--use_vertical_symmetry", help="Use Vertical Symmetry", type=str2bool, default=gp("use_vertical_symmetry", False), required=False)
    parser.add_argument("--use_horizontal_symmetry", help="Use Horizontal Symmetry", type=str2bool, default=gp("use_horizontal_symmetry", False), required=False)
    parser.add_argument("--transformation_percent", type=str2json, help="Symmetry Transformation Percent", default=gp("transformation_percent", "[0.09]"), required=False)
    # Twilio SMS args
    parser.add_argument("--twilio_account_sid", help="Twilio Account SID", type=int, default=gp("twilio_account_sid", None), required=False)
    parser.add_argument("--twilio_auth_token", help="Twilio Auth Token", type=int, default=gp("twilio_auth_token", None), required=False)
    parser.add_argument("--twilio_to", help="Twilio SMS recipient", type=int, default=gp("twilio_to", None), required=False)
    parser.add_argument("--twilio_from", help="Twilio SMS sender", type=int, default=gp("twilio_from", None), required=False)
    parser.add_argument("--per_job_kills", help="Allow Control+C killing of single batches", type=str2bool, default=gp("per_job_kills", False), required=False)
    parser.add_argument("--dd_bot", help="Enable DD Discord Bot mode", type=str2bool, default=gp("dd_bot", False), required=False)
    parser.add_argument("--dd_bot_url", help="DD Discord Bot URL", default=gp("dd_bot_url", "http://your-bot.com:5000/"), required=False)
    parser.add_argument("--dd_bot_agentname", help="DD Discord Bot Agent Name", default=gp("dd_bot_agentname", "james-bond"), required=False)
    parser.add_argument(
        "--gen_config",
        help="Generate initial configurations",
        type=str,
        default="AUTO",
        required=False,
    )
    parser.add_argument(
        "--gen_config_only",
        help="Generate initial configurations and exit",
        type=str2bool,
        default=False,
        required=False,
    )
    parser.add_argument(
        "--config_file",
        help="Configuration file to use instead of command-line arguments",
        type=str,
        default=None,
        required=False,
    )
    if a == None:
        return parser.parse_args()
    else:
        return parser.parse_args(a)


# Thanks, https://github.com/aredden
def arg_configuration_loader(args: Union[pydot, dict] = None) -> pydot:
    ignorelist = ["f", "ip", "stdin", "control", "hb", "Session.key", "Session.signature_scheme", "shell", "transport", "iopub"]
    # get args if loader called without cli-arguments.
    cliargs = parse().__dict__
    defaults = parse([]).__dict__

    if args is None:
        logger.debug("No arguments directly passed.")
        args = parse().__dict__
    else:
        for arg in args:
            if arg not in ignorelist:
                if cliargs[arg]:
                    # cliargs[arg] = args[arg]
                    pass
                else:
                    cliargs[arg] = args[arg]
        logger.debug(f"Arguments directly passed:\n\n{args}")

    # Check whether 'args' is a dict, which would error, since using dot access.
    if type(args) == dict:
        confargs = pydot(args)
    else:
        confargs = args  # NB support

    # Try loading config from config_file cli-argument if exists.
    if confargs.config_file is not None:
        logger.info("Attempting to load configuration from: " + confargs.config_file)
        try:
            with open(confargs.config_file, "r") as conf:
                confargs = pydot(full_load(conf))
        except Exception as e:
            logger.error(
                f"Could not load configuration file! There was an error loading from {confargs.config_file}" + "\nCheck to make sure it exists, and is formatted correctly."
            )
            logger.warning(
                "\n".join(traceback.format_exception(type(e), e, e.__traceback__, limit=4)),
            )
            exit(0)
        logger.info("Loaded configuration arguments.")

    # Override args that came from CLI
    for arg in cliargs:
        if arg not in confargs and arg not in ignorelist:
            logger.debug(f"Found CLI argument '{arg}' value '{cliargs[arg]}' not present in config file.  Adding anyway...")
            confargs[arg] = cliargs[arg]

        c = DeepHash(cliargs[arg])[cliargs[arg]]
        d = DeepHash(defaults[arg])[defaults[arg]]

        if c != d:
            logger.info(f"Overriding config file parameter '{arg}' value to '{cliargs[arg]}' found in CLI.")
            confargs[arg] = cliargs[arg]

    # Override if sent straight to function
    # for arg in args:
    #     if arg not in confargs and arg not in ignorelist:
    #         logger.debug(f"Found function argument '{arg}' value '{cliargs[arg]}' not present in CLI or Config file.  Adding...")
    #         confargs[arg] = args[arg]

    #     c = DeepHash(cliargs[arg])[cliargs[arg]]
    #     d = DeepHash(args[arg])[args[arg]]

    #     if c != d:
    #         logger.info(f"Overriding config file parameter '{arg}' value to '{cliargs[arg]}' found in function args.")
    #         confargs[arg] = cliargs[arg]

    # Check if user wants to generate a defaults configuration file.
    if confargs.gen_config != "":
        confgen = confargs.gen_config
        if confgen == "AUTO":
            confgen = f"configs/{confargs.batch_name}_gen.yaml"

        if confgen.endswith(".yml") or confgen.endswith(".yaml"):
            gco = confargs.gen_config_only
            try:  # b/w compat
                del confargs.gen_config
                del confargs.config_file
                del confargs.gen_config_only
            except:
                pass
            dump(confargs.todict(), open(confgen, "w"))
            logger.info("Configuration saved in " + confgen)
            if gco == True:
                exit(0)
        else:
            logger.warning("Configuration file output must be a YAML file, ending with .yml or .yaml\n" + "Example: python disco.py --gen_config defaults.yml")
            exit(0)
    return confargs
