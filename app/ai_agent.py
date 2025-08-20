import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("AI")

def classify_issue(description):
    """简单 AI 分类（可替换成 OpenAI API）"""
    desc = description.lower()
    if "leak" in desc or "water" in desc:
        return ("Plumbing", "High")
    if "electric" in desc:
        return ("Electrical", "High")
    if "ac" in desc or "aircon" in desc:
        return ("HVAC", "Medium")
    return ("General", "Low")

def recommend_solutions(description, collection, top_k=3):
    """从 ChromaDB 搜索解决方案"""
    results = collection.query(query_texts=[description], n_results=top_k, include=["documents", "metadatas"])
    recs = []
    if results and results["documents"][0]:
        for i, doc in enumerate(results["documents"][0]):
            meta = results["metadatas"][0][i]
            recs.append({
                "title": meta.get("title", f"Solution {i+1}"),
                "snippet": doc[:200] + "..." if len(doc) > 200 else doc,
                "source": meta.get("source", "knowledge")
            })
    return recs
