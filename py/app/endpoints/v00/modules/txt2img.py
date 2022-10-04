# AI ML imports
from torch import autocast, Generator, float16, cuda
from diffusers import StableDiffusionPipeline

# Object models import
from app.models.fvsion import FvsionModel


# Utility imports
from app.endpoints.v00.modules import utils


def wrapper(fv: FvsionModel):
    
    # Parameters and settings
    # Need to find a way to make this more robust... , e.g. join?
    pathToLocalModel = fv.pathToLocalModel
    pathToOutput = fv.pathToOutput

    # if folder has fp16 mentioned, use fp16
    if "fp16" in pathToLocalModel:
        revision = "fp16"
    else:
        revision = "main"

    utils.createFolder(pathToOutput)

    cuda.reset_peak_memory_stats()
    # DIFFUSERS: setup diffusers pipe
    gen = Generator("cuda").manual_seed(fv.seed)

    pipe = StableDiffusionPipeline.from_pretrained(pathToLocalModel, revision=revision, torch_dtype=float16, use_auth_token=False)
    pipe.set_progress_bar_config(disable=None)


    # enable/disable safety (NSFW) checker
    if(fv.allowNSFW):
        pipe.safety_checker = utils.dummy

    # reduce VRAM requirement
    pipe.enable_attention_slicing()

    # send to CUDA for NVIDIA GPU
    pipe = pipe.to("cuda")

    print("Complete pipe setup. Starting image generation.")

    # print(fv) # diagnostic

    # the actual generation happens here.
    try:
        with autocast("cuda"):
            images = pipe(fv.prompt,  height=fv.height, width=fv.width, num_inference_steps=fv.num_inference_steps, 
            guidance_scale = fv.guidance_scale,  generator=gen, eta = fv.eta).images  

        print(f"Completed Generation. Attempting to save {len(images)} file(s)")

        mem_bytes = float(cuda.max_memory_allocated()) / (10**9)
        print("{:.1f}".format(mem_bytes) + " GB of VRAM used by cuda directly")
        cuda.reset_peak_memory_stats()
    except Exception as e:
        print(e)
        return e   

    # UTILITY: saving the file to a unique name, if fails, try one more time, which will generate a new secret
    try:
        utils.saveOutput(fv=fv, pathToOutput=pathToOutput, image=images)
        print(f"successfully saved {len(images)} files")
    except:
        try:
            utils.saveOutput(fv=fv, pathToOutput=pathToOutput, image=images)
            print(f"successfully saved {len(images)} files")
        except Exception as e:
            print(e)
            return e 

    # if successful return fv
    return fv