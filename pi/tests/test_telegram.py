"""Tests for two-way Telegram control (docs/UPGRADES.md §9).

Everything runs against a fake in-memory transport - zero network. Update
handling is exercised directly via _handle_update/_poll_once, so no real
threads or long sleeps are needed.
"""
from __future__ import annotations

import alerts.telegram_bot as telegram_bot
from alerts.telegram_bot import TelegramCommander, _multipart_encode, send_alert

AUTH_CHAT = 111
INTRUDER_CHAT = 999


class FakeApi:
    """Records every call; serves queued getUpdates batches."""

    def __init__(self, updates=None):
        self.calls = []
        self.update_batches = list(updates or [])

    def __call__(self, method, params=None, files=None):
        self.calls.append((method, params, files))
        if method == "getUpdates":
            batch = self.update_batches.pop(0) if self.update_batches else []
            return {"ok": True, "result": batch}
        return {"ok": True, "result": {}}

    def sent(self, method="sendMessage"):
        return [c for c in self.calls if c[0] == method]

    def texts_to(self, chat_id):
        return [p["text"] for m, p, _ in self.calls
                if m == "sendMessage" and p["chat_id"] == chat_id]


def make_update(update_id, chat_id, text):
    return {"update_id": update_id,
            "message": {"message_id": update_id,
                        "chat": {"id": chat_id, "type": "private"},
                        "text": text}}


def make_commander(api, callbacks=None, allowed=(AUTH_CHAT,), **kwargs):
    return TelegramCommander(callbacks=callbacks or {}, allowed_chat_ids=allowed,
                             token="123:TESTTOKEN", api=api, **kwargs)


class TestAuth:
    def test_authorized_chat_dispatches_stop(self):
        api = FakeApi()
        calls = []
        cmd = make_commander(api, {"stop": lambda: calls.append("stop")})
        cmd._handle_update(make_update(1, AUTH_CHAT, "/stop"), now=1000.0)
        assert calls == ["stop"]
        assert "STOP" in api.texts_to(AUTH_CHAT)[0]

    def test_unauthorized_chat_not_dispatched_one_reply(self):
        api = FakeApi()
        calls = []
        cmd = make_commander(api, {"stop": lambda: calls.append("stop")})
        cmd._handle_update(make_update(1, INTRUDER_CHAT, "/stop"), now=1000.0)
        cmd._handle_update(make_update(2, INTRUDER_CHAT, "/stop"), now=1010.0)
        cmd._handle_update(make_update(3, INTRUDER_CHAT, "/photo"), now=1020.0)
        assert calls == []                       # never dispatched
        assert api.sent("sendPhoto") == []
        replies = api.texts_to(INTRUDER_CHAT)
        assert len(replies) == 1                 # at most one unauthorized reply
        assert "unauthorized" in replies[0].lower()

    def test_unauthorized_reply_allowed_again_after_an_hour(self):
        api = FakeApi()
        cmd = make_commander(api, {})
        cmd._handle_update(make_update(1, INTRUDER_CHAT, "/stop"), now=1000.0)
        cmd._handle_update(make_update(2, INTRUDER_CHAT, "/stop"), now=1000.0 + 3601)
        assert len(api.texts_to(INTRUDER_CHAT)) == 2

    def test_empty_allowlist_fails_closed(self):
        api = FakeApi()
        calls = []
        cmd = make_commander(api, {"stop": lambda: calls.append("stop")},
                             allowed=())
        cmd._handle_update(make_update(1, AUTH_CHAT, "/stop"), now=1000.0)
        assert calls == []
        assert api.calls == []                   # not even an unauthorized reply
        assert cmd.start() is False              # inbound disabled entirely
        assert cmd._thread is None

    def test_no_token_does_not_start(self):
        cmd = TelegramCommander(callbacks={}, allowed_chat_ids=(AUTH_CHAT,),
                                token="", api=FakeApi())
        assert cmd.start() is False

    def test_allowlist_parsed_from_env(self, monkeypatch):
        monkeypatch.setenv("TELEGRAM_ALLOWED_CHAT_IDS", " 111 , 222 ")
        cmd = TelegramCommander(callbacks={}, token="123:T", api=FakeApi())
        assert cmd.allowed_chat_ids == frozenset({"111", "222"})


