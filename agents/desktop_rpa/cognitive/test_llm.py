"""Test script for LLM Wrapper."""

import asyncio
import logging
from pathlib import Path

from agents.desktop_rpa.cognitive.llm_wrapper import LLMWrapper
from agents.desktop_rpa.cognitive.models import LLMRequest, StrategyRequest
from agents.desktop_rpa.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def test_ask_for_next_action():
    """Test asking LLM for next action."""
    logger.info("=" * 80)
    logger.info("TEST: Ask for Next Action")
    logger.info("=" * 80)

    # Create LLM wrapper
    llm = LLMWrapper(api_key=settings.openai_api_key)

    # Create request
    request = LLMRequest(
        goal="Open Outlook and compose a new email",
        current_state="desktop_visible",
        context={
            "screen_resolution": "1920x1080",
            "visible_applications": ["File Explorer", "Chrome"],
        },
        previous_actions=[],
        obstacles=[],
    )

    # Ask for next action
    try:
        response = await llm.ask_for_next_action(request)

        logger.info("\n" + "=" * 80)
        logger.info("LLM RESPONSE:")
        logger.info("=" * 80)
        logger.info(f"State Assessment: {response.state_assessment}")
        logger.info(f"Next State Prediction: {response.next_state_prediction}")
        logger.info("")
        logger.info("Suggested Action:")
        logger.info(f"  Type: {response.suggestion.action_type}")
        logger.info(f"  Selector: {response.suggestion.selector}")
        logger.info(f"  Value: {response.suggestion.value}")
        logger.info(f"  Reasoning: {response.suggestion.reasoning}")
        logger.info(f"  Confidence: {response.suggestion.confidence:.2f}")
        logger.info("")
        if response.warnings:
            logger.info(f"Warnings: {', '.join(response.warnings)}")
        logger.info(f"Model Used: {response.model_used}")
        logger.info(f"Tokens Used: {response.tokens_used}")
        logger.info("=" * 80)

        return response

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise


async def test_ask_for_next_action_with_screenshot():
    """Test asking LLM for next action with screenshot."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST: Ask for Next Action with Screenshot")
    logger.info("=" * 80)

    # Create LLM wrapper
    llm = LLMWrapper(api_key=settings.openai_api_key)

    # Check if screenshot exists
    screenshot_dir = Path(settings.screenshot_dir)
    screenshots = list(screenshot_dir.glob("*.png"))

    if not screenshots:
        logger.warning("No screenshots found. Taking a screenshot first...")
        # Take a screenshot using PyAutoGUI
        import pyautogui
        screenshot_path = screenshot_dir / "test_screenshot.png"
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        screenshot = pyautogui.screenshot()
        screenshot.save(screenshot_path)
        logger.info(f"Screenshot saved to {screenshot_path}")
    else:
        screenshot_path = screenshots[0]
        logger.info(f"Using existing screenshot: {screenshot_path}")

    # Encode screenshot
    screenshot_base64 = LLMWrapper.encode_screenshot(screenshot_path)
    logger.info(f"Screenshot encoded ({len(screenshot_base64)} bytes)")

    # Create request with screenshot
    request = LLMRequest(
        goal="Find and click the Start button",
        current_state="desktop_visible",
        screenshot_base64=screenshot_base64,
        context={
            "screen_resolution": "1920x1080",
        },
        previous_actions=[],
        obstacles=[],
    )

    # Ask for next action
    try:
        response = await llm.ask_for_next_action(request)

        logger.info("\n" + "=" * 80)
        logger.info("LLM RESPONSE (with Vision):")
        logger.info("=" * 80)
        logger.info(f"State Assessment: {response.state_assessment}")
        logger.info(f"Next State Prediction: {response.next_state_prediction}")
        logger.info("")
        logger.info("Suggested Action:")
        logger.info(f"  Type: {response.suggestion.action_type}")
        logger.info(f"  Selector: {response.suggestion.selector}")
        logger.info(f"  Value: {response.suggestion.value}")
        logger.info(f"  Reasoning: {response.suggestion.reasoning}")
        logger.info(f"  Confidence: {response.suggestion.confidence:.2f}")
        logger.info("")
        if response.warnings:
            logger.info(f"Warnings: {', '.join(response.warnings)}")
        logger.info(f"Model Used: {response.model_used}")
        logger.info(f"Tokens Used: {response.tokens_used}")
        logger.info("=" * 80)

        return response

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise


async def test_ask_for_strategy():
    """Test asking LLM for strategy."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST: Ask for Strategy")
    logger.info("=" * 80)

    # Create LLM wrapper
    llm = LLMWrapper(api_key=settings.openai_api_key)

    # Create request
    request = StrategyRequest(
        goal="Send an email via Outlook with an attachment from a project folder",
        context={
            "available_applications": ["Outlook", "File Explorer"],
        },
        known_states=[
            "desktop_visible",
            "outlook_closed",
            "outlook_open",
            "outlook_compose_email",
            "file_explorer_open",
        ],
        known_transitions=[
            {
                "from": "desktop_visible",
                "to": "outlook_open",
                "action": "click Start menu and search for Outlook",
            },
            {
                "from": "outlook_open",
                "to": "outlook_compose_email",
                "action": "click New Email button",
            },
        ],
    )

    # Ask for strategy
    try:
        response = await llm.ask_for_strategy(request)

        logger.info("\n" + "=" * 80)
        logger.info("STRATEGY RESPONSE:")
        logger.info("=" * 80)
        logger.info(f"Strategy Name: {response.strategy_name}")
        logger.info(f"Goal: {response.goal}")
        logger.info(f"Confidence: {response.confidence:.2f}")
        logger.info("")
        logger.info("Preconditions:")
        for i, precondition in enumerate(response.preconditions, 1):
            logger.info(f"  {i}. {precondition}")
        logger.info("")
        logger.info("Steps:")
        for i, step in enumerate(response.steps, 1):
            logger.info(f"  {i}. {step}")
        logger.info("")
        logger.info("Expected States:")
        for i, state in enumerate(response.expected_states, 1):
            logger.info(f"  {i}. {state}")
        logger.info("")
        logger.info(f"Reasoning: {response.reasoning}")
        logger.info(f"Model Used: {response.model_used}")
        logger.info("=" * 80)

        return response

    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)
        raise


