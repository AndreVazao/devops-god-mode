#!/usr/bin/env python3
from __future__ import annotations

import argparse
import asyncio
import hashlib
import json
import os
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List

PROVIDERS = {
    "chatgpt": {
        "url": "https://chat.openai.com/",
        "message_selectors": ["[data-message-author-role]", "article", "main [role='article']", "main div"],
        "ready_selectors": ["textarea", "[contenteditable='true']", "[data-message-author-role]"],
        "conversation_link_selectors": ["a[href*='/c/']", "a[href*='chat.openai.com']"],
    },
    "claude": {
        "url": "https://claude.ai/",
        "message_selectors": ["[data-testid*='message']", "article", "main div"],
        "ready_selectors": ["div[contenteditable='true']", "textarea", "[data-testid*='message']"],
        "conversation_link_selectors": ["a[href*='/chat/']", "a[href*='claude.ai']"],
    },
    "gemini": {
        "url": "https://gemini.google.com/",
        "message_selectors": ["message-content", "model-response", "user-query", "main *"],
        "ready_selectors": ["rich-textarea", "textarea", "[contenteditable='true']", "message-content"],
        "conversation_link_selectors": ["a[href*='/app/']", "a[href*='gemini.google.com']"],
    },
    "perplexity": {
        "url": "https://www.perplexity.ai/",
        "message_selectors": ["[data-testid*='message']", "article", "main div"],
        "ready_selectors": ["textarea", "[contenteditable='true']", "[data-testid*='message']"],
        "conversation_link_selectors": ["a[href*='/search/']", "a[href*='perplexity.ai']"],
    },
}

BLOCKED_TEXT_HINTS = ("password", "token", "cookie", "authorization", "bearer", "api_key", "secret")


def now() -> str:
    return datetime.now(timezone.utc).isoformat()


