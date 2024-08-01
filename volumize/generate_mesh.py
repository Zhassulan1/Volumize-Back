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
	space_name = MESH_SPACE + str(randint(0, 4))
	print("Space name: ", space_name)
	client = Client(space_name, hf_token=TOKEN)
	return client


def check_input_image(file_url):
	client = init_client()
	try:
		result = client.predict(
			gradio_client.handle_file(file_url),
			api_name="/check_input_image"
		)
	except Exception as err:
		print("Check: ", err)
		return False

	if len(result) != 0:
		print(result)
		return False
	return True


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
	print("MVS: ", result)
	
	result = client.predict(
		api_name="/make3d"
	)
	print("3D: ", path.normpath(result[0]), '\n', path.normpath(result[1]))
	return path.normpath(path.normpath(result[0]))



def text_to_image(prompt: str):
	print("Prompt: ", prompt)
	try:
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
	except Exception as err:
		print("Text: ", err)
		raise err
	
	print("Generated image: ", result)
	return result[0]


def gen(file_url):
	is_valid = not (check_input_image(file_url))
	if is_valid:
		without_bg = preprocess(file_url, foreground_ratio=0.5)
		obj_path = generate(without_bg)
		return obj_path
	return None