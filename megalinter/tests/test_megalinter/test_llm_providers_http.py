#!/usr/bin/env python3
"""
HTTP request shape tests of the LLM Advisor providers (no network)
"""

import json
import os
import tempfile
import unittest
from typing import Any, Dict, Optional
from unittest.mock import MagicMock, patch

import requests
from megalinter.llm_provider.llm_provider import LLMProvider, LLMProviderError
from megalinter.llm_provider.llm_provider_factory import LLMProviderFactory

API_KEY = "sk-secret-test-key-123456"
SYSTEM_PROMPT = "You are a linter expert"
USER_PROMPT = "Explain F401"


def make_response(
    status_code: int = 200,
    json_body: Any = None,
    text: Optional[str] = None,
    headers: Optional[Dict[str, str]] = None,
    lines: Optional[list] = None,
) -> MagicMock:
    response = MagicMock(spec=requests.Response)
    response.status_code = status_code
    response.reason = "OK" if status_code < 400 else "Error"
    response.headers = headers or {}
    if text is None:
        text = json.dumps(json_body) if json_body is not None else ""
    response.text = text
    if json_body is not None:
        response.json.return_value = json_body
    else:
        response.json.side_effect = ValueError("not json")
    response.iter_lines.return_value = iter(lines or [])
    return response


def openai_body(content: Any = "Remove the unused import") -> Dict[str, Any]:
    return {"choices": [{"message": {"role": "assistant", "content": content}}]}


class LLMProviderHttpTestBase(unittest.TestCase):
    def setUp(self):
        self.env: Dict[str, str] = {}
        self.config_patch = patch(
            "megalinter.config.get",
            side_effect=lambda request_id, key, default=None: self.env.get(
                key, default
            ),
        )
        self.config_patch.start()
        self.sleep_patch = patch("megalinter.llm_provider.llm_provider.time.sleep")
        self.mock_sleep = self.sleep_patch.start()

    def tearDown(self):
        self.sleep_patch.stop()
        self.config_patch.stop()

    def create(self, provider_name: str, env: Dict[str, str]) -> LLMProvider:
        self.env.update(env)
        provider = LLMProviderFactory.create_provider(provider_name, "test-request")
        self.assertIsNotNone(provider, f"{provider_name} provider not created")
        assert provider is not None
        self.assertTrue(provider.is_available())
        return provider

    def invoke(self, provider: LLMProvider, *responses: MagicMock):
        with patch.object(
            requests.Session, "post", side_effect=list(responses)
        ) as mock_post:
            result = provider.invoke(USER_PROMPT, SYSTEM_PROMPT)
        return result, mock_post

    def call_kwargs(self, mock_post, index: int = 0) -> Dict[str, Any]:
        args, kwargs = mock_post.call_args_list[index]
        kwargs = dict(kwargs)
        kwargs["url"] = args[0]
        return kwargs


