import os

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

OLLAMA_HOST = "http://ollama:11434"
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "gemma3:1b")

class Question(BaseModel):
    question: str

data = """He graduated from the Rzeszów University of Technology. In his master's thesis, Kamil developed an application for constructing and processing decision trees. The goal of this application was to analyze and present a modern tool applying decision theory under conditions of risk. His work was highly acclaimed. In his engineering thesis, Kamil compared various types of machine learning algorithms. Kamil has over 3.5 years of experience in application programming, in an international corporate environment at MTU Aero Engines. He is proficient in technologies such as Python, Qt, PyQt, pyqtgraph, Angular, Django, FastAPI, JavaScript, TypeScript, pytest, unittest, TensorFlow, Scikit-Learn, Bokeh, Holoviz, SQL, Pandas, Numpy, Azure, Docker, Docker-compose, Git, Linux, PyInstaller, SQLAlchemy, Redis, MongoDB, REST, design patterns, Test Driven Development (TDD), and CI/CD. Kamil's English proficiency is at the C1 level, allowing him to communicate fluently and effectively. He is an independent developer with extensive knowledge of IT solution architecture. Reliable and thorough, he graduated from his master's program with a perfect grade of 5.0. Kamil excels at mentoring junior colleagues, demonstrating this consistently by providing guidance and support to interns and junior developers. Professionally, he has participated in numerous projects, including developing a desktop application for data analysis and visualization using PyQt5, pyqtgraph, NumPy, and Pandas. He also created an extensive dashboard using Bokeh and Holoviews, visualizing the operations of a cutting machine, facilitating comprehensive analysis and reducing component wear. Additionally, Kamil is involved in an Angular application project utilizing PrimeNG and participates in implementing an AI Assistant designed to respond to inquiries about documents and procedures."""

@app.post("/ask-about-portfolio")
async def ask_about_portfolio(question: Question):

    async def stream_response():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_HOST}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": f"You are an assistant who, based on the information below, is expected to answer recruiters' questions about Kamil's knowledge and experience: {data}.\n\n Question: {question.question} \n Don't lie! If there is no information in the text then make it clear." + "\n", "stream": True}
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        yield line + "\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")

@app.post("/ask")
async def ask(question: Question):

    async def stream_response():
        async with httpx.AsyncClient(timeout=None) as client:
            async with client.stream(
                "POST",
                f"{OLLAMA_HOST}/api/generate",
                json={"model": OLLAMA_MODEL, "prompt": question.question + "\n", "stream": True}
            ) as response:
                async for line in response.aiter_lines():
                    if line:
                        yield line + "\n"

    return StreamingResponse(stream_response(), media_type="text/event-stream")
