"""Single bounded HTTP request in a killable process. Credentials use stdin, never argv."""

import json
import resource
import sys
import time

import httpx

from .errors import RagError


def request_once(url, key, encoded, timeout, transport=None):
    deadline = time.monotonic() + timeout
    with httpx.Client(
        timeout=min(5, timeout), follow_redirects=False, transport=transport, trust_env=False
    ) as client:
        with client.stream(
            "POST",
            url,
            headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"},
            content=encoded,
        ) as response:
            if response.status_code != 200:
                raise RagError("provider_request_failed", 502)
            raw = bytearray()
            for part in response.iter_bytes():
                if len(raw) + len(part) > 32768 or time.monotonic() > deadline:
                    raise RagError("provider_response_budget", 502)
                raw.extend(part)
    return bytes(raw)


def main():
    resource.setrlimit(resource.RLIMIT_CPU, (5, 5))
    resource.setrlimit(resource.RLIMIT_AS, (256 * 1024 * 1024,) * 2)
    resource.setrlimit(resource.RLIMIT_FSIZE, (0, 0))
    resource.setrlimit(resource.RLIMIT_NOFILE, (32, 32))
    try:
        data = json.loads(sys.stdin.buffer.read(20000))
        sys.stdout.buffer.write(
            request_once(
                data["url"], data["key"], json.dumps(data["payload"]).encode(), data["timeout"]
            )
        )
    except RagError as exc:
        print(exc.code)
        sys.exit(2)
    except httpx.TimeoutException:
        print("provider_timeout")
        sys.exit(2)
    except Exception:
        print("provider_invalid_response")
        sys.exit(2)


if __name__ == "__main__":
    main()