class TestOpenAICompatibleProviders(LLMProviderHttpTestBase):
    # provider, api key var, base url var, default base url, max tokens field,
    # developer role for o-series, extra payload
    CASES = [
        (
            "openai",
            "OPENAI_API_KEY",
            "OPENAI_BASE_URL",
            "https://api.openai.com/v1",
            "max_completion_tokens",
            True,
            {},
        ),
        (
            "grok",
            "GROK_API_KEY",
            "GROK_BASE_URL",
            "https://api.x.ai/v1",
            "max_completion_tokens",
            True,
            {},
        ),
        (
            "orcarouter",
            "ORCAROUTER_API_KEY",
            "ORCAROUTER_BASE_URL",
            "https://api.orcarouter.ai/v1",
            "max_completion_tokens",
            True,
            {},
        ),
        (
            "deepseek",
            "DEEPSEEK_API_KEY",
            "DEEPSEEK_BASE_URL",
            "https://api.deepseek.com/v1",
            "max_tokens",
            False,
            {},
        ),
        (
            "mistral",
            "MISTRAL_API_KEY",
            "MISTRAL_BASE_URL",
            "https://api.mistral.ai/v1",
            "max_tokens",
            False,
            {"top_p": 1},
        ),
    ]

    def test_request_shape_with_defaults(self):
        for name, key_var, _, base_url, max_field, _, extra in self.CASES:
            with self.subTest(provider=name):
                self.env.clear()
                provider = self.create(name, {key_var: API_KEY})
                result, mock_post = self.invoke(
                    provider, make_response(json_body=openai_body())
                )
                self.assertEqual(result, "Remove the unused import")
                call = self.call_kwargs(mock_post)
                self.assertEqual(call["url"], f"{base_url}/chat/completions")
                self.assertEqual(call["headers"]["Authorization"], f"Bearer {API_KEY}")
                self.assertEqual(call["headers"]["Content-Type"], "application/json")
                self.assertEqual(call["timeout"], (30.0, 600.0))
                self.assertIs(call["verify"], True)
                expected = {
                    "model": provider.get_default_model(),
                    "messages": [
                        {"role": "system", "content": SYSTEM_PROMPT},
                        {"role": "user", "content": USER_PROMPT},
                    ],
                    "stream": False,
                    "temperature": 0.1,
                    max_field: 1000,
                    **extra,
                }
                self.assertEqual(call["json"], expected)

    def test_base_url_override_and_config(self):
        for name, key_var, url_var, _, max_field, _, _ in self.CASES:
            with self.subTest(provider=name):
                self.env.clear()
                provider = self.create(
                    name,
                    {
                        key_var: API_KEY,
                        url_var: "https://proxy.example.com/v2/",
                        "LLM_MODEL_NAME": "custom-model",
                        "LLM_TEMPERATURE": "0.7",
                        "LLM_MAX_TOKENS": "321",
                    },
                )
                _, mock_post = self.invoke(
                    provider, make_response(json_body=openai_body())
                )
                call = self.call_kwargs(mock_post)
                self.assertEqual(
                    call["url"], "https://proxy.example.com/v2/chat/completions"
                )
                self.assertEqual(call["json"]["model"], "custom-model")
                self.assertEqual(call["json"]["temperature"], 0.7)
                self.assertEqual(call["json"][max_field], 321)

    def test_developer_role_for_o_series(self):
        for name, key_var, _, _, _, developer_role, _ in self.CASES:
            with self.subTest(provider=name):
                self.env.clear()
                provider = self.create(
                    name, {key_var: API_KEY, "LLM_MODEL_NAME": "o3-mini"}
                )
                _, mock_post = self.invoke(
                    provider, make_response(json_body=openai_body())
                )
                messages = self.call_kwargs(mock_post)["json"]["messages"]
                self.assertEqual(
                    messages[0]["role"], "developer" if developer_role else "system"
                )

    def test_gpt5_temperature_omitted(self):
        provider = self.create(
            "openai", {"OPENAI_API_KEY": API_KEY, "LLM_MODEL_NAME": "gpt-5-mini"}
        )
        _, mock_post = self.invoke(provider, make_response(json_body=openai_body()))
        self.assertNotIn("temperature", self.call_kwargs(mock_post)["json"])
        self.env["LLM_MODEL_NAME"] = "gpt-5-chat-latest"
        provider = self.create("openai", {})
        _, mock_post = self.invoke(provider, make_response(json_body=openai_body()))
        self.assertEqual(self.call_kwargs(mock_post)["json"]["temperature"], 0.1)

    def test_openai_legacy_env_and_org_headers(self):
        provider = self.create(
            "openai",
            {
                "OPENAI_API_KEY": API_KEY,
                "OPENAI_API_BASE": "https://legacy.example.com/v1",
                "OPENAI_ORG_ID": "org-123",
                "OPENAI_PROJECT_ID": "proj-456",
            },
        )
        _, mock_post = self.invoke(provider, make_response(json_body=openai_body()))
        call = self.call_kwargs(mock_post)
        self.assertEqual(call["url"], "https://legacy.example.com/v1/chat/completions")
        self.assertEqual(call["headers"]["OpenAI-Organization"], "org-123")
        self.assertEqual(call["headers"]["OpenAI-Project"], "proj-456")

    def test_no_system_prompt(self):
        provider = self.create("openai", {"OPENAI_API_KEY": API_KEY})
        with patch.object(
            requests.Session,
            "post",
            return_value=make_response(json_body=openai_body()),
        ) as mock_post:
            provider.invoke(USER_PROMPT)
        self.assertEqual(
            self.call_kwargs(mock_post)["json"]["messages"],
            [{"role": "user", "content": USER_PROMPT}],
        )

    def test_mistral_content_chunks(self):
        provider = self.create("mistral", {"MISTRAL_API_KEY": API_KEY})
        content = [
            {"type": "thinking", "thinking": [{"type": "text", "text": "hmm"}]},
            {"type": "text", "text": "Answer"},
        ]
        result, _ = self.invoke(provider, make_response(json_body=openai_body(content)))
        self.assertEqual(result, "Answer")

    def test_missing_api_key(self):
        for name, _, _, _, _, _, _ in self.CASES:
            with self.subTest(provider=name):
                self.env.clear()
                self.assertIsNone(
                    LLMProviderFactory.create_provider(name, "test-request")
                )


