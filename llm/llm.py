from langchain_google_genai import ChatGoogleGenerativeAI
from dotenv import load_dotenv
from .langsmith import langsmith
import os


class LLM:
    def __init__(self):
        load_dotenv()
        langsmith("kakao-bot")
        self.llm = ChatGoogleGenerativeAI(
            model="gemini-2.0-flash-exp",
            temperature=0.1,
            max_output_tokens=2048,
        )
        self.messages = [
            {"role": "system", "content": "You are a helpful assistant."}
        ]

    def question(self, question):
        self.messages.append({"role": "user", "content": question})
        return self.llm.invoke(self.messages).content


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
