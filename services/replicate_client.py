import replicate
import os
from config import REPLICATE_API_TOKEN

async def generar_video(imagen_url, audio_url):
    output = replicate.run(
        "cjwbw/sadtalker:3aa3dac9353cc4d6bd62a8f95957bd844003b401ca4e4a9b33baa574c549d376",
        input={
            "source_image": imagen_url,
            "driven_audio": audio_url,
            "preprocess": "full",
            "still_mode": False,
            "use_enhancer": True,
            "batch_size": 1,
            "size": 256,
            "pose_style": 0,
            "facerender": "facevid2vid",
            "exp_scale": 1.0
        }
    )
    return output
