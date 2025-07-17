from pathlib import Path
from llama_cpp import Llama
from fastapi import FastAPI, Request
from config import MODEL_PATH, SYS_PROMPT, SYS_PROMPT_REPLY, MAX_MESSAGES

app = FastAPI()

base_dir = Path(__file__).resolve().parent
model_path = base_dir / MODEL_PATH

llm = Llama(
    model_path=str(model_path),
    n_ctx=2000,
)

messages = []
# gemmaはシステムロールなし&ユーザー，アシスタントの繰り返ししか許可しないため
messages.append({"role": "user", "content": SYS_PROMPT})
messages.append({"role": "assistant", "content": SYS_PROMPT_REPLY})

@app.post("/generate")
async def generate_text(request: Request):
    data = await request.json()
    user_input = data.get("prompt")
    
    messages.append({"role": "user", "content": user_input})

    # 推論
    output = llm.create_chat_completion(
        messages,
        stop=["###","</s>","�"]
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