class TestAnthropicProvider(LLMProviderHttpTestBase):
    BODY = {
        "content": [
            {"type": "text", "text": "Remove "},
            {"type": "text", "text": "the import"},
        ]
    }

    def test_request_shape(self):
        provider = self.create("anthropic", {"ANTHROPIC_API_KEY": API_KEY})
        result, mock_post = self.invoke(provider, make_response(json_body=self.BODY))
        self.assertEqual(result, "Remove the import")
        call = self.call_kwargs(mock_post)
        self.assertEqual(call["url"], "https://api.anthropic.com/v1/messages")
        self.assertEqual(call["headers"]["x-api-key"], API_KEY)
        self.assertEqual(call["headers"]["anthropic-version"], "2023-06-01")
        self.assertNotIn("Authorization", call["headers"])
        self.assertEqual(call["timeout"], (30.0, 600.0))
        self.assertEqual(
            call["json"],
            {
                "model": "claude-sonnet-5-5",
                "max_tokens": 1000,
                "messages": [{"role": "user", "content": USER_PROMPT}],
                "system": SYSTEM_PROMPT,
            },
        )

    def test_base_url_override(self):
        provider = self.create(
            "anthropic",
            {
                "ANTHROPIC_API_KEY": API_KEY,
                "ANTHROPIC_BASE_URL": "https://gw.example.com/",
                "ANTHROPIC_API_VERSION": "2024-01-01",
            },
        )
        _, mock_post = self.invoke(provider, make_response(json_body=self.BODY))
        self.assertEqual(
            self.call_kwargs(mock_post)["url"], "https://gw.example.com/v1/messages"
        )
        self.assertEqual(
            self.call_kwargs(mock_post)["headers"]["anthropic-version"], "2024-01-01"
        )

    def test_temperature_omitted_for_fixed_temperature_models(self):
        provider = self.create(
            "anthropic",
            {"ANTHROPIC_API_KEY": API_KEY, "LLM_MODEL_NAME": "claude-fable-5"},
        )
        _, mock_post = self.invoke(provider, make_response(json_body=self.BODY))
        self.assertNotIn("temperature", self.call_kwargs(mock_post)["json"])


