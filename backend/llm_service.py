import logging
import httpx

LLM_SERVICE_URL = "http://llama_container:9000/chat"

# Configure logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("app.log"),
        logging.StreamHandler()
    ]
)

async def generate_presentation_content(topic: str, duration: int, detail_level: str, impersonation: str) -> str:
    payload = {
        "input_text": _build_presentation_text_prompt_from_template(topic, duration, detail_level, impersonation),
        "duration": duration
    }
    logging.debug("Sending payload to LLM service for presentation content: %s", payload)
    async with httpx.AsyncClient(timeout=None) as client:
        try:
            response = await client.post(LLM_SERVICE_URL, json=payload)
            response.raise_for_status()
            logging.info("Received response from LLM service for presentation content")
            return response.json()["response_text"]
        except httpx.HTTPError as e:
            logging.error("HTTP error occurred while calling LLM service: %s", e)
            raise
        except Exception as e:
            logging.error("Unexpected error occurred: %s", e)
            raise

def _build_presentation_text_prompt_from_template(topic, duration, detail_level, impersonation):
    try:
        with open("prompts/presentation_content.prompt", 'r', encoding='utf-8') as file:
            template_content = file.read()
            logging.info("Successfully read presentation template")
    except FileNotFoundError:
        logging.error("Template file not found at: prompts/presentation_content.prompt")
        raise FileNotFoundError("Template file not found at: prompts/presentation_content.prompt")
    except Exception as e:
        logging.error("An error occurred while reading the template file: %s", e)
        raise

    placeholders = {
        '[Your Topic]': topic,
        '[Desired Duration]': str(duration),
        '[Beginner/Intermediate/Advanced]': detail_level,
        '[Well-Known Personality]': impersonation
    }

    for placeholder, value in placeholders.items():
        template_content = template_content.replace(placeholder, value)

    logging.debug("Built presentation text prompt: %s", template_content)
    return template_content

async def generate_stable_diffusion_prompt(title: str) -> str:
    payload = {
        "input_text": _build_stable_diffusion_prompt_from_template(title),
    }
    logging.debug("Sending payload to LLM service for stable diffusion prompt: %s", payload)
    async with httpx.AsyncClient(timeout=None) as client:
        try:
            response = await client.post(LLM_SERVICE_URL, json=payload)
            response.raise_for_status()
            logging.info("Received response from LLM service for stable diffusion prompt")
            return response.json()["response_text"]
        except httpx.HTTPError as e:
            logging.error("HTTP error occurred while calling LLM service: %s", e)
            raise
        except Exception as e:
            logging.error("Unexpected error occurred: %s", e)
            raise

def _build_stable_diffusion_prompt_from_template(title):
    try:
        with open("prompts/stable_diffusion_prompt_builder.prompt", 'r', encoding='utf-8') as file:
            template_content = file.read()
            logging.info("Successfully read stable diffusion template")
    except FileNotFoundError:
        logging.error("Template file not found at: prompts/stable_diffusion_prompt_builder.prompt")
        raise FileNotFoundError("Template file not found at: prompts/stable_diffusion_prompt_builder.prompt")
    except Exception as e:
        logging.error("An error occurred while reading the template file: %s", e)
        raise

    placeholders = {
        '[Slide Title]': title
    }

    for placeholder, value in placeholders.items():
        template_content = template_content.replace(placeholder, value)

    logging.debug("Built stable diffusion prompt: %s", template_content)
    return template_content

if __name__ == "__main__":
    import asyncio

    async def main():
        topic = "Pollution in the oceans"
        duration = 5
        detail_level = "Beginner"
        impersonation = "David Attenborough"

        os.makedirs(OUTPUT_DIR, exist_ok=True)
        logging.info(f"Output directory ensured: {OUTPUT_DIR}")

        try:
            logging.info("Starting the main async function")
            result = await generate_presentation_content(topic, duration, detail_level, impersonation)
            logging.info("Generated presentation content: %s", result)
        except Exception as e:
            logging.error("An error occurred in the main function: %s", e)

    asyncio.run(main())
