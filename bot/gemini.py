import aiohttp

from bot import config


# =========================
# 共通：リクエストURL・ヘッダ・ペイロードの組み立て
# gemini_generate と gemini_generate_grounded で共有する
# =========================
def _build_request(prompt, system_instruction, max_output_tokens, temperature):
    url = (
        "https://generativelanguage.googleapis.com/v1beta/models/"
        f"{config.GEMINI_MODEL}:generateContent"
    )
    headers = {
        "x-goog-api-key": config.GEMINI_API_KEY,
        "Content-Type": "application/json",
    }
    payload = {
        "contents": [{"parts": [{"text": prompt}]}],
        "generationConfig": {
            "maxOutputTokens": max_output_tokens,
            "temperature": temperature,
        },
    }
    if system_instruction:
        payload["systemInstruction"] = {"parts": [{"text": system_instruction}]}
    return url, headers, payload


# 応答JSONから本文テキストを連結して取り出す
def _extract_text(data):
    parts = data["candidates"][0]["content"]["parts"]
    return "".join(p.get("text", "") for p in parts).strip()


# =========================
# Gemini汎用生成（セバスチャンの応答用）
# 出力トークンに上限を設けて料金を抑える
# =========================
async def gemini_generate(
    prompt,
    system_instruction=None,
    max_output_tokens=256,
    temperature=1.0,
):
    if not config.GEMINI_API_KEY:
        return None

    url, headers, payload = _build_request(
        prompt, system_instruction, max_output_tokens, temperature
    )

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=headers, json=payload, timeout=30
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()

        return _extract_text(data)
    except Exception as e:
        print(f"Gemini生成エラー: {e}")
        return None


# =========================
# Google検索グラウンディング付き生成（/ask の通常質問用）
# google_search ツールを付与し、Geminiが必要に応じてWeb検索して回答する。
# 検索しないと分からない時事・固有の事実にも対応できる。
# 戻り値: (本文text, 出典sources) sources は [(title, uri), ...]（無ければ空）
# =========================
async def gemini_generate_grounded(
    prompt,
    system_instruction=None,
    max_output_tokens=512,
    temperature=1.0,
):
    if not config.GEMINI_API_KEY:
        return None, []

    url, headers, payload = _build_request(
        prompt, system_instruction, max_output_tokens, temperature
    )
    # Gemini 2.x/3.x 系の正しい形式（1.5系の google_search_retrieval ではない）
    payload["tools"] = [{"google_search": {}}]

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                url, headers=headers, json=payload, timeout=30
            ) as resp:
                resp.raise_for_status()
                data = await resp.json()

        text = _extract_text(data)
        sources = _extract_sources(data)
        return text, sources
    except Exception as e:
        print(f"Geminiグラウンディング生成エラー: {e}")
        return None, []


# 応答JSONの groundingMetadata から出典 (title, uri) を取り出す。
# 検索が走らなかった応答では groundingChunks が無いので空リストを返す。
def _extract_sources(data):
    try:
        chunks = (
            data["candidates"][0]
            .get("groundingMetadata", {})
            .get("groundingChunks", [])
        )
    except (KeyError, IndexError):
        return []

    sources = []
    seen = set()
    for chunk in chunks:
        web = chunk.get("web") or {}
        uri = web.get("uri")
        if not uri or uri in seen:
            continue
        seen.add(uri)
        sources.append((web.get("title", uri), uri))
    return sources
