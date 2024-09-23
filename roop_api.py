from fastapi import FastAPI, File, UploadFile
from fastapi.responses import StreamingResponse
from io import BytesIO
from PIL import Image
import subprocess
import os

app = FastAPI()

@app.post("/predict")
async def predict(image1: UploadFile = File(...), image2: UploadFile = File(...)):
    # Load and process the images
    image_data1 = await image1.read()
    image_data2 = await image2.read()
    
    img1 = Image.open(BytesIO(image_data1))
    img2 = Image.open(BytesIO(image_data2))
    
    # Process the images
    output_image = swap_faces_cli(img1, img2)

    # Convert output image to BytesIO object for response
    buf = BytesIO()
    output_image.save(buf,'png')
    buf.seek(0)

    return StreamingResponse(buf, media_type="image/jpeg")

def swap_faces_cli(source_image: Image, target_image: Image) -> Image:
    # Define paths for temporary files
    source_path = "/tmp/input_faces.jpg"
    target_path = "/tmp/target_faces.png"
    output_path = "/tmp/output_faces.jpg"

    # Save images to temporary files
    source_image.save(source_path)
    target_image.save(target_path)

    try:
        # Construct and execute the command
        command = f"python run.py -s {source_path} -t {target_path} -o {output_path}"
        subprocess.run(command, shell=True, check=True)
        
        # Load and return the output image
        output_image = Image.open(output_path)
        return output_image
    except subprocess.CalledProcessError as e:
        print(f"Error occurred: {e}")
        raise RuntimeError("An error occurred while processing the images.")
    finally:
        # Clean up temporary files
        #os.remove(source_path)
        #os.remove(target_path)
        #os.remove(output_path)
        pass



# To run the API on localhost:8000:
# uvicorn roop_api:app --host localhost --port 8000