async def test_iterative_conversation():
    """Test iterative conversation with LLM."""
    logger.info("\n" + "=" * 80)
    logger.info("TEST: Iterative Conversation")
    logger.info("=" * 80)

    # Create LLM wrapper
    llm = LLMWrapper(api_key=settings.openai_api_key)

    # Simulate a multi-step interaction
    goal = "Open Outlook and send an email"
    current_state = "desktop_visible"
    previous_actions = []

    for step in range(3):
        logger.info(f"\n--- Step {step + 1} ---")

        request = LLMRequest(
            goal=goal,
            current_state=current_state,
            previous_actions=previous_actions,
            obstacles=[],
        )

        response = await llm.ask_for_next_action(request)

        logger.info(f"Current State: {current_state}")
        logger.info(f"Suggested Action: {response.suggestion.action_type}")
        logger.info(f"Reasoning: {response.suggestion.reasoning}")
        logger.info(f"Confidence: {response.suggestion.confidence:.2f}")

        # Simulate action execution
        previous_actions.append({
            "action_type": response.suggestion.action_type,
            "selector": response.suggestion.selector,
            "value": response.suggestion.value,
            "result": "success",
        })

        # Update state based on prediction
        if response.next_state_prediction:
            current_state = response.next_state_prediction
        else:
            current_state = f"after_{response.suggestion.action_type}"

        logger.info(f"New State: {current_state}")


async def main():
    """Run all tests."""
    logger.info("Starting LLM Wrapper Tests")
    logger.info(f"Using model: {settings.llm_model}")
    logger.info(f"Temperature: {settings.llm_temperature}")
    logger.info(f"Max tokens: {settings.llm_max_tokens}")
    logger.info("")

    try:
        # Test 1: Ask for next action (no screenshot)
        await test_ask_for_next_action()

        # Test 2: Ask for next action (with screenshot)
        await test_ask_for_next_action_with_screenshot()

        # Test 3: Ask for strategy
        await test_ask_for_strategy()

        # Test 4: Iterative conversation
        await test_iterative_conversation()

        logger.info("\n" + "=" * 80)
        logger.info("ALL TESTS COMPLETED SUCCESSFULLY!")
        logger.info("=" * 80)

    except Exception as e:
        logger.error(f"Tests failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())

