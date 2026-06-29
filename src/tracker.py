import json
import os
from datetime import datetime

TRACKER_FILE = "progress.json"

def load_progress():
    if os.path.exists(TRACKER_FILE):
        with open(TRACKER_FILE, "r") as f:
            return json.load(f)
    return []

def save_attempt(chunk_id, question, correct):
    progress = load_progress()
    progress.append({
        "chunk_id": chunk_id,
        "question": question,
        "correct": correct,
        "timestamp": datetime.now().isoformat()
    })
    with open(TRACKER_FILE, "w") as f:
        json.dump(progress, f, indent=2)

def get_weak_chunks():
    progress = load_progress()
    if not progress:
        return {}
    
    chunk_stats = {}
    for attempt in progress:
        cid = attempt["chunk_id"]
        if cid not in chunk_stats:
            chunk_stats[cid] = {"correct": 0, "wrong": 0}
        if attempt["correct"]:
            chunk_stats[cid]["correct"] += 1
        else:
            chunk_stats[cid]["wrong"] += 1
    
    return chunk_stats
if __name__ == "__main__":
    import os
    if os.path.exists("progress.json"):
        os.remove("progress.json")
    
    save_attempt("chunk_0", "What is balance of trade?", correct=False)
    save_attempt("chunk_0", "What is BOP?", correct=True)
    save_attempt("chunk_1", "What are visible items?", correct=False)
    save_attempt("chunk_1", "What is double entry?", correct=False)
    save_attempt("chunk_0", "Define balance of trade", correct=False)
    
    stats = get_weak_chunks()
    print(stats)