class TestGoogleProvider(LLMProviderHttpTestBase):
    BODY = {
        "candidates": [
            {
                "content": {
                    "parts": [
                        {"text": "thinking...", "thought": True},
                        {"text": "Remove the import"},
                    ]
                },
                "finishReason": "STOP",
            }
        ]
    }

    def test_request_shape(self):
        provider = self.create("google", {"GOOGLE_API_KEY": API_KEY})
        result, mock_post = self.invoke(provider, make_response(json_body=self.BODY))
        self.assertEqual(result, "Remove the import")
        call = self.call_kwargs(mock_post)
        self.assertEqual(
            call["url"],
            "https://generativelanguage.googleapis.com/v1beta/models/"
            "gemini-2.5-flash:generateContent",
        )
        self.assertEqual(call["headers"]["x-goog-api-key"], API_KEY)
        self.assertNotIn(API_KEY, call["url"])
        self.assertEqual(
            call["json"],
            {
                "contents": [{"role": "user", "parts": [{"text": USER_PROMPT}]}],
                "systemInstruction": {"parts": [{"text": SYSTEM_PROMPT}]},
                "generationConfig": {
                    "candidateCount": 1,
                    "temperature": 0.1,
                    "maxOutputTokens": 1000,
                },
            },
        )

    def test_blocked_prompt(self):
        provider = self.create("google", {"GOOGLE_API_KEY": API_KEY})
        body = {"promptFeedback": {"blockReason": "SAFETY"}}
        with self.assertRaisesRegex(LLMProviderError, "SAFETY"):
            self.invoke(provider, make_response(json_body=body))

    def test_no_text(self):
        provider = self.create("google", {"GOOGLE_API_KEY": API_KEY})
        body = {
            "candidates": [{"content": {"parts": []}, "finishReason": "MAX_TOKENS"}]
        }
        with self.assertRaisesRegex(LLMProviderError, "MAX_TOKENS"):
            self.invoke(provider, make_response(json_body=body))


class TestOllamaProvider(LLMProviderHttpTestBase):
    LINES = [
        json.dumps({"response": "Remove ", "done": False}),
        "",
        json.dumps({"response": "the import", "done": True}),
    ]

    def test_request_shape(self):
        provider = self.create("ollama", {})
        result, mock_post = self.invoke(provider, make_response(lines=self.LINES))
        self.assertEqual(result, "Remove the import")
        call = self.call_kwargs(mock_post)
        self.assertEqual(call["url"], "http://localhost:11434/api/generate")
        self.assertTrue(call["stream"])
        self.assertNotIn("Authorization", call["headers"])
        self.assertEqual(
            call["json"],
            {
                "model": "llama3.2",
                "prompt": f"System: {SYSTEM_PROMPT}\n\nUser: {USER_PROMPT}",
                "options": {"temperature": 0.1},
            },
        )

    def test_base_url_override(self):
        provider = self.create("ollama", {"OLLAMA_BASE_URL": "http://ollama:11434/"})
        _, mock_post = self.invoke(provider, make_response(lines=self.LINES))
        self.assertEqual(
            self.call_kwargs(mock_post)["url"], "http://ollama:11434/api/generate"
        )

    def test_model_not_found_hint(self):
        provider = self.create("ollama", {})
        with self.assertRaisesRegex(LLMProviderError, "ollama pull llama3.2"):
            self.invoke(
                provider, make_response(404, text='{"error":"model not found"}')
            )

    def test_stream_error(self):
        provider = self.create("ollama", {})
        lines = [json.dumps({"error": "out of memory"})]
        with self.assertRaisesRegex(LLMProviderError, "out of memory"):
            self.invoke(provider, make_response(lines=lines))


class TestHuggingFaceProvider(LLMProviderHttpTestBase):
    def test_pipeline_invocation(self):
        hf_pipeline = MagicMock(return_value=[[{"generated_text": "Generated"}]])
        hf_pipeline.task = "text-generation"
        fake_transformers = MagicMock()
        fake_transformers.pipeline.return_value = hf_pipeline
        with patch.dict("sys.modules", {"transformers": fake_transformers}):
            provider = self.create(
                "huggingface",
                {"HUGGINGFACE_API_TOKEN": API_KEY, "LLM_MODEL_NAME": "gpt2"},
            )
        fake_transformers.pipeline.assert_called_once_with(
            task="text-generation", model="gpt2", device=-1, token=API_KEY
        )
        self.assertEqual(provider.invoke(USER_PROMPT, SYSTEM_PROMPT), "Generated")
        hf_pipeline.assert_called_once_with(
            [f"System: {SYSTEM_PROMPT}\n\nUser: {USER_PROMPT}"]
        )

    def test_missing_dependencies(self):
        with (
            patch.dict("sys.modules", {"transformers": None}),
            self.assertLogs(level="ERROR") as logs,
        ):
            provider = LLMProviderFactory.create_provider("huggingface", "test-request")
        self.assertIsNone(provider)
        self.assertIn("pip install transformers torch", "\n".join(logs.output))


