prompt = """
Generate a structured presentation in JSON format on the topic: "The Impact of Renewable Energy on Global Economies." The presentation should include:

- **Introduction Slide**: Contains a title, subtitle, and an introduction script.
- **Main Content Slides**: Each slide should have a title, bullet points, and a script.
- **Conclusion Slide**: Contains a title, subtitle, and a conclusion script.

Please format the response as follows:

{
  "slides": [
    {
      "type": "introduction",
      "title": "Introduction to [Your Topic]",
      "subtitle": "[Subtitle]",
      "script": "[Introduction script]"
    },
    {
      "type": "main",
      "title": "[Main Slide Title]",
      "bullet_points": [
        "[Bullet point 1]",
        "[Bullet point 2]",
        "[Bullet point 3]"
      ],
      "script": "[Detailed script for the main slide]"
    },
    {
      "type": "conclusion",
      "title": "Conclusion",
      "subtitle": "[Subtitle]",
      "script": "[Conclusion script]"
    }
  ]
}

**Example:**

{
  "slides": [
    {
      "type": "introduction",
      "title": "The Impact of Renewable Energy on Global Economies",
      "subtitle": "Driving Sustainable Growth",
      "script": "In this presentation, we will explore how renewable energy sources are influencing global economies, fostering sustainable development, and reshaping industries worldwide."
    },
    {
      "type": "main",
      "title": "Economic Benefits of Renewable Energy",
      "bullet_points": [
        "Job creation in green industries",
        "Reduction in energy costs",
        "Attraction of sustainable investments"
      ],
      "script": "Renewable energy initiatives have led to significant job creation in sectors like solar and wind power. Additionally, the shift to renewables has reduced energy costs for businesses and consumers, while attracting investments focused on sustainability."
    },
    {
      "type": "main",
      "title": "Challenges in Transitioning to Renewable Energy",
      "bullet_points": [
        "High initial capital expenditure",
        "Infrastructure adaptation requirements",
        "Intermittency and reliability concerns"
      ],
      "script": "Transitioning to renewable energy presents challenges such as the need for substantial upfront investment, the necessity to adapt existing infrastructure, and concerns over the reliability of energy supply due to the intermittent nature of some renewable sources."
    },
    {
      "type": "conclusion",
      "title": "Conclusion",
      "subtitle": "The Path Forward",
      "script": "Embracing renewable energy is crucial for sustainable economic growth. While challenges exist, the long-term benefits of a greener economy outweigh the initial hurdles, paving the way for a resilient and prosperous future."
    }
  ]
}
"""

import requests

url = "http://localhost:9000/chat"

# {
#    "messages": [
#        {
#            "role":"user",
#           "content":[{"text":""}]
#        }
#    ],
#    "model_id": "meta.llama3-1-405b-instruct-v1:0",
#    "inference_config": {
#        "maxTokens": 512,
#        "temperature": 0.5,
#        "topP": 0.9
#    }
# }

if __name__ == "__main__":
    payload = {
        "messages": [
            {
                "role": "user",
                "content": [{"text": prompt}]
            }
        ],
        "model_id": "meta.llama3-1-405b-instruct-v1:0",
        "inference_config": {
            "maxTokens": 512,
            "temperature": 0.5,
            "topP": 0.9
        }
    }

    response = requests.post(url, json=payload)

    response_json = response.json()
    response_text = response_json["response_text"]
    print(response_text)

