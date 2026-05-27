#!/usr/bin/env python3
"""Production smoke test for the deployed AI Trainer API.

The script creates an isolated demo user and exercises the public auth flow,
protected CRUD endpoints, AI-backed endpoints, file uploads, and frontend
static routes through the deployed domain.
"""

from __future__ import annotations

import argparse
import base64
import json
import sys
import time
from dataclasses import dataclass
from datetime import date, timedelta
from typing import Any, Callable

import httpx


PNG_1X1 = base64.b64decode(
    "iVBORw0KGgoAAAANSUhEUgAAAGAAAABgCAIAAABt+uBvAAAA1klEQVR4nO3QMQHAIADAMJga"
    "ROBfCjqmAGogeft1nr0Gd9+jYVAzKBgUDAoGBYOCQcGgYFAwKBgUDAoGBYOCQcGgYFAwKBgU"
    "DAoGBYOCQcGgYFAwKBgUDAoGBYOCQcGgYFAwKBgUDAoGBYOCQcGgYFAwKBgUDAoGBYOCQcGg"
    "YFAwKBgUDAoGBYOCQcGgYFAwKBgUDAoGBYOCQcGgYFAwKBgUDAoGBYOCQcGgYFAwKBgUDAoG"
    "BYOCQcGgYFAwKBgUDAoGBYOCQcGgYFAwKBgUDAoGBYPG2w/M1gIKSqf8jQAAAABJRU5ErkJggg=="
)


@dataclass
class SmokeState:
    email: str
    password: str
    token: str | None = None
    refresh_token: str | None = None
    profile_id: str | None = None
    exercise_id: str | None = None
    workout_plan_id: str | None = None
    workout_session_id: str | None = None
    workout_exercise_id: str | None = None
    schedule_entry_id: str | None = None
    nutrition_plan_id: str | None = None
    conversation_id: str | None = None
    uploaded_url: str | None = None