class TestHttpHelper(LLMProviderHttpTestBase):
    def setUp(self):
        super().setUp()
        self.provider = self.create("openai", {"OPENAI_API_KEY": API_KEY})

    def test_retry_on_429_then_success(self):
        result, mock_post = self.invoke(
            self.provider,
            make_response(429, text="rate limited", headers={"Retry-After": "2"}),
            make_response(json_body=openai_body("ok")),
        )
        self.assertEqual(result, "ok")
        self.assertEqual(mock_post.call_count, 2)
        self.mock_sleep.assert_called_once_with(2.0)

    def test_retry_after_is_capped(self):
        _, mock_post = self.invoke(
            self.provider,
            make_response(429, headers={"Retry-After": "3600"}),
            make_response(json_body=openai_body("ok")),
        )
        self.mock_sleep.assert_called_once_with(LLMProvider.RETRY_AFTER_MAX_SECONDS)

    def test_retry_on_5xx_with_backoff(self):
        result, mock_post = self.invoke(
            self.provider,
            make_response(500, text="boom"),
            make_response(503, text="unavailable"),
            make_response(json_body=openai_body("ok")),
        )
        self.assertEqual(result, "ok")
        self.assertEqual(mock_post.call_count, 3)
        self.assertEqual(
            [c.args[0] for c in self.mock_sleep.call_args_list], [0.5, 1.0]
        )

    def test_retry_on_connection_error(self):
        result, mock_post = self.invoke(
            self.provider,
            requests.exceptions.ConnectionError("connection refused"),
            make_response(json_body=openai_body("ok")),
        )
        self.assertEqual(result, "ok")
        self.assertEqual(mock_post.call_count, 2)

    def test_gives_up_after_retry_attempts(self):
        with self.assertRaisesRegex(LLMProviderError, "HTTP 502"):
            self.invoke(self.provider, *[make_response(502, text="bad gateway")] * 3)
        self.assertEqual(self.mock_sleep.call_count, 2)

    def test_no_retry_on_4xx(self):
        with patch.object(
            requests.Session,
            "post",
            return_value=make_response(400, text="bad request"),
        ) as mock_post:
            with self.assertRaisesRegex(LLMProviderError, "HTTP 400"):
                self.provider.invoke(USER_PROMPT, SYSTEM_PROMPT)
        self.assertEqual(mock_post.call_count, 1)
        self.mock_sleep.assert_not_called()

    def test_no_retry_on_read_timeout(self):
        with patch.object(
            requests.Session,
            "post",
            side_effect=requests.exceptions.ReadTimeout("slow"),
        ) as mock_post:
            with self.assertRaisesRegex(LLMProviderError, "timed out"):
                self.provider.invoke(USER_PROMPT, SYSTEM_PROMPT)
        self.assertEqual(mock_post.call_count, 1)

    def test_error_message_is_truncated_and_redacted(self):
        body = f"Incorrect API key provided: {API_KEY}. " + "x" * 5000
        with (
            self.assertRaises(LLMProviderError) as context,
            self.assertLogs(level="ERROR") as logs,
        ):
            self.invoke(self.provider, make_response(401, text=body))
        message = str(context.exception)
        self.assertIn("HTTP 401", message)
        self.assertNotIn(API_KEY, message)
        self.assertNotIn(API_KEY, "\n".join(logs.output))
        self.assertLess(len(message), 700)
        self.assertIn("(truncated)", message)

    def test_non_json_response(self):
        with self.assertRaisesRegex(LLMProviderError, "non-JSON"):
            self.invoke(self.provider, make_response(200, text="<html>proxy</html>"))

    def test_error_field_in_body(self):
        with self.assertRaisesRegex(LLMProviderError, "quota"):
            self.invoke(
                self.provider, make_response(json_body={"error": {"message": "quota"}})
            )

    def test_ssl_cert_file_fallback(self):
        with tempfile.NamedTemporaryFile(suffix=".pem", delete=False) as cert_file:
            cert_path = cert_file.name
        try:
            self.env["SSL_CERT_FILE"] = cert_path
            self.assertEqual(self.provider.get_ssl_verify(), cert_path)
            _, mock_post = self.invoke(
                self.provider, make_response(json_body=openai_body())
            )
            self.assertEqual(self.call_kwargs(mock_post)["verify"], cert_path)
            # REQUESTS_CA_BUNDLE wins over SSL_CERT_FILE
            self.env["REQUESTS_CA_BUNDLE"] = "/etc/ssl/requests-bundle.pem"
            self.assertEqual(
                self.provider.get_ssl_verify(), "/etc/ssl/requests-bundle.pem"
            )
        finally:
            os.remove(cert_path)

    def test_ssl_cert_file_missing_is_ignored(self):
        self.env["SSL_CERT_FILE"] = "/does/not/exist.pem"
        self.assertIs(self.provider.get_ssl_verify(), True)


