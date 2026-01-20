"""Integration tests for Calculator POC."""

import asyncio
import time

import httpx
import pytest


@pytest.mark.asyncio
async def test_calculator_end_to_end():
    """Test complete calculator flow: UI -> Scheduler -> Orchestrator -> Agents."""
    base_url = "http://localhost:8000"

    async with httpx.AsyncClient(timeout=30.0) as client:
        # Step 1: Submit calculation request
        response = await client.post(
            f"{base_url}/api/calculate",
            json={
                "num1": 10,
                "num2": 5,
                "operator": "add",
                "locale": "en-US",
                "decimals": 2,
            },
        )

        assert response.status_code == 202
        data = response.json()
        assert "job_id" in data
        assert data["status"] == "pending"

        job_id = data["job_id"]

        # Step 2: Poll for result
        max_attempts = 30
        for attempt in range(max_attempts):
            response = await client.get(f"{base_url}/api/calculate/{job_id}")
            assert response.status_code == 200

            data = response.json()
            status = data["status"]

            if status == "done":
                # Check the formatted result within the result object
                assert data["result"]["formatted_result"] == "15.00"
                print(f"✅ Test passed! Result: {data['result']['formatted_result']}")
                return

            if status == "failed":
                pytest.fail(f"Job failed: {data.get('error')}")

            # Wait before next poll
            await asyncio.sleep(1)

        pytest.fail(f"Job did not complete within {max_attempts} seconds")


@pytest.mark.asyncio
async def test_calculator_different_operators():
    """Test different operators."""
    base_url = "http://localhost:8000"

    test_cases = [
        {"num1": 10, "num2": 5, "operator": "add", "expected": "15.00"},
        {"num1": 10, "num2": 5, "operator": "subtract", "expected": "5.00"},
        {"num1": 10, "num2": 5, "operator": "multiply", "expected": "50.00"},
        {"num1": 10, "num2": 5, "operator": "divide", "expected": "2.00"},
    ]

    async with httpx.AsyncClient(timeout=30.0) as client:
        for test_case in test_cases:
            # Submit request
            response = await client.post(
                f"{base_url}/api/calculate",
                json={
                    "num1": test_case["num1"],
                    "num2": test_case["num2"],
                    "operator": test_case["operator"],
                    "locale": "en-US",
                    "decimals": 2,
                },
            )

            assert response.status_code == 202
            job_id = response.json()["job_id"]

            # Poll for result
            for _ in range(30):
                response = await client.get(f"{base_url}/api/calculate/{job_id}")
                data = response.json()

                if data["status"] == "done":
                    # Check the formatted result within the result object
                    assert data["result"]["formatted_result"] == test_case["expected"]
                    print(
                        f"✅ {test_case['num1']} {test_case['operator']} {test_case['num2']} = {data['result']['formatted_result']}"
                    )
                    break

                if data["status"] == "failed":
                    pytest.fail(f"Job failed: {data.get('error')}")

                await asyncio.sleep(1)


@pytest.mark.asyncio
async def test_calculator_different_locales():
    """Test different locales."""
    base_url = "http://localhost:8000"

    test_cases = [
        {"locale": "en-US", "expected_pattern": "1,234.56"},
        {"locale": "de-DE", "expected_pattern": "1.234,56"},
        {"locale": "fr-FR", "expected_pattern": "1 234,56"},
    ]

    async with httpx.AsyncClient(timeout=30.0) as client:
        for test_case in test_cases:
            # Submit request
            response = await client.post(
                f"{base_url}/api/calculate",
                json={
                    "num1": 1234.56,
                    "num2": 0,
                    "operator": "add",
                    "locale": test_case["locale"],
                    "decimals": 2,
                },
            )

            assert response.status_code == 202
            job_id = response.json()["job_id"]

            # Poll for result
            for _ in range(30):
                response = await client.get(f"{base_url}/api/calculate/{job_id}")
                data = response.json()

                if data["status"] == "done":
                    # Check the formatted result within the result object
                    assert data["result"]["formatted_result"] == test_case["expected_pattern"]
                    print(f"✅ Locale {test_case['locale']}: {data['result']['formatted_result']}")
                    break

                if data["status"] == "failed":
                    pytest.fail(f"Job failed: {data.get('error')}")

                await asyncio.sleep(1)


if __name__ == "__main__":
    # Run tests manually
    print("Running Calculator POC integration tests...")
    print("Make sure all services are running (docker-compose up)")
    print()

    asyncio.run(test_calculator_end_to_end())
    print()
    asyncio.run(test_calculator_different_operators())
    print()
    asyncio.run(test_calculator_different_locales())
    print()
    print("✅ All tests passed!")

