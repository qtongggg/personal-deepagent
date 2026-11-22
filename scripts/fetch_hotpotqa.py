import json
import os
import urllib.request

URL = "https://huggingface.co/datasets/namlh2004/hotpotqa/resolve/main/hotpot_dev_distractor_v1.json"
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "benchmarks", "hotpotqa_sample_10.json")

def stream_hotpotqa_samples(num_samples=10):
    print(f"Connecting to Hugging Face HotpotQA repository...")
    req = urllib.request.Request(URL, headers={"User-Agent": "Mozilla/5.0"})
    
    with urllib.request.urlopen(req, timeout=30) as resp:
        # Read until array start '['
        char = resp.read(1).decode("utf-8")
        while char and char != "[":
            char = resp.read(1).decode("utf-8")
            
        items = []
        for i in range(num_samples):
            # Skip delimiter commas and spaces
            c = resp.read(1).decode("utf-8")
            while c in [" ", "\n", "\r", "\t", ","]:
                c = resp.read(1).decode("utf-8")
            if not c or c == "]":
                break
                
            obj_parts = [c]
            brace_count = 1 if c == "{" else 0
            while brace_count > 0:
                chunk = resp.read(1).decode("utf-8")
                if not chunk:
                    break
                obj_parts.append(chunk)
                if chunk == "{":
                    brace_count += 1
                elif chunk == "}":
                    brace_count -= 1
                    
            obj_str = "".join(obj_parts)
            item = json.loads(obj_str)
            items.append(item)
            q = item.get("question", "")
            ans = item.get("answer", "")
            print(f"  [{i+1}/{num_samples}] Q: {q[:70]}... | Ans: {ans}")

    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(items, f, indent=2)
        
    print(f"\n[Success] Saved {len(items)} official HotpotQA samples to: {OUTPUT_FILE}")
    return items

if __name__ == "__main__":
    stream_hotpotqa_samples(num_samples=10)
