import re

def split_script(script: str, count: int):
    # Keep paragraph boundaries where possible, then balance by word count.
    paras = [p.strip() for p in re.split(r"\n\s*\n", script) if p.strip()]
    if len(paras) >= count:
        groups = [[] for _ in range(count)]
        weights = [0] * count
        for para in paras:
            idx = min(range(count), key=lambda i: weights[i])
            groups[idx].append(para)
            weights[idx] += len(para.split())
        return ["\n\n".join(g) for g in groups if g]
    sentences = re.split(r"(?<=[.!?…])\s+", " ".join(paras))
    groups = [[] for _ in range(count)]
    weights = [0] * count
    for sentence in sentences:
        if not sentence.strip():
            continue
        idx = min(range(count), key=lambda i: weights[i])
        groups[idx].append(sentence.strip())
        weights[idx] += len(sentence.split())
    return [" ".join(g) for g in groups if g]

def visual_prompt(text: str, style: str, index: int, total: int):
    excerpt = " ".join(text.split())[:700]
    return (
        f"Create one visually compelling 16:9 image for scene {index} of {total} in a historical documentary. "
        f"Visual style: {style}. Depict the historical events and people described here: {excerpt}. "
        "Authentic period clothing, architecture, tools and environment; cinematic composition; rich detail; "
        "clear focal subject; no captions, no typography, no logos, no watermark."
    )
