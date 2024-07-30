from django.conf import settings
from os import path
from random import randint

from gradio_client import Client
import gradio_client

MESH_SPACE = settings.HUGGINGFACE_SPACE_NAME
TOKEN = settings.HUGGINGFACE_TOKEN


def init_client(is_hard=False):
  if not is_hard:
    return Client("TencentARC/InstantMesh")
  space_name = MESH_SPACE + str(randint(0, 9))
  client = Client(space_name, hf_token=TOKEN)
  return client


def check_input_image(file_url):
  client = init_client()
  result = client.predict(
      gradio_client.handle_file(file_url),
      api_name="/check_input_image"
  )
  print("Image check: ", result)


def preprocess(file_url, foreground_ratio):
  client = init_client()
  result = client.predict(
		gradio_client.handle_file(file_url),
		True,	# bool  in 'Remove Background' Checkbox component
		foreground_ratio,	# float (numeric value between 0.5 and 1.0) in 'Foreground Ratio' Slider component
		api_name="/preprocess"
  )
  print("Preprocess: ", result)
  return result


def generate(file_url):
  client = init_client(is_hard=True)
  result = client.predict(
    gradio_client.handle_file(file_url),
    sample_steps=75,
    sample_seed=42,
    api_name="/generate_mvs"
  )

  print("Generate MVS:", result)
 
  result = client.predict(
    api_name="/make3d"
  )
  print("Make 3D", path.normpath(result[0]), '\n', path.normpath(result[1]))
  return path.normpath(path.normpath(result[0]))



def text_to_image(prompt: str):
  print("Prompt: ", prompt)
  client = Client("stabilityai/stable-diffusion-3-medium")
  result = client.predict(
		prompt=prompt,
		seed=0,
    negative_prompt="cropped, lowres, text, error, cropped, worst quality, low quality, jpeg artifacts, signature, watermark, username, blurry",
		randomize_seed=True,
		width=1024,
		height=1024,
		guidance_scale=5,
		num_inference_steps=28,
		api_name="/infer"
  )
  print("Result from generation: ", result)
  return result[0]


def gen(file_url):
    is_valid = not (check_input_image(file_url))
    if is_valid:
      without_bg = preprocess(file_url, foreground_ratio=0.5)
      obj_path = generate(without_bg)
      return obj_path
    return None