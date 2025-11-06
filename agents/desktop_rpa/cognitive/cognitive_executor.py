"""Cognitive Executor - LLM-guided task execution with Vision Layer."""

import asyncio
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

import pyautogui

from agents.desktop_rpa.agent_comm import AgentDiscovery, AgentRegistry
from agents.desktop_rpa.agent_comm.models import AgentRequest
from agents.desktop_rpa.cognitive.llm_wrapper import LLMWrapper
from agents.desktop_rpa.cognitive.models import LLMRequest
from agents.desktop_rpa.config.luminaos_config import luminaos_config
from agents.desktop_rpa.config.settings import settings
from agents.desktop_rpa.state_graph import PathFinder, StateGraph, StateTracker
from agents.desktop_rpa.vision.element_detector import ElementDetector
from agents.desktop_rpa.window_manager import WindowManager, UserPrompt

logger = logging.getLogger(__name__)


class CognitiveExecutor:
    """Executor that uses LLM to guide task execution.

    This executor:
    1. Receives a high-level goal
    2. Takes screenshots to understand current state
    3. Asks LLM for next action
    4. Executes the suggested action
    5. Repeats until goal is achieved
    """

    def __init__(self, llm_wrapper: LLMWrapper | None = None, callback=None, use_vision: bool = True, use_state_graph: bool = True, use_window_manager: bool = True, use_agent_comm: bool = True):
        """Initialize cognitive executor.

        Args:
            llm_wrapper: LLM wrapper instance (creates new one if None)
            callback: Optional callback function for UI updates (receives event dict)
            use_vision: Whether to use Vision Layer (UI Automation + OCR)
            use_state_graph: Whether to use State Graph for navigation
            use_window_manager: Whether to use Window Manager for intelligent window handling
            use_agent_comm: Whether to use Agent Communication for LuminaOS integration
        """
        self.llm = llm_wrapper or LLMWrapper()
        self.screenshot_dir = Path(settings.screenshot_dir)
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        self.callback = callback
        self.use_vision = use_vision
        self.use_state_graph = use_state_graph
        self.use_window_manager = use_window_manager
        self.use_agent_comm = use_agent_comm

        # Vision Layer
        if use_vision:
            try:
                self.element_detector = ElementDetector()
                logger.info("Vision Layer enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize Vision Layer: {e}")
                self.element_detector = None
                self.use_vision = False
        else:
            self.element_detector = None

        # State Graph
        if use_state_graph:
            self.state_graph = self._create_default_graph()
            self.state_tracker = StateTracker(self.state_graph, initial_state="desktop_visible")
            self.path_finder = PathFinder(self.state_graph)
            logger.info("State Graph enabled")
        else:
            self.state_graph = None
            self.state_tracker = None
            self.path_finder = None

        # Window Manager
        if use_window_manager:
            try:
                self.window_manager = WindowManager()
                logger.info("Window Manager enabled")
            except Exception as e:
                logger.warning(f"Failed to initialize Window Manager: {e}")
                self.window_manager = None
                self.use_window_manager = False
        else:
            self.window_manager = None

        # Agent Communication (LuminaOS)
        if use_agent_comm and luminaos_config.enabled:
            try:
                self.agent_discovery = AgentDiscovery(
                    api_token=luminaos_config.api_token,
                    gateway_url=luminaos_config.gateway_url,
                    sender_id=luminaos_config.sender_id,
                    timeout=luminaos_config.timeout,
                )
                self.agent_registry = AgentRegistry()
                logger.info("Agent Communication enabled (LuminaOS)")
            except Exception as e:
                logger.warning(f"Failed to initialize Agent Communication: {e}")
                self.agent_discovery = None
                self.agent_registry = None
                self.use_agent_comm = False
        else:
            self.agent_discovery = None
            self.agent_registry = None

        # Execution state
        self.current_state = "unknown"
        self.current_step = 0
        self.previous_actions: list[dict[str, Any]] = []
        self.obstacles: list[dict[str, Any]] = []
        self.max_steps = 20  # Prevent infinite loops
        self.pending_user_prompts: list[UserPrompt] = []  # Store prompts for SMS

        logger.info(f"Cognitive Executor initialized (Vision: {self.use_vision}, State Graph: {self.use_state_graph}, Window Manager: {self.use_window_manager}, Agent Comm: {self.use_agent_comm})")

    def _create_default_graph(self) -> StateGraph:
        """Create default state graph with common Windows states."""
        graph = StateGraph()

        # Common states
        graph.add_node("desktop_visible", "Desktop is visible")
        graph.add_node("start_menu_open", "Start menu is open")
        graph.add_node("search_active", "Search box is active")
        graph.add_node("notepad_open", "Notepad is open")
        graph.add_node("calculator_open", "Calculator is open")
        graph.add_node("browser_open", "Web browser is open")
        graph.add_node("file_explorer_open", "File Explorer is open")

        # Common transitions
        # Desktop -> Start Menu
        graph.add_transition("desktop_visible", "start_menu_open", "click_start", confidence=0.95, cost=1.0)
        graph.add_transition("start_menu_open", "desktop_visible", "press_escape", confidence=0.95, cost=1.0)

        # Start Menu -> Search
        graph.add_transition("start_menu_open", "search_active", "start_typing", confidence=0.90, cost=0.5)

        # Search -> Applications
        graph.add_transition("search_active", "notepad_open", "search_and_open_notepad", confidence=0.85, cost=2.0)
        graph.add_transition("search_active", "calculator_open", "search_and_open_calculator", confidence=0.85, cost=2.0)
        graph.add_transition("search_active", "browser_open", "search_and_open_browser", confidence=0.85, cost=2.0)
        graph.add_transition("search_active", "file_explorer_open", "search_and_open_explorer", confidence=0.85, cost=2.0)

        # Applications -> Desktop
        graph.add_transition("notepad_open", "desktop_visible", "close_notepad", confidence=0.90, cost=1.0)
        graph.add_transition("calculator_open", "desktop_visible", "close_calculator", confidence=0.90, cost=1.0)
        graph.add_transition("browser_open", "desktop_visible", "close_browser", confidence=0.90, cost=1.0)
        graph.add_transition("file_explorer_open", "desktop_visible", "close_explorer", confidence=0.90, cost=1.0)

        logger.info(f"Created default state graph: {graph}")
        return graph

    async def execute(self, todo: dict[str, Any]) -> dict[str, Any]:
        """Execute a task using LLM guidance.
        
        Args:
            todo: Task to execute with 'goal' field
            
        Returns:
            Execution result
        """
        goal = todo.get("goal")
        if not goal:
            raise ValueError("Task must have 'goal' field")
        
        logger.info(f"Starting cognitive execution: goal='{goal}'")
        print(f"\n🤖 Starting cognitive execution...")
        print(f"🎯 Goal: {goal}\n")

        # Notify UI
        self._notify("start", {"goal": goal})

        # Check for already open windows (Window Manager)
        if self.use_window_manager and self.window_manager:
            print(f"🪟 Checking for already open windows...")
            self._notify("window_check", {"message": "Checking for open windows..."})

            try:
                # Detect open windows
                open_windows = self.window_manager.detect_open_windows()
                if open_windows:
                    print(f"✅ Found {len(open_windows)} open windows:")
                    for window in open_windows[:5]:  # Show first 5
                        print(f"   • {window.app_name}")

                    # Check if goal mentions specific app
                    goal_lower = goal.lower()
                    for app_name in ["notepad", "calculator", "outlook", "excel", "word", "chrome", "firefox", "edge"]:
                        if app_name in goal_lower:
                            existing_window = self.window_manager.is_app_open(app_name.capitalize())
                            if existing_window:
                                print(f"🎯 {app_name.capitalize()} is already open!")
                                print(f"   Bringing to foreground instead of opening new instance...")
                                self._notify("window_reuse", {"app": app_name.capitalize(), "window": existing_window.title})

                                # Bring to foreground
                                if self.window_manager.bring_to_foreground(existing_window):
                                    print(f"✅ {app_name.capitalize()} brought to foreground")
                                    # Update initial state
                                    self.current_state = f"{app_name}_open"
                                else:
                                    print(f"⚠️  Failed to bring {app_name.capitalize()} to foreground")
                                break
            except Exception as e:
                logger.warning(f"Window Manager error: {e}")
                print(f"⚠️  Window Manager error: {e}")

        # Reset state
        if not hasattr(self, 'current_state') or self.current_state == "unknown":
            self.current_state = "desktop_visible"
        self.previous_actions = []
        self.obstacles = []

        # Reset state tracker
        if self.use_state_graph and self.state_tracker:
            self.state_tracker.reset(self.current_state)

        # Execution loop
        for step in range(1, self.max_steps + 1):
            self.current_step = step
            logger.info(f"Step {step}/{self.max_steps}: state={self.current_state}")

            print(f"\n{'─' * 60}")
            print(f"📍 Step {step}/{self.max_steps}")
            print(f"🔍 Current state: {self.current_state}")

            # Notify UI
            self._notify("step", {"step": step, "max_steps": self.max_steps, "state": self.current_state})
            
            try:
                # Take screenshot
                screenshot_path = await self._take_screenshot(f"step_{step}")
                screenshot_base64 = LLMWrapper.encode_screenshot(screenshot_path)
                print(f"📸 Screenshot taken: {screenshot_path.name}")
                self._notify("screenshot", {"path": str(screenshot_path)})

                # Detect UI elements (Vision Layer)
                ui_elements_text = ""
                if self.use_vision and self.element_detector:
                    print(f"👁️  Detecting UI elements...")
                    self._notify("vision", {"message": "Detecting UI elements..."})

                    try:
                        elements = await asyncio.to_thread(
                            self.element_detector.detect_all_elements,
                            screenshot_path=screenshot_path,
                            use_ocr=True,
                        )
                        ui_elements_text = self.element_detector.format_elements_for_llm(elements)
                        print(f"✅ Detected {len(elements)} UI elements")
                    except Exception as e:
                        logger.warning(f"Vision Layer error: {e}")
                        print(f"⚠️  Vision Layer error: {e}")

                # Ask LLM for next action
                request = LLMRequest(
                    goal=goal,
                    current_state=self.current_state,
                    screenshot_base64=screenshot_base64,
                    context={
                        "step": step,
                        "max_steps": self.max_steps,
                        "ui_elements": ui_elements_text,  # Add UI elements to context
                    },
                    previous_actions=self.previous_actions[-5:],  # Last 5 actions
                    obstacles=self.obstacles,
                )

                print(f"🧠 Asking LLM for next action...")
                self._notify("thinking", {"message": "Analyzing screenshot and deciding next action..."})
                response = await self.llm.ask_for_next_action(request)

                logger.info(
                    f"LLM suggested: {response.suggestion.action_type} "
                    f"(confidence={response.suggestion.confidence:.2f})"
                )
                logger.info(f"Reasoning: {response.suggestion.reasoning}")

                confidence_emoji = "🟢" if response.suggestion.confidence >= 0.8 else "🟡" if response.suggestion.confidence >= 0.6 else "🔴"
                print(f"{confidence_emoji} LLM suggests: {response.suggestion.action_type.upper()}")
                print(f"   💭 Reasoning: {response.suggestion.reasoning}")
                print(f"   📊 Confidence: {response.suggestion.confidence:.2f}")
                if response.suggestion.selector:
                    print(f"   🎯 Selector: {response.suggestion.selector}")
                if response.suggestion.value:
                    print(f"   ✍️  Value: {response.suggestion.value}")

                # Notify UI
                self._notify("action_suggested", {
                    "action": response.suggestion.action_type,
                    "reasoning": response.suggestion.reasoning,
                    "confidence": response.suggestion.confidence,
                    "selector": response.suggestion.selector,
                    "value": response.suggestion.value,
                })
                
                # Check for warnings
                if response.warnings:
                    for warning in response.warnings:
                        logger.warning(f"LLM Warning: {warning}")
                        print(f"⚠️  Warning: {warning}")

                # Execute suggested action
                print(f"⚙️  Executing action...")
                self._notify("executing", {"action": response.suggestion.action_type})
                action_result = await self._execute_action(response.suggestion)
                print(f"✅ Action completed: {action_result.get('status', 'unknown')}")
                self._notify("action_completed", {"result": action_result})
                
                # Record action
                self.previous_actions.append({
                    "step": step,
                    "action_type": response.suggestion.action_type,
                    "selector": response.suggestion.selector,
                    "value": response.suggestion.value,
                    "reasoning": response.suggestion.reasoning,
                    "confidence": response.suggestion.confidence,
                    "result": action_result.get("status"),
                    "timestamp": datetime.now().isoformat(),
                })
                
                # Update state
                if response.next_state_prediction:
                    old_state = self.current_state
                    self.current_state = response.next_state_prediction
                    print(f"🔄 State updated to: {self.current_state}")

                    # Update state tracker
                    if self.use_state_graph and self.state_tracker:
                        self.state_tracker.update_state(
                            self.current_state,
                            action_taken=response.suggestion.action_type,
                            metadata={"step": step, "confidence": response.suggestion.confidence}
                        )

                        # Check for loops
                        if self.state_tracker.is_looping():
                            logger.warning("Loop detected in state transitions")
                            print("⚠️  Loop detected! Trying alternative approach...")

                            # Add to obstacles
                            self.obstacles.append({
                                "step": step,
                                "error": "Loop detected in state transitions",
                                "timestamp": datetime.now().isoformat(),
                            })

                # Check if goal is achieved
                if self._is_goal_achieved(response, action_result):
                    logger.info(f"Goal achieved in {step} steps!")
                    print(f"\n🎉 Goal achieved in {step} steps!")

                    # Get state graph summary
                    state_summary = {}
                    if self.use_state_graph and self.state_tracker:
                        state_summary = self.state_tracker.get_summary()
                        print(f"\n📊 State Graph Summary:")
                        print(f"   - Path taken: {' -> '.join(self.state_tracker.get_path_taken())}")
                        print(f"   - Total states visited: {state_summary['unique_states']}")

                    result = {
                        "status": "success",
                        "steps": step,
                        "final_state": self.current_state,
                        "actions": self.previous_actions,
                        "state_summary": state_summary,
                    }
                    self._notify("completed", result)
                    return result
                
                # Wait before next step
                await asyncio.sleep(1.0)
                
            except Exception as e:
                logger.error(f"Error in step {step}: {e}", exc_info=True)
                print(f"❌ Error in step {step}: {e}")

                # Record obstacle
                self.obstacles.append({
                    "step": step,
                    "error": str(e),
                    "timestamp": datetime.now().isoformat(),
                })

                # Continue to next step (LLM might suggest recovery)
                continue

        # Max steps reached
        logger.warning(f"Max steps ({self.max_steps}) reached without achieving goal")
        print(f"\n⚠️  Max steps ({self.max_steps}) reached without achieving goal")
        return {
            "status": "incomplete",
            "steps": self.max_steps,
            "final_state": self.current_state,
            "actions": self.previous_actions,
            "obstacles": self.obstacles,
        }



    def _notify(self, event_type: str, data: dict[str, Any] | None = None):
        """Notify callback about event.

        Args:
            event_type: Type of event (start, step, thinking, executing, completed, etc.)
            data: Event data
        """
        if self.callback:
            try:
                self.callback({
                    "type": event_type,
                    "data": data or {},
                    "timestamp": datetime.now().isoformat(),
                })
            except Exception as e:
                logger.warning(f"Callback error: {e}")

    async def _take_screenshot(self, name: str) -> Path:
        """Take a screenshot.
        
        Args:
            name: Screenshot name
            
        Returns:
            Path to screenshot
        """
        screenshot_path = self.screenshot_dir / f"{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        
        # Take screenshot in thread pool
        screenshot = await asyncio.to_thread(pyautogui.screenshot)
        await asyncio.to_thread(screenshot.save, screenshot_path)
        
        logger.debug(f"Screenshot saved: {screenshot_path}")
        return screenshot_path

    async def _execute_action(self, suggestion: Any) -> dict[str, Any]:
        """Execute suggested action.
        
        Args:
            suggestion: Action suggestion from LLM
            
        Returns:
            Execution result
        """
        action_type = suggestion.action_type
        selector = suggestion.selector
        value = suggestion.value
        
        logger.info(f"Executing: {action_type} (selector={selector}, value={value})")
        
        try:
            if action_type == "click":
                return await self._execute_click(selector)
            elif action_type == "type":
                return await self._execute_type(value)
            elif action_type == "wait_for":
                return await self._execute_wait(selector)
            elif action_type == "screenshot":
                # Already taken screenshot, just return success
                return {"status": "success", "action": "screenshot"}
            else:
                logger.warning(f"Unknown action type: {action_type}")
                return {"status": "unknown_action", "action": action_type}
                
        except Exception as e:
            logger.error(f"Error executing {action_type}: {e}")
            return {"status": "error", "error": str(e)}

    async def _execute_click(self, selector: str | None) -> dict[str, Any]:
        """Execute click action with Vision Layer support.

        Args:
            selector: Click target (coordinates, "center", or element name)

        Returns:
            Execution result
        """
        if not selector:
            return {"status": "error", "error": "No selector provided"}

        x, y = None, None

        # Try Vision Layer first (if enabled and selector is not coordinates)
        if self.use_vision and self.element_detector and not selector.replace(",", "").replace(" ", "").isdigit():
            try:
                print(f"🔍 Searching for element: {selector}")
                element = await asyncio.to_thread(
                    self.element_detector.find_element,
                    search_text=selector,
                )

                if element:
                    x, y = element.center_x, element.center_y
                    print(f"✅ Found element via Vision Layer: {element.name} at ({x}, {y})")
                    logger.info(f"Found element via Vision Layer: {element}")
                else:
                    print(f"⚠️  Element not found via Vision Layer: {selector}")
            except Exception as e:
                logger.warning(f"Vision Layer search error: {e}")
                print(f"⚠️  Vision Layer error: {e}")

        # Fallback to coordinate parsing
        if x is None or y is None:
            if selector == "center":
                # Click center of screen
                screen_width, screen_height = await asyncio.to_thread(pyautogui.size)
                x, y = screen_width // 2, screen_height // 2
            elif "," in selector:
                # Parse coordinates
                try:
                    x, y = map(int, selector.split(","))
                except ValueError:
                    return {"status": "error", "error": f"Invalid coordinates: {selector}"}
            else:
                return {"status": "error", "error": f"Element not found and invalid coordinates: {selector}"}

        # Move mouse slowly to position (so user can see it)
        await asyncio.to_thread(pyautogui.moveTo, x, y, duration=1.0)

        # Click
        await asyncio.to_thread(pyautogui.click)
        logger.info(f"Clicked at ({x}, {y})")

        return {"status": "success", "action": "click", "x": x, "y": y}

    async def _execute_type(self, text: str | None) -> dict[str, Any]:
        """Execute type action.
        
        Args:
            text: Text to type
            
        Returns:
            Execution result
        """
        if not text:
            return {"status": "error", "error": "No text provided"}
        
        # Type text
        await asyncio.to_thread(pyautogui.write, text, interval=0.05)
        logger.info(f"Typed: {text}")
        
        return {"status": "success", "action": "type", "text": text}

    async def _execute_wait(self, duration_str: str | None) -> dict[str, Any]:
        """Execute wait action.
        
        Args:
            duration_str: Duration in seconds
            
        Returns:
            Execution result
        """
        if not duration_str:
            duration = 1.0
        else:
            try:
                duration = float(duration_str)
            except ValueError:
                return {"status": "error", "error": f"Invalid duration: {duration_str}"}
        
        # Wait
        await asyncio.sleep(duration)
        logger.info(f"Waited {duration} seconds")

        return {"status": "success", "action": "wait", "duration": duration}

    async def _send_user_prompt_sms(self, prompt: UserPrompt, phone_number: str | None = None) -> bool:
        """Send user prompt via SMS using LuminaOS agent.

        Args:
            prompt: User prompt to send
            phone_number: Phone number to send to (optional, uses default if None)

        Returns:
            True if SMS sent successfully, False otherwise
        """
        if not self.use_agent_comm or not self.agent_discovery:
            logger.warning("Agent Communication not enabled, cannot send SMS")
            return False

        try:
            # Get phone number from settings or use provided one
            if not phone_number:
                phone_number = settings.user_phone_number

            # If still no phone number, log warning and return
            if not phone_number:
                logger.warning("No phone number configured, cannot send SMS")
                print("⚠️  No phone number configured. Please set USER_PHONE_NUMBER in .env file.")
                return False

            # Format message
            message = f"🤖 CPA Agent needs your decision:\n\n{prompt.message}\n\nOptions: {', '.join(prompt.options)}"

            logger.info(f"Sending SMS notification for prompt: {prompt.prompt_type}")
            print(f"📱 Sending SMS notification...")

            # Try to get SMS agent from registry first
            sms_agent = None
            if self.agent_registry:
                sms_agent = self.agent_registry.get_preferred_agent("sms")

            # If not in registry, discover
            if not sms_agent:
                logger.info("SMS agent not in registry, discovering...")
                sms_agent = await self.agent_discovery.find_agent_by_capability("sms")

                # Save to registry for next time
                if sms_agent and self.agent_registry:
                    self.agent_registry.register_agent(sms_agent)

            if not sms_agent:
                logger.warning("No SMS agent available")
                print(f"⚠️  No SMS agent available")
                return False

            # Send SMS request with correct parameter names
            request = AgentRequest(
                capability="sms",
                parameters={
                    "recipient_number": phone_number,  # Use recipient_number
                    "message_text": message,  # Use message_text
                },
                priority="high",
            )

            response = await self.agent_discovery.send_request(sms_agent, request)

            if response.success:
                logger.info("SMS sent successfully")
                print(f"✅ SMS notification sent to {phone_number}")
                return True
            else:
                logger.error(f"Failed to send SMS: {response.error}")
                print(f"❌ Failed to send SMS: {response.error}")

                # Remove agent from registry if it failed
                if self.agent_registry:
                    self.agent_registry.update_agent_status(sms_agent.id, "offline")

                return False

        except Exception as e:
            logger.error(f"Error sending SMS: {e}")
            print(f"❌ Error sending SMS: {e}")
            return False

    def _is_goal_achieved(self, response: Any, action_result: dict[str, Any]) -> bool:
        """Check if goal is achieved.
        
        Args:
            response: LLM response
            action_result: Action execution result
            
        Returns:
            True if goal is achieved
        """
        # Simple heuristic: if LLM predicts a "done" or "complete" state
        if response.next_state_prediction:
            prediction = response.next_state_prediction.lower()
            if any(keyword in prediction for keyword in ["done", "complete", "success", "sent", "saved"]):
                return True
        
        # Check if LLM has high confidence and suggests no more actions
        if response.suggestion.action_type == "screenshot" and response.suggestion.confidence > 0.9:
            # LLM is just observing, might be done
            return False
        
        return False

