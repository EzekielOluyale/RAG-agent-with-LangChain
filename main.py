from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from langchain_core.messages import HumanMessage

from src.utils import setup_environment
from src.database import get_vector_store, get_checkpointer
from src.agent import build_agent

@asynccontextmanager
async def lifespan(app: FastAPI):
    setup_environment()
    
    print("Connecting to Pinecone vector store...")
    vector_store = get_vector_store()
    checkpointer = get_checkpointer()

    app.state.agent = build_agent(vector_store=vector_store, checkpointer=checkpointer)
    
    print("Application started successfully and listening for traffic.")
    yield
    print("Application shutting down...")

app = FastAPI(
    title="RAG Agent API",
    description="LangChain + Gemini + Pinecone",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust this to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class ChatRequest(BaseModel):
    message: str = Field(..., description="The message sent by the user.")
    thread_id: str = Field(..., description="Unique identifier tracking this specific conversation session.")

class ChatResponse(BaseModel):
    answer: str = Field(..., description="The final verified response from the agent.")

@app.get("/")
async def root():
    return {"message": "RAG Agent Running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}

@app.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    if not request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty.")
        
    try:
        agent = app.state.agent
        
        config = {"configurable": {"thread_id": request.thread_id}}
        
        response = agent.invoke({
            "messages": [HumanMessage(content=request.message)]
        }, config=config)
        
        answer = response["messages"][-1].content
        
        return ChatResponse(answer=answer)
        
    except Exception as e:
        print(f"CRITICAL API ERROR: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while the agent was generating a response."
        )