class TestBaseUrlOverrides(LLMProviderHttpTestBase):
    ANTHROPIC_BODY = {"content": [{"type": "text", "text": "ok"}]}
    GOOGLE_BODY = {"candidates": [{"content": {"parts": [{"text": "ok"}]}}]}
    OLLAMA_LINES = [json.dumps({"response": "ok", "done": True})]

    def assert_url(self, provider_name, env, body_kwargs, expected_url):
        self.env.clear()
        provider = self.create(provider_name, env)
        _, mock_post = self.invoke(provider, make_response(**body_kwargs))
        self.assertEqual(self.call_kwargs(mock_post)["url"], expected_url)

    def test_openai_compatible_overrides(self):
        cases = [
            ("openai", "OPENAI_API_KEY", "OPENAI_BASE_URL"),
            ("grok", "GROK_API_KEY", "GROK_BASE_URL"),
            ("orcarouter", "ORCAROUTER_API_KEY", "ORCAROUTER_BASE_URL"),
            ("deepseek", "DEEPSEEK_API_KEY", "DEEPSEEK_BASE_URL"),
            ("mistral", "MISTRAL_API_KEY", "MISTRAL_BASE_URL"),
        ]
        for name, key_var, url_var in cases:
            for base_url in [
                "https://llm.example.com/v1",
                "https://llm.example.com/v1/",
                "https://llm.example.com/v1/chat/completions",
            ]:
                with self.subTest(provider=name, base_url=base_url):
                    self.assert_url(
                        name,
                        {key_var: API_KEY, url_var: base_url},
                        {"json_body": openai_body()},
                        "https://llm.example.com/v1/chat/completions",
                    )

    def test_vendor_host_without_version_segment(self):
        cases = [
            (
                "mistral",
                "MISTRAL_API_KEY",
                "MISTRAL_BASE_URL",
                "https://api.mistral.ai/v1",
            ),
            (
                "openai",
                "OPENAI_API_KEY",
                "OPENAI_BASE_URL",
                "https://api.openai.com/v1",
            ),
            ("grok", "GROK_API_KEY", "GROK_BASE_URL", "https://api.x.ai/v1"),
        ]
        for name, key_var, url_var, default_url in cases:
            with self.subTest(provider=name):
                host = default_url[: -len("/v1")]
                self.assert_url(
                    name,
                    {key_var: API_KEY, url_var: host + "/"},
                    {"json_body": openai_body()},
                    f"{default_url}/chat/completions",
                )
        # Other hosts are used as-is, as the OpenAI SDKs did
        self.assert_url(
            "openai",
            {"OPENAI_API_KEY": API_KEY, "OPENAI_BASE_URL": "https://proxy.example.com"},
            {"json_body": openai_body()},
            "https://proxy.example.com/chat/completions",
        )

    def test_anthropic_overrides(self):
        for base_url in [
            "https://gw.example.com",
            "https://gw.example.com/",
            "https://gw.example.com/v1",
            "https://gw.example.com/v1/messages",
        ]:
            for var_name in ["ANTHROPIC_BASE_URL", "ANTHROPIC_API_URL"]:
                with self.subTest(base_url=base_url, var_name=var_name):
                    self.assert_url(
                        "anthropic",
                        {"ANTHROPIC_API_KEY": API_KEY, var_name: base_url},
                        {"json_body": self.ANTHROPIC_BODY},
                        "https://gw.example.com/v1/messages",
                    )

    def test_google_overrides(self):
        cases = [
            (
                "https://gemini.example.com",
                "https://gemini.example.com/v1beta/models/gemini-2.5-flash:generateContent",
            ),
            (
                "https://gemini.example.com/",
                "https://gemini.example.com/v1beta/models/gemini-2.5-flash:generateContent",
            ),
            (
                "https://gemini.example.com/v1beta/",
                "https://gemini.example.com/v1beta/models/gemini-2.5-flash:generateContent",
            ),
            (
                "https://gemini.example.com/v1",
                "https://gemini.example.com/v1/models/gemini-2.5-flash:generateContent",
            ),
        ]
        for base_url, expected_url in cases:
            with self.subTest(base_url=base_url):
                self.assert_url(
                    "google",
                    {"GOOGLE_API_KEY": API_KEY, "GOOGLE_BASE_URL": base_url},
                    {"json_body": self.GOOGLE_BODY},
                    expected_url,
                )

    def test_ollama_overrides(self):
        for base_url in [
            "http://ollama:11434",
            "http://ollama:11434/",
            "http://ollama:11434/api",
            "http://ollama:11434/api/generate",
        ]:
            with self.subTest(base_url=base_url):
                self.assert_url(
                    "ollama",
                    {"OLLAMA_BASE_URL": base_url},
                    {"lines": self.OLLAMA_LINES},
                    "http://ollama:11434/api/generate",
                )

    def test_ollama_cloud_api_key(self):
        provider = self.create(
            "ollama",
            {"OLLAMA_BASE_URL": "https://ollama.com", "OLLAMA_API_KEY": API_KEY},
        )
        _, mock_post = self.invoke(provider, make_response(lines=self.OLLAMA_LINES))
        call = self.call_kwargs(mock_post)
        self.assertEqual(call["url"], "https://ollama.com/api/generate")
        self.assertEqual(call["headers"]["Authorization"], f"Bearer {API_KEY}")


