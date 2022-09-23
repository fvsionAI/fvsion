# AI ML imports
from torch import autocast, Generator, float16
from diffusers import StableDiffusionInpaintPipeline

# Object models import
from app.models.fvsion import FvsionModel, MaskImageEnum


# Utility imports
import PIL
from app.endpoints.modules import utils
from fastapi.encoders import jsonable_encoder


def wrapper(fv: FvsionModel):
    
    # Parameters and settings
    # Need to find a way to make this more robust... , e.g. join?
    pathToLocalModel = "models/stable-diffusion-v1-4"
    pathToOutput = "output"


    # from diffusers library
    # `Image`, or tensor representing an image batch, to mask `init_image`. White pixels in the mask will be
    # replaced by noise and therefore repainted, while black pixels will be preserved. If `mask_image` is a
    # PIL image, it will be converted to a single channel (luminance) before use. If it's a tensor, it should
    # contain one color channel (L) instead of 3, so the expected shape would be `(B, H, W, 1)`.

    # Try loading init_image and mask_image
    try:
        init_image = utils.initProcessing(fv) 
        print("success loading init_image")
    except Exception as e:
        print("error loading init_image")
        print(e)

    try:
        mask_image = utils.maskProcessing(fv)
        print("success loading masked_image")
    except Exception as e:
        print("error loading mask_image")
        print(e)

    utils.createFolder(pathToOutput)

    # DIFFUSERS: setup diffusers pipe
    gen = Generator("cuda").manual_seed(fv.seed)

    pipe = StableDiffusionInpaintPipeline.from_pretrained(pathToLocalModel, revision="fp16", torch_dtype=float16, use_auth_token=False)


    # enable/disable safety (NSFW) checker
    if(fv.allowNSFW):
        pipe.safety_checker = utils.dummy

    # send to CUDA for NVIDIA GPU
    pipe = pipe.to("cuda")

    # https://github.com/huggingface/diffusers/blob/91db81894b44798649b6cf54be085c205e146805/src/diffusers/pipelines/stable_diffusion/pipeline_stable_diffusion_inpaint.py#L157
    # the actual generation happens here.
    with autocast("cuda"):
        # image = pipe(prompt=fv.prompt, init_image=init_image, mask_image=mask_image,  strength=0.75, generator=gen, eta = fv.eta, num_inference_steps=fv.num_inference_steps, 
        # guidance_scale = fv.guidance_scale).images[0] 
        image = pipe(prompt=fv.prompt, init_image=init_image, mask_image=mask_image,  strength=0.75, generator=gen).images[0] 

    print(f"Completed Generation. Attempting to save file")   


    # UTILITY: saving the file to a unique name, if fails, try one more time, which will generate a new secret

    try:
        utils.saveOutput(fv=fv, pathToOutput=pathToOutput, image=image)
        print("successfully saved files")
        return jsonable_encoder(fv)
    except:
        try:
            utils.saveOutput(fv=fv, pathToOutput=pathToOutput, image=image)
            print("successfully saved files after second attempt")
            return jsonable_encoder(fv)
        except Exception as e:
            print(e)
