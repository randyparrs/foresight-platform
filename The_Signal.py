# { "Depends": "py-genlayer:test" }

import json
from genlayer import *


class TheSignal(gl.Contract):

    owner: Address
    article_counter: u256
    block_counter: u256
    article_data: DynArray[str]
    category_index: DynArray[str]

    def __init__(self, owner_address: Address):
        if isinstance(owner_address, int):
            self.owner = Address(owner_address.to_bytes(20, 'big'))
        else:
            self.owner = owner_address
        self.article_counter = u256(0)
        self.block_counter = u256(0)

    # ─── VIEW METHODS ───────────────────────────────────────────────────────────

    @gl.public.view
    def get_article(self, article_id: str) -> str:
        title = self._get(article_id, "title")
        if not title:
            return "Article not found"
        return (
            f"ID: {article_id} | "
            f"Title: {title} | "
            f"Category: {self._get(article_id, 'category')} | "
            f"Sentiment: {self._get(article_id, 'sentiment')} | "
            f"Headline: {self._get(article_id, 'headline')} | "
            f"Body: {self._get(article_id, 'body')} | "
            f"Tags: {self._get(article_id, 'tags')} | "
            f"Sources: {self._get(article_id, 'sources')} | "
            f"Block: {self._get(article_id, 'block')}"
        )

    @gl.public.view
    def get_article_count(self) -> u256:
        return self.article_counter

    @gl.public.view
    def get_articles_by_category(self, category: str) -> str:
        ids = []
        for i in range(len(self.category_index)):
            entry = self.category_index[i]
            parts = entry.split(":", 1)
            if len(parts) == 2 and parts[0].upper() == category.upper():
                ids.append(parts[1])
        if not ids:
            return f"No articles found for category: {category}"
        return f"Category {category.upper()}: {len(ids)} article(s): {', '.join(ids[-20:])}"

    @gl.public.view
    def get_latest(self, count: u256) -> str:
        total = int(self.article_counter)
        n = int(count)
        if total == 0:
            return "No articles published yet"
        start = max(0, total - n)
        results = []
        for i in range(start, total):
            aid = str(i)
            title = self._get(aid, "title")
            category = self._get(aid, "category")
            sentiment = self._get(aid, "sentiment")
            results.append(f"[{aid}] {category} | {sentiment} | {title}")
        return "\n".join(results)

    @gl.public.view
    def get_summary(self) -> str:
        total = int(self.article_counter)
        crypto = 0
        sports = 0
        politics = 0
        markets = 0
        tech = 0
        other = 0
        bullish = 0
        bearish = 0
        neutral = 0
        for i in range(total):
            aid = str(i)
            cat = self._get(aid, "category")
            sent = self._get(aid, "sentiment")
            if cat == "CRYPTO":
                crypto += 1
            elif cat == "SPORTS":
                sports += 1
            elif cat == "POLITICS":
                politics += 1
            elif cat == "MARKETS":
                markets += 1
            elif cat == "TECH":
                tech += 1
            else:
                other += 1
            if sent == "BULLISH" or sent == "POSITIVE":
                bullish += 1
            elif sent == "BEARISH" or sent == "NEGATIVE":
                bearish += 1
            else:
                neutral += 1
        return (
            f"Foresight Journals\n"
            f"Total Articles: {total}\n"
            f"CRYPTO: {crypto} | SPORTS: {sports} | POLITICS: {politics} | "
            f"MARKETS: {markets} | TECH: {tech} | OTHER: {other}\n"
            f"Bullish/Positive: {bullish} | Bearish/Negative: {bearish} | Neutral: {neutral}"
        )

    # ─── WRITE METHODS ──────────────────────────────────────────────────────────

    @gl.public.write
    def publish_article(
        self,
        category: str,
        source_url_1: str,
        source_url_2: str,
        source_url_3: str,
    ) -> str:
        valid_categories = ("CRYPTO", "SPORTS", "POLITICS", "MARKETS", "TECH", "OTHER")
        assert category.upper() in valid_categories, "Invalid category"
        assert len(source_url_1) >= 10, "Source URL 1 too short"

        self.block_counter = u256(int(self.block_counter) + 1)
        article_id = str(int(self.article_counter))
        category = category.upper()

        def leader_fn():
            sources = []
            source_list = []
            for url in (source_url_1, source_url_2, source_url_3):
                if len(url) >= 10:
                    try:
                        response = gl.nondet.web.get(url)
                        raw = response.body.decode("utf-8")
                        sources.append(f"Source ({url}):\n{raw[:2000]}")
                        source_list.append(url)
                    except Exception:
                        sources.append(f"Source ({url}): Could not fetch content.")

            sources_text = "\n\n".join(sources)

            if category in ("CRYPTO", "MARKETS"):
                sentiment_options = "BULLISH, BEARISH, or NEUTRAL"
                sentiment_note = "BULLISH means positive outlook, BEARISH means negative outlook, NEUTRAL means mixed or unclear."
            else:
                sentiment_options = "POSITIVE, NEGATIVE, or NEUTRAL"
                sentiment_note = "POSITIVE means favorable news, NEGATIVE means unfavorable news, NEUTRAL means mixed."

            prompt = f"""You are a professional financial and news journalist writing for Foresight Journals,
an AI-powered on-chain publication. Your writing is factual, concise, and insightful.

Category: {category}
Sources provided:
{sources_text}

Write a well-structured news article based on the sources above.
The article must cover the most significant and newsworthy information from the sources.

Rules:
- Title: punchy, under 80 characters
- Headline: one sentence expanding on the title, under 150 characters
- Body: three focused paragraphs. Each paragraph is 2-3 sentences. Total body under 600 characters.
- Tags: 3 to 5 relevant keywords separated by commas
- Sentiment: {sentiment_options}
  {sentiment_note}

Respond ONLY with this JSON:
{{
  "title": "Article title here",
  "headline": "One sentence headline expanding on the title",
  "body": "Paragraph one. Paragraph two. Paragraph three.",
  "tags": "tag1, tag2, tag3",
  "sentiment": "BULLISH"
}}

sentiment must be exactly one of: {sentiment_options.replace(', or ', ', ')}.
No extra text."""

            result = gl.nondet.exec_prompt(prompt)
            clean = result.strip().replace("```json", "").replace("```", "").strip()
            data = json.loads(clean)

            title = data.get("title", "Untitled")
            headline = data.get("headline", "")
            body = data.get("body", "")
            tags = data.get("tags", "")
            sentiment = data.get("sentiment", "NEUTRAL").upper()

            if category in ("CRYPTO", "MARKETS"):
                valid_sentiments = ("BULLISH", "BEARISH", "NEUTRAL")
            else:
                valid_sentiments = ("POSITIVE", "NEGATIVE", "NEUTRAL")

            if sentiment not in valid_sentiments:
                sentiment = "NEUTRAL"

            title = title[:80]
            headline = headline[:150]
            body = body[:600]

            return json.dumps({
                "title": title,
                "headline": headline,
                "body": body,
                "tags": tags,
                "sentiment": sentiment,
                "sources": ", ".join(source_list[:3])
            }, sort_keys=True)

        def validator_fn(leader_result) -> bool:
            if not isinstance(leader_result, gl.vm.Return):
                return False
            try:
                validator_raw = leader_fn()
                leader_data = json.loads(leader_result.calldata)
                validator_data = json.loads(validator_raw)
                if leader_data["sentiment"] != validator_data["sentiment"]:
                    return False
                return True
            except Exception:
                return False

        raw = gl.vm.run_nondet_unsafe(leader_fn, validator_fn)
        data = json.loads(raw)

        self._set(article_id, "title", data["title"])
        self._set(article_id, "headline", data["headline"])
        self._set(article_id, "body", data["body"])
        self._set(article_id, "tags", data["tags"])
        self._set(article_id, "sentiment", data["sentiment"])
        self._set(article_id, "sources", data["sources"])
        self._set(article_id, "category", category)
        self._set(article_id, "block", str(int(self.block_counter)))

        self.category_index.append(f"{category}:{article_id}")
        self.article_counter = u256(int(self.article_counter) + 1)

        return (
            f"Article {article_id} published. "
            f"Category: {category}. "
            f"Sentiment: {data['sentiment']}. "
            f"Title: {data['title']}"
        )

    # ─── PRIVATE HELPERS ────────────────────────────────────────────────────────

    def _get(self, article_id: str, field: str) -> str:
        key = f"{article_id}_{field}:"
        for i in range(len(self.article_data)):
            if self.article_data[i].startswith(key):
                return self.article_data[i][len(key):]
        return ""

    def _set(self, article_id: str, field: str, value: str) -> None:
        key = f"{article_id}_{field}:"
        for i in range(len(self.article_data)):
            if self.article_data[i].startswith(key):
                self.article_data[i] = f"{key}{value}"
                return
        self.article_data.append(f"{key}{value}")
