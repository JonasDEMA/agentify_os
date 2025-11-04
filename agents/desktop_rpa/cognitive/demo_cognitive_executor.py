"""Demo script for Cognitive Executor."""

import asyncio
import logging

from agents.desktop_rpa.cognitive.cognitive_executor import CognitiveExecutor
from agents.desktop_rpa.config.settings import settings

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


async def demo_simple_task():
    """Demo: Simple task - Open Start Menu."""
    logger.info("=" * 80)
    logger.info("DEMO: Simple Task - Open Start Menu")
    logger.info("=" * 80)
    
    executor = CognitiveExecutor()
    
    task = {
        "goal": "Open the Windows Start Menu",
    }
    
    result = await executor.execute(task)
    
    logger.info("\n" + "=" * 80)
    logger.info("RESULT:")
    logger.info("=" * 80)
    logger.info(f"Status: {result['status']}")
    logger.info(f"Steps: {result['steps']}")
    logger.info(f"Final State: {result['final_state']}")
    logger.info("\nActions taken:")
    for i, action in enumerate(result['actions'], 1):
        logger.info(f"  {i}. {action['action_type']} - {action['reasoning']}")
    logger.info("=" * 80)
    
    return result


async def demo_complex_task():
    """Demo: Complex task - Open Notepad and type text."""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO: Complex Task - Open Notepad and Type Text")
    logger.info("=" * 80)
    
    executor = CognitiveExecutor()
    
    task = {
        "goal": "Open Notepad and type 'Hello from Cognitive RPA Agent!'",
    }
    
    result = await executor.execute(task)
    
    logger.info("\n" + "=" * 80)
    logger.info("RESULT:")
    logger.info("=" * 80)
    logger.info(f"Status: {result['status']}")
    logger.info(f"Steps: {result['steps']}")
    logger.info(f"Final State: {result['final_state']}")
    logger.info("\nActions taken:")
    for i, action in enumerate(result['actions'], 1):
        logger.info(
            f"  {i}. {action['action_type']} "
            f"(confidence={action['confidence']:.2f}) - {action['reasoning']}"
        )
    logger.info("=" * 80)
    
    return result


async def demo_with_obstacles():
    """Demo: Task with potential obstacles."""
    logger.info("\n" + "=" * 80)
    logger.info("DEMO: Task with Potential Obstacles")
    logger.info("=" * 80)
    
    executor = CognitiveExecutor()
    
    task = {
        "goal": "Find and open the Calculator application",
    }
    
    result = await executor.execute(task)
    
    logger.info("\n" + "=" * 80)
    logger.info("RESULT:")
    logger.info("=" * 80)
    logger.info(f"Status: {result['status']}")
    logger.info(f"Steps: {result['steps']}")
    logger.info(f"Final State: {result['final_state']}")
    logger.info("\nActions taken:")
    for i, action in enumerate(result['actions'], 1):
        logger.info(
            f"  {i}. {action['action_type']} "
            f"(confidence={action['confidence']:.2f}) - {action['reasoning']}"
        )
    
    if result.get('obstacles'):
        logger.info("\nObstacles encountered:")
        for i, obstacle in enumerate(result['obstacles'], 1):
            logger.info(f"  {i}. Step {obstacle['step']}: {obstacle['error']}")
    
    logger.info("=" * 80)
    
    return result


async def main():
    """Run all demos."""
    logger.info("Starting Cognitive Executor Demos")
    logger.info(f"Using model: {settings.llm_model}")
    logger.info(f"Max steps: 20")
    logger.info("")
    
    try:
        # Demo 1: Simple task
        await demo_simple_task()
        
        # Wait between demos
        logger.info("\nWaiting 5 seconds before next demo...")
        await asyncio.sleep(5)
        
        # Demo 2: Complex task
        await demo_complex_task()
        
        # Wait between demos
        logger.info("\nWaiting 5 seconds before next demo...")
        await asyncio.sleep(5)
        
        # Demo 3: Task with obstacles
        await demo_with_obstacles()
        
        logger.info("\n" + "=" * 80)
        logger.info("ALL DEMOS COMPLETED!")
        logger.info("=" * 80)
        
    except KeyboardInterrupt:
        logger.info("\nDemos interrupted by user")
    except Exception as e:
        logger.error(f"Demos failed: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    asyncio.run(main())

