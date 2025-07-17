from pathlib import Path
from llama_cpp import Llama, Gemma3ChatHandler
from fastapi import FastAPI, Request
from config import VISION_MODEL_PATH, SYS_PROMPT, MAX_MESSAGES, MMPROJ_PATH

def image_to_base64_uri(image: bytes | str):
  import base64
  import urllib.request as request

  if isinstance(image, bytes):
    data = base64.b64encode(image).decode('utf-8')
  else:
    with request.urlopen(image) as f:
      data = base64.b64encode(f.read()).decode('utf-8')
  return f'data:image/png;base64,{data}'

app = FastAPI()

base_dir = Path(__file__).resolve().parent
model_path = base_dir / VISION_MODEL_PATH
mmproj_path = base_dir / MMPROJ_PATH

chat_handler = Gemma3ChatHandler(clip_model_path=mmproj_path)
llm = Llama(
    model_path=str(model_path),
    chat_handler=chat_handler,
    n_ctx=1024,
)

messages = []
messages.append({"role": "system", "content": SYS_PROMPT})

@app.post("/generate")
async def generate_text(request: Request):
    data = await request.json()
    user_input = data.get("prompt")
    user_input_image = data.get("image")
    
    if (user_input_image):
      messages.append(
                {
                "role": "user",
                "content": [
                    {'type': 'image_url', 'image_url': user_input_image},
                    {"type" : "text", "text": user_input}
                ]
            }
        )
    else:
      messages.append({"role": "user", "content": user_input})
    
    # 推論
    output = llm.create_chat_completion(
        messages,
        stop=['<end_of_turn>', '<eos>'],
        max_tokens=200,
    )
    
    print(output)
    messages.append(output["choices"][0]["message"])

    while len(messages) > MAX_MESSAGES:
        messages.pop(2) # 先頭のユーザーメッセージを削除(システムプロンプト除く)
    print(messages)
    return {"text": output["choices"][0]["message"]["content"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