class TestCommands:
    def test_status_reply_sent_back(self):
        api = FakeApi()
        cmd = make_commander(api, {"status": lambda: "Battery 72%, spraying"})
        cmd._handle_update(make_update(1, AUTH_CHAT, "/status"), now=1000.0)
        assert api.texts_to(AUTH_CHAT) == ["Battery 72%, spraying"]

    def test_summary_reply_sent_back(self):
        api = FakeApi()
        cmd = make_commander(api, {"summary": lambda: "Saved 3.2 L herbicide"})
        cmd._handle_update(make_update(1, AUTH_CHAT, "/summary"), now=1000.0)
        assert api.texts_to(AUTH_CHAT) == ["Saved 3.2 L herbicide"]

    def test_go_and_resume_are_aliases(self):
        api = FakeApi()
        calls = []
        cmd = make_commander(api, {"resume": lambda: calls.append("resume")})
        cmd._handle_update(make_update(1, AUTH_CHAT, "/go"), now=1000.0)
        cmd._handle_update(make_update(2, AUTH_CHAT, "/resume"), now=1001.0)
        assert calls == ["resume", "resume"]

    def test_unknown_command_gets_help_hint(self):
        api = FakeApi()
        cmd = make_commander(api, {"stop": lambda: None})
        cmd._handle_update(make_update(1, AUTH_CHAT, "/fly"), now=1000.0)
        assert "/help" in api.texts_to(AUTH_CHAT)[0]

    def test_missing_callback_polite_reply(self):
        api = FakeApi()
        cmd = make_commander(api, {})            # no callbacks registered
        cmd._handle_update(make_update(1, AUTH_CHAT, "/photo"), now=1000.0)
        assert "not available" in api.texts_to(AUTH_CHAT)[0]

    def test_help_lists_commands(self):
        api = FakeApi()
        cmd = make_commander(api, {"stop": lambda: None})
        cmd._handle_update(make_update(1, AUTH_CHAT, "/help"), now=1000.0)
        text = api.texts_to(AUTH_CHAT)[0]
        for command in ("/stop", "/status", "/photo", "/summary", "/help"):
            assert command in text

    def test_command_with_botname_suffix(self):
        api = FakeApi()
        calls = []
        cmd = make_commander(api, {"stop": lambda: calls.append("stop")})
        cmd._handle_update(make_update(1, AUTH_CHAT, "/STOP@AgriRoverBot now"),
                           now=1000.0)
        assert calls == ["stop"]

    def test_callback_exception_replies_error_and_continues(self):
        api = FakeApi()

        def boom():
            raise RuntimeError("camera offline")

        seen = []
        cmd = make_commander(api, {"photo": boom,
                                   "status": lambda: seen.append(1) or "ok"})
        cmd._handle_update(make_update(1, AUTH_CHAT, "/photo"), now=1000.0)
        assert "camera offline" in api.texts_to(AUTH_CHAT)[0]
        # ...and the very next update is still handled normally.
        cmd._handle_update(make_update(2, AUTH_CHAT, "/status"), now=1001.0)
        assert seen == [1]
        assert api.texts_to(AUTH_CHAT)[-1] == "ok"

    def test_photo_bytes_sent_as_multipart(self):
        api = FakeApi()
        jpeg = b"\xff\xd8\xe0fakejpeg"
        cmd = make_commander(api, {"photo": lambda: jpeg})
        cmd._handle_update(make_update(1, AUTH_CHAT, "/photo"), now=1000.0)
        (method, params, files), = api.sent("sendPhoto")
        assert params["chat_id"] == AUTH_CHAT
        filename, data, ctype = files["photo"]
        assert data == jpeg and ctype == "image/jpeg"

    def test_photo_path_read_from_disk(self, tmp_path):
        api = FakeApi()
        path = tmp_path / "snap.jpg"
        path.write_bytes(b"jpegdata")
        cmd = make_commander(api, {"photo": lambda: str(path)})
        cmd._handle_update(make_update(1, AUTH_CHAT, "/photo"), now=1000.0)
        (_, _, files), = api.sent("sendPhoto")
        assert files["photo"][1] == b"jpegdata"

    def test_photo_none_polite_reply(self):
        api = FakeApi()
        cmd = make_commander(api, {"photo": lambda: None})
        cmd._handle_update(make_update(1, AUTH_CHAT, "/photo"), now=1000.0)
        assert api.sent("sendPhoto") == []
        assert "photo" in api.texts_to(AUTH_CHAT)[0].lower()


