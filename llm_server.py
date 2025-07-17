from pathlib import Path
from llama_cpp import Llama
from fastapi import FastAPI, Request
from config import MODEL_PATH, SYS_PROMPT

# メッセージ履歴の制限
max_messages = 10

app = FastAPI()

base_dir = Path(__file__).resolve().parent
model_path = base_dir / MODEL_PATH

llm = Llama(
    model_path=str(model_path),
    n_ctx=2000,
)

messages = []
# システムロールのないモデル(llm-jp3とか)はuserにする必要がある
messages.append({"role": "system", "content": SYS_PROMPT})

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

    while len(messages) > max_messages:
        messages.pop(2) # 先頭のユーザーメッセージを削除(システムプロンプト除く)
    print(messages)
    return {"text": output["choices"][0]["message"]["content"]}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