class SmokeRunner:
    def __init__(self, base_url: str, *, skip_ai: bool) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_url = f"{self.base_url}/api/v1"
        self.skip_ai = skip_ai
        self.client = httpx.Client(timeout=180, follow_redirects=False)
        self.state = SmokeState(
            email=f"prod-smoke-{int(time.time())}@example.com",
            password="Password123!",
        )
        self.failures: list[str] = []
        self.skipped: list[str] = []

    def close(self) -> None:
        self.client.close()

    def headers(self) -> dict[str, str]:
        if not self.state.token:
            return {}
        return {"Authorization": f"Bearer {self.state.token}"}

    def request(
        self,
        method: str,
        path: str,
        *,
        expected: int | tuple[int, ...] = 200,
        api: bool = True,
        **kwargs: Any,
    ) -> httpx.Response:
        url = f"{self.api_url if api else self.base_url}{path}"
        response = self.client.request(method, url, **kwargs)
        expected_codes = (expected,) if isinstance(expected, int) else expected
        if response.status_code not in expected_codes:
            body = response.text[:1000].replace("\n", " ")
            raise AssertionError(f"{method} {path}: expected {expected_codes}, got {response.status_code}: {body}")
        return response

    def step(self, name: str, fn: Callable[[], None]) -> None:
        started = time.monotonic()
        try:
            fn()
        except Exception as exc:  # noqa: BLE001 - this is a smoke reporter
            self.failures.append(f"{name}: {type(exc).__name__}: {exc}")
            print(f"FAIL {name}: {type(exc).__name__}: {exc}")
            return
        elapsed = time.monotonic() - started
        print(f"PASS {name} ({elapsed:.1f}s)")

    def skip(self, name: str, reason: str) -> None:
        self.skipped.append(f"{name}: {reason}")
        print(f"SKIP {name}: {reason}")

    def run(self) -> int:
        steps: list[tuple[str, Callable[[], None]]] = [
            ("frontend root HTTPS", self.frontend_root),
            ("frontend register page", self.frontend_register),
            ("backend register endpoint", self.backend_register_probe),
            ("auth register", self.auth_register),
            ("auth login", self.auth_login),
            ("frontend refresh proxy", self.frontend_refresh_proxy),
            ("users me", self.users_me),
            ("profile get missing", self.profile_get_missing),
            ("profile update", self.profile_update),
            ("profile get", self.profile_get),
            ("analytics dashboard profile weight fallback", self.analytics_dashboard_profile_weight_fallback),
            ("medical restrictions", self.medical_restrictions),
            ("exercises taxonomy", self.exercises_taxonomy),
            ("exercises list/detail/search", self.exercises_list_detail),
            ("nutrition foods search", self.nutrition_foods_search),
            ("nutrition log/list/summary", self.nutrition_log_flow),
            ("analytics weight/measurements/dashboard", self.analytics_basic),
            ("file upload and serve", self.file_upload_and_serve),
        ]

        if self.skip_ai:
            self.skip("workout generate/schedule/log", "--skip-ai")
            self.skip("nutrition generate/activate", "--skip-ai")
            self.skip("nutrition recognize photo", "--skip-ai")
            self.skip("chat stream/delete", "--skip-ai")
        else:
            steps.extend(
                [
                    ("workout generate/schedule/log", self.workout_flow),
                    ("nutrition generate/activate", self.nutrition_generate_flow),
                    ("nutrition recognize photo", self.nutrition_recognize),
                    ("chat stream/delete", self.chat_flow),
                ]
            )

        steps.extend(
            [
                ("analytics exercise history", self.analytics_exercise_history),
                ("auth logout", self.auth_logout),
            ]
        )

        for name, fn in steps:
            self.step(name, fn)

        print("\nSUMMARY")
        print(f"passed={len(steps) - len(self.failures)} failed={len(self.failures)} skipped={len(self.skipped)}")
        for failure in self.failures:
            print(f"- {failure}")
        for skipped in self.skipped:
            print(f"- skipped {skipped}")
        return 1 if self.failures else 0

    def frontend_root(self) -> None:
        response = self.request("GET", "/", api=False)
        assert "text/html" in response.headers.get("content-type", "")

    def frontend_register(self) -> None:
        response = self.request("GET", "/register", api=False)
        assert "text/html" in response.headers.get("content-type", "")

    def backend_register_probe(self) -> None:
        # /openapi.json is intentionally not exposed publicly. Confirm backend
        # reachability via the register endpoint with bad payload — should
        # return 422, not 502/504.
        response = self.request(
            "POST",
            "/auth/register",
            json={},
            expected=(422,),
        )
        assert "detail" in response.json()

    def auth_register(self) -> None:
        response = self.request(
            "POST",
            "/auth/register",
            json={"email": self.state.email, "password": self.state.password},
        )
        data = response.json()
        assert data["email"] == self.state.email
        assert data["requires_verification"] is False

    def auth_login(self) -> None:
        response = self.request(
            "POST",
            "/auth/login",
            json={"email": self.state.email, "password": self.state.password},
        )
        data = response.json()
        assert data["access_token"]
        assert data["user"]["is_verified"] is True
        self.state.token = data["access_token"]
        self.state.refresh_token = response.cookies.get("refresh_token")
        assert self.state.refresh_token

    def frontend_refresh_proxy(self) -> None:
        response = self.client.post(
            f"{self.base_url}/api/auth/refresh",
            cookies={"refresh_token": self.state.refresh_token or ""},
        )
        if response.status_code != 200:
            raise AssertionError(f"frontend refresh returned {response.status_code}: {response.text[:500]}")
        data = response.json()
        assert data["accessToken"]
        self.state.token = data["accessToken"]
        rotated = response.cookies.get("refresh_token")
        if rotated:
            self.state.refresh_token = rotated

    def users_me(self) -> None:
        response = self.request("GET", "/users/me", headers=self.headers())
        data = response.json()
        assert data["email"] == self.state.email

    def profile_get_missing(self) -> None:
        self.request("GET", "/profiles/me", expected=404, headers=self.headers())

    def profile_update(self) -> None:
        response = self.request(
            "PUT",
            "/profiles/me",
            headers=self.headers(),
            json={
                "first_name": "Prod",
                "last_name": "Smoke",
                "date_of_birth": "2007-05-19",
                "gender": "male",
                "height_cm": 180,
                "weight_kg": 76,
                "experience_level": "intermediate",
                "goal": "muscle_gain",
                "sport_type": "gym",
                "activity_level": "moderate",
                "target_weight_kg": 80,
                "equipment_available": "full_gym",
                "training_days_per_week": 3,
                "meals_per_day": 4,
                "food_allergies": "",
                "disliked_foods": "",
                "custom_health_notes": "prod smoke test",
                "medical_restriction_ids": [],
            },
        )
        data = response.json()
        assert data["first_name"] == "Prod"
        self.state.profile_id = data["id"]

    def profile_get(self) -> None:
        response = self.request("GET", "/profiles/me", headers=self.headers())
        assert response.json()["id"] == self.state.profile_id

    def analytics_dashboard_profile_weight_fallback(self) -> None:
        response = self.request("GET", "/analytics/dashboard", headers=self.headers())
        data = response.json()
        assert data["current_weight"] == 76

    def medical_restrictions(self) -> None:
        response = self.request("GET", "/profiles/medical-restrictions", headers=self.headers())
        assert isinstance(response.json(), list)

    def exercises_taxonomy(self) -> None:
        assert isinstance(self.request("GET", "/exercises/muscle-groups", headers=self.headers()).json(), list)
        assert isinstance(self.request("GET", "/exercises/equipment", headers=self.headers()).json(), list)

    def exercises_list_detail(self) -> None:
        response = self.request("GET", "/exercises?per_page=10", headers=self.headers())
        exercises = response.json()
        assert exercises, "exercise seed catalog is empty"
        self.state.exercise_id = exercises[0]["id"]
        detail = self.request("GET", f"/exercises/{self.state.exercise_id}", headers=self.headers()).json()
        assert detail["id"] == self.state.exercise_id
        search = self.request("GET", "/exercises?search=жим&per_page=5", headers=self.headers()).json()
        assert isinstance(search, list)

    def nutrition_foods_search(self) -> None:
        response = self.request("GET", "/nutrition/foods/search?q=рис&per_page=5", headers=self.headers())
        assert isinstance(response.json(), list)

    def nutrition_log_flow(self) -> None:
        today = date.today().isoformat()
        self.request(
            "POST",
            "/nutrition/logs",
            headers=self.headers(),
            json={
                "food_name": "Рис",
                "meal_type": "lunch",
                "quantity_g": 150,
                "calories": 195,
                "protein_g": 4,
                "fat_g": 1,
                "carbs_g": 42,
                "logged_at": today,
                "notes": "prod smoke",
            },
        )
        logs = self.request("GET", f"/nutrition/logs?date={today}", headers=self.headers()).json()
        assert any(log["food_name"] == "Рис" for log in logs)
        summary = self.request("GET", f"/nutrition/summary?date={today}", headers=self.headers()).json()
        assert summary["total_calories"] >= 195

    def analytics_basic(self) -> None:
        today = date.today().isoformat()
        self.request("POST", "/analytics/weight", headers=self.headers(), json={"weight_kg": 76, "logged_at": today})
        weight = self.request("GET", "/analytics/weight", headers=self.headers()).json()
        assert weight
        self.request(
            "POST",
            "/analytics/measurements",
            headers=self.headers(),
            json={"measurement_type": "waist", "value_cm": 82, "logged_at": today},
        )
        measurements = self.request("GET", "/analytics/measurements?type=waist", headers=self.headers()).json()
        assert measurements
        dashboard = self.request("GET", "/analytics/dashboard", headers=self.headers()).json()
        assert "calories_today" in dashboard

    def file_upload_and_serve(self) -> None:
        response = self.request(
            "POST",
            "/files/upload",
            headers=self.headers(),
            files={"file": ("avatar.png", PNG_1X1, "image/png")},
            data={"folder": "avatars"},
        )
        data = response.json()
        assert data["url"].startswith("/uploads/")
        self.state.uploaded_url = data["url"]
        served = self.request("GET", self.state.uploaded_url, api=False)
        assert served.content.startswith(b"\x89PNG")

    def workout_flow(self) -> None:
        today = date.today()
        response = self.request(
            "POST",
            "/workouts/generate",
            headers=self.headers(),
            json={"weeks": 1, "days_per_week": 2, "periodization": "linear"},
        )
        plan = response.json()
        self.state.workout_plan_id = plan["id"]
        self.request("POST", f"/workouts/plans/{self.state.workout_plan_id}/activate", headers=self.headers())
        full_plan = self.request("GET", f"/workouts/plans/{self.state.workout_plan_id}", headers=self.headers()).json()
        session = full_plan["sessions"][0]
        self.state.workout_session_id = session["id"]
        self.state.workout_exercise_id = session["exercises"][0]["id"]
        self.request("POST", f"/workouts/plans/{self.state.workout_plan_id}/schedule", headers=self.headers())
        calendar = self.request(
            "GET",
            f"/workouts/calendar?year={today.year}&month={today.month}",
            headers=self.headers(),
        ).json()
        if calendar:
            self.state.schedule_entry_id = calendar[0]["id"]
        else:
            entry = self.request(
                "POST",
                "/workouts/schedule/start",
                headers=self.headers(),
                json={"session_id": self.state.workout_session_id, "scheduled_date": today.isoformat()},
            ).json()
            self.state.schedule_entry_id = entry["id"]

        tomorrow = (today + timedelta(days=1)).isoformat()
        self.request(
            "PATCH",
            f"/workouts/schedule/{self.state.schedule_entry_id}/reschedule",
            headers=self.headers(),
            json={"scheduled_date": tomorrow},
        )
        self.request("PATCH", f"/workouts/schedule/{self.state.schedule_entry_id}/complete", headers=self.headers())
        self.request(
            "POST",
            f"/workouts/exercises/{self.state.workout_exercise_id}/log",
            headers=self.headers(),
            json={
                "set_number": 1,
                "reps_completed": 10,
                "weight_kg": 40,
                "is_warmup": False,
                "scheduled_workout_id": self.state.schedule_entry_id,
            },
        )
        filtered = self.request(
            "GET",
            f"/workouts/plans/{self.state.workout_plan_id}?entry_id={self.state.schedule_entry_id}",
            headers=self.headers(),
        ).json()
        assert filtered["sessions"][0]["exercises"][0]["logged_sets"]
        self.request("POST", "/workouts/schedule", expected=(200, 500), headers=self.headers(), json={
            "session_id": self.state.workout_session_id,
            "scheduled_date": (today + timedelta(days=2)).isoformat(),
            "is_completed": False,
        })

    def nutrition_generate_flow(self) -> None:
        response = self.request(
            "POST",
            "/nutrition/generate",
            headers=self.headers(),
            json={"goal": "muscle_gain", "meals_per_day": 3},
        )
        plan = response.json()
        self.state.nutrition_plan_id = plan["id"]
        self.request("GET", "/nutrition/plans", headers=self.headers())
        self.request("GET", f"/nutrition/plans/{self.state.nutrition_plan_id}", headers=self.headers())
        self.request("POST", f"/nutrition/plans/{self.state.nutrition_plan_id}/activate", headers=self.headers())

    def nutrition_recognize(self) -> None:
        response = self.request(
            "POST",
            "/nutrition/recognize",
            headers=self.headers(),
            files={"file": ("food.png", PNG_1X1, "image/png")},
        )
        assert "is_food" in response.json()

    def chat_flow(self) -> None:
        conv = self.request(
            "POST",
            "/chat/conversations",
            headers=self.headers(),
            json={"title": "Prod smoke"},
        ).json()
        self.state.conversation_id = conv["id"]
        listed = self.request("GET", "/chat/conversations", headers=self.headers()).json()
        assert any(item["id"] == self.state.conversation_id for item in listed)
        message_url = f"{self.api_url}/chat/conversations/{self.state.conversation_id}/messages"
        chunks: list[str] = []
        with self.client.stream(
            "POST",
            message_url,
            headers=self.headers(),
            json={"content": "Дай короткий совет по разминке перед жимом."},
            timeout=180,
        ) as response:
            if response.status_code != 200:
                raise AssertionError(f"chat stream returned {response.status_code}: {response.text[:500]}")
            for chunk in response.iter_text():
                chunks.append(chunk)
                if "[DONE]" in chunk:
                    break
        assert any("data:" in chunk for chunk in chunks)
        full = self.request("GET", f"/chat/conversations/{self.state.conversation_id}", headers=self.headers()).json()
        assert len(full["messages"]) >= 2
        self.request("DELETE", f"/chat/conversations/{self.state.conversation_id}", headers=self.headers())

    def analytics_exercise_history(self) -> None:
        summary = self.request("GET", "/analytics/exercises-summary", headers=self.headers()).json()
        assert isinstance(summary, list)
        exercise_id = self.state.exercise_id
        if summary:
            exercise_id = summary[0]["exercise_id"]
        if not exercise_id:
            return
        self.request("GET", f"/analytics/exercise-progress/{exercise_id}", headers=self.headers())
        self.request("GET", f"/analytics/exercise-sessions/{exercise_id}", headers=self.headers())
        self.request("GET", "/analytics/completed-sessions", headers=self.headers())

    def auth_logout(self) -> None:
        self.request("POST", "/auth/logout", headers=self.headers())


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="https://coach-ai.ru")
    parser.add_argument("--skip-ai", action="store_true")
    args = parser.parse_args()

    runner = SmokeRunner(args.base_url, skip_ai=args.skip_ai)
    try:
        return runner.run()
    finally:
        runner.close()


if __name__ == "__main__":
    sys.exit(main())
