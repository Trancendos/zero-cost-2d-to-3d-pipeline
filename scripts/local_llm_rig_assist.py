"""Loopback-only Ollama/LM Studio parameter advice; never executes model-generated commands."""
import json, urllib.error, urllib.request
from urllib.parse import urlparse

DEFAULT={"top_k":5,"top_p":0.95,"temperature":1.0,"repetition_penalty":2.0,"num_beams":10}
LIMITS={"top_k":(1,200),"top_p":(0.1,1.0),"temperature":(0.1,2.0),"repetition_penalty":(0.5,3.0),"num_beams":(1,20)}

def safe_base(url):
    p=urlparse(url)
    if p.scheme!="http" or p.hostname not in {"127.0.0.1","localhost","::1"} or p.username or p.password:
        raise ValueError("Local LLM endpoint must use HTTP loopback only.")
    return url.rstrip("/")

def clamp(data):
    if not isinstance(data,dict): return dict(DEFAULT)
    result={}
    for key,(lo,hi) in LIMITS.items():
        try:
            value=float(data.get(key,DEFAULT[key]))
            if not lo <= value <= hi: value=DEFAULT[key]
            result[key]=int(round(value)) if key in {"top_k","num_beams"} else value
        except (TypeError,ValueError): result[key]=DEFAULT[key]
    return result

def recommend(provider="ollama",model="qwen2.5:3b",base_url=None,timeout=8):
    try:
        if provider=="ollama":
            url=safe_base(base_url or "http://127.0.0.1:11434")+"/api/generate"
            body={"model":model,"stream":False,"format":"json","prompt":"Return JSON only with top_k, top_p, temperature, repetition_penalty, num_beams. Use conservative 3D rigging sampling parameters. No commands or paths."}
        elif provider=="lmstudio":
            url=safe_base(base_url or "http://127.0.0.1:1234")+"/v1/chat/completions"
            body={"model":model,"stream":False,"temperature":0,"response_format":{"type":"json_object"},"messages":[{"role":"system","content":"Return JSON only with top_k, top_p, temperature, repetition_penalty, num_beams. No commands or paths."},{"role":"user","content":"Suggest conservative rigging sampling parameters."}]}
        else: return dict(DEFAULT),"Unknown local provider; safe defaults used."
        req=urllib.request.Request(url,data=json.dumps(body).encode(),headers={"Content-Type":"application/json"},method="POST")
        with urllib.request.urlopen(req,timeout=max(1,min(int(timeout),20))) as response: payload=json.loads(response.read(256000).decode())
        text=payload.get("response","{}") if provider=="ollama" else payload["choices"][0]["message"]["content"]
        return clamp(json.loads(text)),"Local LLM recommendation bounded and accepted."
    except (OSError,ValueError,KeyError,TypeError,urllib.error.URLError,json.JSONDecodeError) as e:
        return dict(DEFAULT),f"Local LLM unavailable/invalid; safe defaults used ({type(e).__name__})."
