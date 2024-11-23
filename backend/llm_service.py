import httpx

LLM_SERVICE_URL = "http://localhost:9000/chat"

async def generate_presentation_content(topic: str, duration: int, detail_level: str, impersonation: str) -> str:
    payload = {
        "input_text": _build_presentation_text_prompt_from_template(topic, duration, detail_level, impersonation),
    }
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(LLM_SERVICE_URL, json=payload)
        response.raise_for_status()
        return response.json()

def _build_presentation_text_prompt_from_template(topic, duration, detail_level, impersonation):
    try:
        with open("prompts/presentation_content.prompt", 'r', encoding='utf-8') as file:
            template_content = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Template file not found at: prompts/presentation_content.prompt")
    except Exception as e:
        raise Exception(f"An error occurred while reading the template file: {e}")

    placeholders = {
        '[Your Topic]': topic,
        '[Desired Duration]': str(duration),
        '[Beginner/Intermediate/Advanced]': detail_level,
        '[Well-Known Personality]': impersonation
    }

    for placeholder, value in placeholders.items():
        template_content = template_content.replace(placeholder, value)

    return template_content

async def generate_stable_diffusion_prompt(title: str) -> str:
    payload = {
        "input_text": _build_stable_diffusion_prompt_from_template(title),
    }
    async with httpx.AsyncClient(timeout=None) as client:
        response = await client.post(LLM_SERVICE_URL, json=payload)
        response.raise_for_status()
        return response.json()["response_text"]

def _build_stable_diffusion_prompt_from_template(title):
    try:
        with open("prompts/stable_diffusion_prompt_builder.prompt", 'r', encoding='utf-8') as file:
            template_content = file.read()
    except FileNotFoundError:
        raise FileNotFoundError(f"Template file not found at: prompts/stable_diffusion_prompt_builder.prompt")
    except Exception as e:
        raise Exception(f"An error occurred while reading the template file: {e}")

    placeholders = {
        '[Slide Title]': title
    }

    for placeholder, value in placeholders.items():
        template_content = template_content.replace(placeholder, value)

    return template_content

if __name__ == "__main__":
    import asyncio

    #async def main():
    #    topic = "Pollution in the oceans"
    #    result = await generate_stable_diffusion_prompt(topic)
    #    print(result)

    # generate presentation content
    async def main():
        topic = "Pollution in the oceans"
        duration = 5
        detail_level = "Beginner"
        impersonation = "David Attenborough"
        #result = await generate_presentation_content(topic, duration, detail_level, impersonation)
        result = await generate_stable_diffusion_prompt(topic)
        print(result)

    asyncio.run(main())
