import json
import os
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt

from volumize.generate_mesh import check_input_image, preprocess, generate, text_to_image
import requests as r
from volumize.s3 import upload_bytes, upload_file, generate_key


# @csrf_exempt
# def upload_image(request):
#     if request.method == 'POST' and request.FILES['image']:
#         image = request.FILES['image']
#         image_key = generate_key()
#         image_url = upload_bytes(image, image_key)

#         obj_path = gen(image_url)

#         if obj_path:
#             obj_key = generate_key('user', "obj", os.path.basename(obj_path))
#             obj_url = upload_file(obj_path, obj_key)

#             return JsonResponse({'obj_url': obj_url})
            

#         return JsonResponse({'error': 'No file uploaded'}, status=400)
#     return JsonResponse({'error': 'No file uploaded'}, status=400)

@csrf_exempt
def healthcheck(request):
    print("Health check")
    res = r.get("http://localhost:6969/healthcheck")
    print(res.content)
    return JsonResponse({'status': res.content.decode('ascii')})

@csrf_exempt
def generate_image(request):
    if request.method == 'POST' :
        try:
            data = json.loads(request.body)
            print(f"Parsed JSON data: {data}")
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        try:
            prompt = data.get('prompt')
            print(f"Prompt: {prompt}")
        except Exception as e:
            return JsonResponse({'error': 'Unexpected Fields'}, status=400)

        file_path = text_to_image(prompt)
        print("File path: ", file_path)
        file_key = generate_key('user', "textgen", os.path.basename(file_path))
        file_url = upload_file(file_path, file_key)
        return JsonResponse({'file_url': file_url})
    
    return JsonResponse({'error': 'No file uploaded or invalid method'}, status=400)




@csrf_exempt
def process_url(request):
    if request.method == 'POST' :
        try:
            data = json.loads(request.body)
            print(f"Parsed JSON data: {data}")
        except json.JSONDecodeError as e:
            print(f"JSONDecodeError: {e}")
            return JsonResponse({'error': 'Invalid JSON'}, status=400)
        try:
            image_url = data.get('image_url')
            print(f"Prompt: {image_url}")
        except Exception as e:
            return JsonResponse({'error': 'Unexpected Fields'}, status=400)

        if check_input_image(image_url) == ():
            print("Invalid image")
            return JsonResponse({'error': 'Invalid image'}, status=400)

        processed_path = preprocess(image_url, foreground_ratio=0.5)

        if processed_path:
            processed_image_key = generate_key('user', "processed", os.path.basename(processed_path))
            processed_image_url = upload_file(processed_path, processed_image_key)

            return JsonResponse({'image_url': processed_image_url})

    
    return JsonResponse({'error': 'No file uploaded or invalid method'}, status=400)




@csrf_exempt
def process(request):
    if request.method == 'POST' and request.FILES['image']:
        image = request.FILES['image']
        image_key = generate_key('user', "original", image.name)
        image_url = upload_bytes(image, image_key)

        if check_input_image(image_url) == ():
            print("Invalid image")
            return JsonResponse({'error': 'Invalid image'}, status=400)

        processed_path = preprocess(image_url, foreground_ratio=0.5)

        if processed_path:
            processed_image_key = generate_key('user', "processed", os.path.basename(processed_path))
            processed_image_url = upload_file(processed_path, processed_image_key)

            return JsonResponse({'image_url': processed_image_url})
            

        return JsonResponse({'error': 'No file uploaded'}, status=400)
    return JsonResponse({'error': 'No file uploaded'}, status=400)


@csrf_exempt
def make_3d(request):
    print(f"Request method: {request.method}")
    print(f"Request body: {request.body}")

    try:
        data = json.loads(request.body)
        print(f"Parsed JSON data: {data}")
    except json.JSONDecodeError as e:
        print(f"JSONDecodeError: {e}")
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    image_url = data.get('image_url')
    print(f"Image URL: {image_url}")

    if request.method == 'POST' and image_url:
        model_path = generate(image_url)
        if model_path:
            model_key = generate_key('user', "obj", os.path.basename(model_path))
            model_url = upload_file(model_path, model_key)
            return JsonResponse({'model_url': model_url})
        else:
            return JsonResponse({'error': 'Model generation failed'}, status=500)

    return JsonResponse({'error': 'No file uploaded or invalid method'}, status=400)