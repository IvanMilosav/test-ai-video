video_model_fast = "veo-3.1-fast-generate-001"

from google import genai
from google.genai import types

print(prompt)
enhance_prompt = True  # @param {type: 'boolean'}
generate_audio = True  # @param {type: 'boolean'}

operation = client.models.generate_videos(
    model=video_model,
    prompt=prompt,
    config=types.GenerateVideosConfig(
        aspect_ratio="16:9",
        number_of_videos=1,
        duration_seconds=6,
        resolution="1080p",
        person_generation="allow_adult",
        enhance_prompt=enhance_prompt,
        generate_audio=generate_audio,
    ),
)

while not operation.done:
    time.sleep(15)
    operation = client.operations.get(operation)
    print(operation)

if operation.response:
    show_video(operation.result.generated_videos[0].video.video_bytes)


## FROM IMAGE

print(prompt)
enhance_prompt = True  # @param {type: 'boolean'}
generate_audio = True  # @param {type: 'boolean'}

operation = client.models.generate_videos(
    model=video_model,
    prompt=prompt,
    image=types.Image.from_file(location=starting_image),
    config=types.GenerateVideosConfig(
        aspect_ratio="16:9",
        number_of_videos=1,
        duration_seconds=6,
        resolution="720p",
        person_generation="allow_adult",
        enhance_prompt=enhance_prompt,
        generate_audio=generate_audio,
    ),
)

while not operation.done:
    time.sleep(15)
    operation = client.operations.get(operation)
    print(operation)

if operation.response:
    show_video(operation.result.generated_videos[0].video.video_bytes)

