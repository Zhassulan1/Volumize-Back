import gradio_client
from gradio_client import Client
from os import path 

client = Client("TencentARC/InstantMesh")


def check_input_image(file_url):
    result = client.predict(
        gradio_client.file(file_url),
		api_name="/check_input_image"
    )
    print("Image check: ", result)


def preprocess(file_url, foreground_ratio):
    result = client.predict(
		gradio_client.file(file_url),
		True,	# bool  in 'Remove Background' Checkbox component
		foreground_ratio,	# float (numeric value between 0.5 and 1.0) in 'Foreground Ratio' Slider component
		api_name="/preprocess"
    )
    print("Preprocess: ", result)
    return result


def generate(file_url):
  result = client.predict(
    gradio_client.file(file_url),
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




def gen(file_url):
    is_valid = not (check_input_image(file_url))
    if is_valid:
      without_bg = preprocess(file_url, foreground_ratio=0.5)
      obj_path = generate(without_bg)
      return obj_path
    return None