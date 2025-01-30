from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
import os


class Langchain:
    def __init__(self):
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            max_output_tokens=2048,
        )

    def question(self, question):
        return self.llm.invoke(question)

# llm = ChatGoogleGenerativeAI(model="gemini-2.0-flash-exp",
#                                temperature=0.1,
#                                max_output_tokens=2048,
#
#                                )
# message = HumanMessage(
#     content=[
#         {
#             "type": "text",
#             "text": "What's in this image?",
#         },  # You can optionally provide text parts
#         {"type": "image_url", "image_url": "https://picsum.photos/seed/picsum/200/300"},
#     ]
# )
#
# llm.invoke([message])