def sha_text(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8", errors="ignore")).hexdigest()[:16]


def safe_text(value: Any, limit: int = 4000) -> str:
    text = str(value or "").replace("\r", " ").strip()
    lowered = text.lower()
    if any(hint in lowered for hint in BLOCKED_TEXT_HINTS):
        return "[REDACTED_BY_PC_PROVIDER_CONVERSATION_PROBE]"
    return text[:limit]


async def first_visible_text(page: Any, selectors: List[str], limit: int = 30) -> List[Dict[str, Any]]:
    messages: List[Dict[str, Any]] = []
    seen = set()
    for selector in selectors:
        try:
            loc = page.locator(selector)
            count = min(await loc.count(), limit)
            for idx in range(count):
                item = loc.nth(idx)
                visible = await item.is_visible(timeout=700)
                if not visible:
                    continue
                text = safe_text(await item.inner_text(timeout=1200), limit=4000)
                if not text or text in seen:
                    continue
                seen.add(text)
                role = "unknown"
                try:
                    role_attr = await item.get_attribute("data-message-author-role", timeout=500)
                    if role_attr:
                        role = safe_text(role_attr, limit=60)
                except Exception:
                    pass
                messages.append({
                    "index": len(messages),
                    "role": role,
                    "text": text,
                    "text_hash": sha_text(text),
                    "source_selector": selector,
                    "visible": True,
                })
                if len(messages) >= limit:
                    return messages
        except Exception:
            continue
    return messages


async def collect_links(page: Any, selectors: List[str], limit: int = 40) -> List[Dict[str, Any]]:
    links: List[Dict[str, Any]] = []
    seen = set()
    for selector in selectors:
        try:
            loc = page.locator(selector)
            count = min(await loc.count(), limit)
            for idx in range(count):
                item = loc.nth(idx)
                href = safe_text(await item.get_attribute("href", timeout=700), limit=600)
                title = safe_text(await item.inner_text(timeout=700), limit=220)
                if not href or href in seen:
                    continue
                seen.add(href)
                links.append({"title": title or "untitled", "href": href, "source_selector": selector})
                if len(links) >= limit:
                    return links
        except Exception:
            continue
    return links


async def detect_ready(page: Any, selectors: List[str]) -> Dict[str, Any]:
    hits = []
    for selector in selectors:
        try:
            loc = page.locator(selector)
            count = await loc.count()
            if count:
                hits.append({"selector": selector, "count": min(count, 100)})
        except Exception:
            continue
    return {"ready": bool(hits), "hits": hits}


async def run_probe(args: argparse.Namespace) -> Dict[str, Any]:
    try:
        from playwright.async_api import async_playwright
    except Exception as exc:
        return {
            "ok": False,
            "status": "playwright_not_installed",
            "error": exc.__class__.__name__,
            "install_hint": "python -m pip install playwright && python -m playwright install chromium",
            "stores_credentials": False,
        }

    provider = PROVIDERS.get(args.provider)
    if provider is None:
        return {"ok": False, "status": "unknown_provider", "provider": args.provider, "supported": sorted(PROVIDERS)}

    profile_dir = Path(args.profile_dir or f"data/local_browser_profiles/{args.provider}").resolve()
    output_dir = Path(args.output_dir or "data/provider_proofs").resolve()
    output_dir.mkdir(parents=True, exist_ok=True)
    profile_dir.mkdir(parents=True, exist_ok=True)

    target_url = args.url or provider["url"]
    proof: Dict[str, Any] = {
        "ok": False,
        "created_at": now(),
        "provider": args.provider,
        "target_url": target_url,
        "profile_dir": str(profile_dir),
        "output_dir": str(output_dir),
        "manual_login_required": True,
        "stores_passwords": False,
        "exports_cookies": False,
        "exports_tokens": False,
        "status": "started",
    }

    async with async_playwright() as p:
        browser = await p.chromium.launch_persistent_context(
            user_data_dir=str(profile_dir),
            headless=bool(args.headless),
            viewport={"width": 1366, "height": 900},
            args=["--disable-blink-features=AutomationControlled"],
        )
        page = browser.pages[0] if browser.pages else await browser.new_page()
        try:
            await page.goto(target_url, wait_until="domcontentloaded", timeout=args.timeout_ms)
            await page.wait_for_timeout(2500)
            if args.wait_login_seconds > 0 and not args.headless:
                print(f"[God Mode] Browser aberto para {args.provider}. Faz login manual se necessário.")
                print(f"[God Mode] A aguardar {args.wait_login_seconds}s antes da leitura segura...")
                await page.wait_for_timeout(args.wait_login_seconds * 1000)
            ready = await detect_ready(page, provider["ready_selectors"])
            messages = await first_visible_text(page, provider["message_selectors"], limit=args.max_messages)
            links = await collect_links(page, provider["conversation_link_selectors"], limit=args.max_links)
            proof.update({
                "ok": True,
                "status": "proof_collected",
                "final_url": safe_text(page.url, limit=800),
                "title": safe_text(await page.title(), limit=220),
                "ready_detection": ready,
                "message_count": len(messages),
                "messages": messages,
                "conversation_link_count": len(links),
                "conversation_links": links,
                "summary": {
                    "can_open_provider": True,
                    "can_detect_ready_marker": ready["ready"],
                    "can_read_visible_messages": len(messages) > 0,
                    "can_list_candidate_conversation_links": len(links) > 0,
                    "needs_manual_operator_review": True,
                },
            })
        except Exception as exc:
            proof.update({"ok": False, "status": "probe_failed", "error": exc.__class__.__name__, "detail": safe_text(str(exc), limit=600)})
        finally:
            out_file = output_dir / f"{args.provider}_proof_{datetime.now(timezone.utc).strftime('%Y%m%d_%H%M%S')}.json"
            out_file.write_text(json.dumps(proof, ensure_ascii=False, indent=2), encoding="utf-8")
            proof["proof_file"] = str(out_file)
            await browser.close()
    return proof


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Local PC proof runner for external AI provider conversations.")
    parser.add_argument("--provider", default="chatgpt", choices=sorted(PROVIDERS))
    parser.add_argument("--url", default=None, help="Provider/conversation URL. Defaults to provider home.")
    parser.add_argument("--profile-dir", default=None, help="Local browser profile dir. Stored only on the PC.")
    parser.add_argument("--output-dir", default="data/provider_proofs")
    parser.add_argument("--headless", action="store_true", help="Use headless browser. Manual login usually needs visible mode.")
    parser.add_argument("--wait-login-seconds", type=int, default=45)
    parser.add_argument("--timeout-ms", type=int, default=45000)
    parser.add_argument("--max-messages", type=int, default=40)
    parser.add_argument("--max-links", type=int, default=40)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    result = asyncio.run(run_probe(args))
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result.get("ok") else 2


if __name__ == "__main__":
    raise SystemExit(main())