class TestPollingAndLimits:
    def test_offset_advances_past_processed_updates(self):
        api = FakeApi(updates=[[make_update(7, AUTH_CHAT, "/status"),
                                make_update(9, AUTH_CHAT, "/status")]])
        cmd = make_commander(api, {"status": lambda: "ok"})
        assert cmd._poll_once() == 2
        assert cmd._offset == 10                 # max(update_id) + 1
        cmd._poll_once()
        second_poll = [p for m, p, _ in api.calls if m == "getUpdates"][1]
        assert second_poll["offset"] == 10

    def test_outbound_replies_rate_limited(self):
        api = FakeApi()
        cmd = make_commander(api, {"status": lambda: "ok"},
                             max_replies_per_min=2)
        for i in range(4):
            cmd._handle_update(make_update(i, AUTH_CHAT, "/status"),
                               now=1000.0 + i)
        assert len(api.sent()) == 2              # window caps sends
        # window slides: a minute later sends are allowed again
        cmd._handle_update(make_update(9, AUTH_CHAT, "/status"), now=1065.0)
        assert len(api.sent()) == 3

    def test_start_stop_thread_lifecycle(self):
        api = FakeApi()
        cmd = make_commander(api, {"status": lambda: "ok"})
        assert cmd.start() is True
        assert cmd._thread is not None and cmd._thread.daemon
        cmd.stop(timeout=1.0)
        assert cmd._thread is None
        assert any(m == "getUpdates" for m, _, _ in api.calls)

    def test_update_without_message_only_advances_offset(self):
        api = FakeApi()
        cmd = make_commander(api, {})
        cmd._handle_update({"update_id": 42,
                            "callback_query": {"data": "x"}}, now=1000.0)
        assert cmd._offset == 43
        assert api.calls == []


class TestSendAlertWrapper:
    def test_unconfigured_returns_false(self, monkeypatch):
        monkeypatch.setattr(telegram_bot.config, "TELEGRAM_TOKEN", "")
        monkeypatch.setattr(telegram_bot.config, "TELEGRAM_CHAT_ID", "")
        assert send_alert("hello") is False

    def test_sends_via_transport(self, monkeypatch):
        monkeypatch.setattr(telegram_bot.config, "TELEGRAM_TOKEN", "123:T")
        monkeypatch.setattr(telegram_bot.config, "TELEGRAM_CHAT_ID", "42")
        sent = {}

        def fake_api(method, params=None, **kwargs):
            sent["method"], sent["params"] = method, params
            return {"ok": True}

        monkeypatch.setattr(telegram_bot, "_http_api", fake_api)
        assert send_alert("Moisture critical") is True
        assert sent["method"] == "sendMessage"
        assert sent["params"] == {"chat_id": "42", "text": "Moisture critical"}

    def test_transport_error_returns_false(self, monkeypatch):
        monkeypatch.setattr(telegram_bot.config, "TELEGRAM_TOKEN", "123:T")
        monkeypatch.setattr(telegram_bot.config, "TELEGRAM_CHAT_ID", "42")

        def fake_api(method, params=None, **kwargs):
            raise OSError("network down")

        monkeypatch.setattr(telegram_bot, "_http_api", fake_api)
        assert send_alert("hello") is False


class TestMultipart:
    def test_encodes_fields_and_file(self):
        body, content_type = _multipart_encode(
            {"chat_id": "42"}, {"photo": ("photo.jpg", b"JPEGDATA", "image/jpeg")})
        boundary = content_type.split("boundary=", 1)[1]
        assert content_type.startswith("multipart/form-data; boundary=")
        assert f"--{boundary}\r\n".encode() in body
        assert body.endswith(f"--{boundary}--\r\n".encode())
        assert b'name="chat_id"\r\n\r\n42\r\n' in body
        assert b'filename="photo.jpg"' in body
        assert b"Content-Type: image/jpeg\r\n\r\nJPEGDATA\r\n" in body