class TestAnthropicTemperature(LLMProviderHttpTestBase):
    def test_temperature_by_model(self):
        cases = {
            "claude-3-7-sonnet-latest": True,
            "claude-sonnet-4-5-20250929": True,
            "claude-opus-4-6": True,
            "claude-opus-4-20250514": True,
            "claude-opus-4-7": False,
            "claude-opus-4-8": False,
            "claude-sonnet-5": False,
            "claude-sonnet-5-5": False,
            "claude-haiku-5-5": False,
            "claude-fable-5-2": False,
            "claude-mythos-preview": False,
        }
        for model_name, expected in cases.items():
            with self.subTest(model=model_name):
                self.env.clear()
                provider = self.create(
                    "anthropic",
                    {"ANTHROPIC_API_KEY": API_KEY, "LLM_MODEL_NAME": model_name},
                )
                payload = provider.build_payload(USER_PROMPT, SYSTEM_PROMPT)
                self.assertEqual("temperature" in payload, expected)

    def test_no_temperature_with_recent_api_version(self):
        provider = self.create(
            "anthropic",
            {
                "ANTHROPIC_API_KEY": API_KEY,
                "ANTHROPIC_API_VERSION": "2026-10-21",
                "LLM_MODEL_NAME": "claude-sonnet-4-6",
            },
        )
        self.assertNotIn("temperature", provider.build_payload(USER_PROMPT))


class TestFactory(unittest.TestCase):
    def test_supported_providers_unchanged(self):
        self.assertEqual(
            list(LLMProviderFactory.get_supported_providers().keys()),
            [
                "openai",
                "anthropic",
                "google",
                "ollama",
                "huggingface",
                "mistral",
                "deepseek",
                "grok",
                "orcarouter",
            ],
        )
        self.assertEqual(
            len(LLMProviderFactory.get_supported_providers_api_key_var_names()), 9
        )


if __name__ == "__main__":
    unittest.main()
