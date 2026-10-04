# Knowledge Intelligence Agent

A document-based question answering application built using Python, FastAPI, React, PostgreSQL, FAISS, Sentence Transformers, LangGraph, and Ollama.

The application allows a user to upload PDF documents and ask questions about the information contained in those documents. The system processes the uploaded documents, extracts their text, divides the text into smaller chunks, creates embeddings for those chunks, and stores the embeddings in a FAISS vector index.

When a user asks a question, the question is converted into an embedding and compared with the document embeddings. The most relevant document chunks are retrieved and passed as context to a locally running Qwen 2.5 model through Ollama. The generated answer is then returned to the frontend.

The project was built to understand the complete flow of a Retrieval-Augmented Generation (RAG) application, including document processing, embeddings, vector search, database storage, authentication, backend APIs, agent workflow, and frontend integration.

---

## 1. Project Overview

The main idea of the application is to provide a way to work with information stored inside documents.

Instead of sending an entire document to a language model whenever a question is asked, the application first searches the document collection for relevant information.

The overall process is:

User uploads a PDF
→ PDF text is extracted
→ Text is divided into chunks
→ Chunks are converted into embeddings
→ Embeddings are stored in FAISS
→ User asks a question
→ Question is converted into an embedding
→ FAISS searches for similar chunks
→ Relevant chunks are retrieved
→ Retrieved information is given to the language model
→ Qwen 2.5 generates the answer
→ Answer is returned to the React frontend

PostgreSQL is used to store structured application information such as users, documents, and document chunk metadata.

The application therefore has two related but separate storage systems:

PostgreSQL
→ Stores application and document information

FAISS
→ Stores and searches document embeddings

---

## 2. Main Features

The current application contains the following functionality:

- User registration
- User login
- Password hashing using bcrypt
- JWT-based authentication
- PDF document upload
- PDF text extraction
- Text chunking
- Document metadata storage
- Document chunk metadata storage
- Embedding generation
- FAISS similarity search
- Retrieval-Augmented Generation
- LangGraph-based workflow
- Local LLM integration through Ollama
- Qwen 2.5 model integration
- Document listing
- Document deletion
- React frontend
- FastAPI backend
- PostgreSQL database

The project is designed around a simple document question-answering workflow rather than a general-purpose chatbot.

---

## 3. Technology Stack

### Backend

Python is used as the main backend programming language.

FastAPI is used to create the backend APIs.

SQLAlchemy is used to communicate with PostgreSQL and define database models.

PyMuPDF is used for extracting text from PDF files.

### Database

PostgreSQL is used for storing users, documents, and document chunk information.

### Authentication

JWT is used for authentication between the frontend and backend.

bcrypt is used for password hashing.

### Embeddings and Retrieval

Sentence Transformers is used to generate embeddings.

The current embedding model is:

all-MiniLM-L6-v2

FAISS is used for storing embeddings and performing similarity search.

### Agent Workflow

LangGraph is used to organize the question-answering workflow.

### Language Model

Ollama is used to run the language model locally.

The current model is:

Qwen 2.5 3B

### Frontend

React is used to build the user interface.

Vite is used as the frontend development and build tool.

JavaScript and CSS are used for the frontend implementation.

### Development Tools

Git and GitHub are used for source code management.

A Python virtual environment is used for backend dependencies.

---

## 4. Project Structure

The project is divided into backend, frontend, and data directories.

collaborative-knowledge-agent/

    backend/
        app/
            __init__.py
            main.py
            database.py
            models.py
            auth.py
            agent.py

            services/
                document_processor.py
                embedding_service.py
                vector_store.py
                llm_service.py

        requirements.txt

    frontend/
        src/
            App.jsx
            App.css
            main.jsx
            index.css

        package.json
        vite.config.js

    data/
        documents/
        index/

    .gitignore
    README.md

The backend contains the API and processing logic.

The frontend contains the React application.

The data/documents directory is used for uploaded PDF files.

The data/index directory contains the locally generated FAISS index and its metadata.

Generated files such as uploaded documents, the local FAISS index, the Python virtual environment, and frontend dependencies are excluded from Git.

---

# 5. Backend Structure

The backend is implemented using FastAPI.

The main backend files have different responsibilities.

### main.py

This file contains the FastAPI application and API routes.

It connects the frontend requests to the backend services.

### database.py

This file contains the PostgreSQL connection and SQLAlchemy configuration.

It creates the database engine and database sessions.

### models.py

This file contains the SQLAlchemy database models.

The main models are:

- User
- Document
- DocumentChunk

### auth.py

This file contains authentication-related functions.

It handles:

- Password hashing
- Password verification
- JWT token creation
- JWT token decoding

### agent.py

This file contains the question-answering workflow.

It connects retrieval with the language model.

### document_processor.py

This file handles PDF text extraction and text chunking.

### embedding_service.py

This file loads the Sentence Transformer model and generates embeddings.

### vector_store.py

This file contains the FAISS vector store implementation.

It handles:

- Creating the index
- Adding embeddings
- Searching the index
- Saving the index
- Loading the index

### llm_service.py

This file handles communication between the backend and Ollama.

Keeping these parts separate makes the application easier to understand and modify.

---

# 6. Authentication

The application uses JWT-based authentication.

A user first creates an account using an email and password.

The password is not stored directly in PostgreSQL.

Instead, bcrypt is used to create a password hash.

The process is:

User enters password
→ Backend receives password
→ bcrypt creates password hash
→ Hash is stored in PostgreSQL

During login:

User enters email and password
→ Backend finds the user
→ Entered password is compared with stored hash
→ If valid, a JWT token is created
→ Token is returned to the frontend

The JWT contains the user ID as the subject.

For protected operations, the frontend sends the token to the backend.

The backend verifies the token and obtains the user ID.

This allows the backend to associate documents with the user who uploaded them.

---

# 7. Database Design

PostgreSQL is used as the main relational database.

The current database contains three important tables:

users

documents

document_chunks

The relationship is:

User
→ has multiple Documents
→ each Document has multiple Document Chunks

---

## Users

The users table contains:

- id
- email
- password_hash
- created_at

The email is unique.

The original password is never stored directly.

---

## Documents

The documents table contains:

- id
- filename
- storage_path
- owner_id
- created_at

The owner_id connects the document with the user who uploaded it.

The actual PDF file is stored on disk under:

data/documents/

PostgreSQL stores the information needed to identify and manage the document.

---

## Document Chunks

The document_chunks table contains:

- id
- document_id
- page_number
- chunk_order
- start_offset
- end_offset

The document_id connects each chunk to its original document.

The page number and character offsets identify where the chunk came from in the PDF.

This information is also useful when connecting retrieved vector results back to the original document.

---

# 8. Document Upload

The document processing pipeline begins when the user uploads a PDF.

The React frontend sends the PDF to the FastAPI backend.

The backend first checks the uploaded file.

The basic checks are:

- A filename must exist
- The file must have a PDF extension
- The user should not already have a document with the same filename

After validation, the file is stored in:

data/documents/

The backend then starts the document processing process.

The complete upload flow is:

PDF selected by user
→ React frontend
→ FastAPI upload endpoint
→ Authentication check
→ File validation
→ PDF saved
→ Text extracted
→ Text chunked
→ Chunk information stored
→ Embeddings generated
→ FAISS updated
→ Index saved

---

# 9. PDF Text Extraction

PyMuPDF is used for reading PDF files.

The PDF is processed page by page.

For each page, the application extracts the available text.

For example:

PDF

Page 1
→ Extract text

Page 2
→ Extract text

Page 3
→ Extract text

The extracted information is stored temporarily so that it can be divided into smaller chunks.

Pages without useful text are skipped.

The PDF processing implementation is located in:

backend/app/services/document_processor.py

---

# 10. Text Chunking

After text is extracted, it is divided into smaller pieces called chunks.

The reason for chunking is that documents can be very large.

Sending the complete document to the language model for every question is unnecessary.

The current implementation uses:

Chunk size: 1000 characters

Overlap: 200 characters

The overlap means that part of one chunk is repeated in the next chunk.

For example:

Chunk 1:
Text from characters 0 to 1000

Chunk 2:
Text from characters 800 to 1800

Chunk 3:
Text from characters 1600 to 2600

The overlapping section helps retain some context between neighboring chunks.

Each chunk also keeps information about:

- Document ID
- Page number
- Chunk order
- Start offset
- End offset

---

# 11. Why Chunking Is Used

Consider a long document containing several chapters.

A user may ask a question about only one section.

There is no need to process the entire document for every question.

Instead, the document is divided into smaller sections.

When a question is asked, the application searches these sections and retrieves only the ones that are relevant.

This reduces the amount of information that needs to be passed to the language model.

It also makes semantic search possible at the chunk level.

---

# 12. Embeddings

After the document is divided into chunks, each chunk is converted into an embedding.

The project uses Sentence Transformers.

The current model is:

all-MiniLM-L6-v2

An embedding represents a piece of text as a numerical vector.

For example:

Text:
"CPU scheduling decides which process gets CPU time."

is converted into a vector containing numerical values.

The important property of these vectors is that text with related meanings tends to have similar vector representations.

The same embedding model is used for:

- Document chunks
- User questions

This allows the application to compare questions with document chunks.

---

# 13. Why Embeddings Are Used

Suppose the document contains:

"The operating system selects the next process to receive CPU time."

The user may ask:

"How does the operating system choose the next process?"

The wording is different, but the meaning is related.

A semantic embedding allows the system to compare the meaning of the question with the meaning of the document text.

The process is:

Document chunk
→ Embedding

User question
→ Embedding

Question embedding
→ Compare against document embeddings

The most similar document chunks are then retrieved.

---

# 14. FAISS

FAISS is used for vector similarity search.

After the document chunks are converted into embeddings, the embeddings are added to a FAISS index.

The current implementation uses:

IndexFlatIP

The embeddings are normalized before being stored.

The vector store is responsible for:

- Adding embeddings
- Searching embeddings
- Saving the index
- Loading the index

The implementation is located in:

backend/app/services/vector_store.py

The basic flow is:

Document chunks
→ Sentence Transformer
→ Embeddings
→ FAISS

---

# 15. FAISS Metadata Mapping

FAISS works with vectors and positions inside the index.

The application also needs to know which database chunk each vector represents.

For this reason, the project maintains a mapping between FAISS positions and chunk IDs.

For example:

FAISS position 0 → Chunk ID 10

FAISS position 1 → Chunk ID 11

FAISS position 2 → Chunk ID 12

When FAISS returns a search result, the corresponding chunk ID can be used to identify the original document chunk.

This creates the connection:

Question
→ FAISS
→ Chunk ID
→ Database chunk
→ Original document

---

# 16. Persistent Vector Index

The FAISS index is saved locally.

The files are:

data/index/knowledge.faiss

data/index/metadata.json

The FAISS file contains the vector index.

The metadata file contains the chunk ID mapping.

Saving the index means that the application does not need to generate all embeddings again every time it starts.

The index can be loaded when the application starts.

---

# 17. Complete Document Ingestion Pipeline

The complete document ingestion process is:

PDF upload

→ File validation

→ Save PDF

→ Open PDF using PyMuPDF

→ Extract text page by page

→ Divide text into chunks

→ Store chunk metadata in PostgreSQL

→ Generate embeddings using Sentence Transformers

→ Add embeddings to FAISS

→ Save FAISS index

This is the first major part of the RAG pipeline.

---

# 18. Retrieval-Augmented Generation

The question-answering part of the application uses Retrieval-Augmented Generation.

RAG can be divided into two main stages:

1. Retrieval
2. Generation

During retrieval, the system finds relevant information from the uploaded documents.

During generation, the language model uses the retrieved information to generate the response.

The basic flow is:

User question
→ Question embedding
→ FAISS search
→ Relevant document chunks
→ Context
→ Language model
→ Answer

The important point is that the language model receives retrieved document information along with the user's question.

---

# 19. Question Processing

When the user enters a question in the React frontend, the question is sent to the FastAPI backend.

For example:

"What is virtual memory?"

The backend creates an embedding for the question using the same Sentence Transformer model used for document chunks.

The process is:

Question
→ Sentence Transformer
→ Question embedding

The question embedding is then passed to FAISS.

---

# 20. Similarity Search

FAISS compares the question embedding with the document embeddings.

The search returns the most similar vectors.

For example:

Question

"What is virtual memory?"

↓

FAISS search

↓

Relevant chunk 1

Relevant chunk 2

Relevant chunk 3

The retrieved chunk IDs are then used to identify the corresponding document information.

The retrieved text becomes the context for the language model.

---

# 21. LangGraph Workflow

LangGraph is used to organize the agent workflow.

The question-answering process can be thought of as a sequence of steps:

Receive question

→ Retrieve relevant chunks

→ Prepare context

→ Generate response

→ Return answer

Using a workflow structure keeps the retrieval and generation stages separate.

It also makes it possible to add additional steps later.

For example, a future workflow could include:

Question
→ Retrieve
→ Check retrieved information
→ Generate
→ Return sources

The current application keeps the workflow simpler.

---

# 22. Ollama and Qwen 2.5

The project uses Ollama to run the language model locally.

The current model is:

qwen2.5:3b

The backend communicates with Ollama through its local API.

The general flow is:

FastAPI
→ Agent workflow
→ LLM service
→ Ollama
→ Qwen 2.5

Ollama normally runs on:

http://127.0.0.1:11434

The installed models can be checked using:

ollama list

If the Qwen model is not available, it can be downloaded using:

ollama pull qwen2.5:3b

If Ollama is already running, another `ollama serve` process should not be started on the same port.

---

# 23. Context Sent to the Language Model

The language model receives two main pieces of information:

1. The user's question
2. The relevant document context retrieved by FAISS

Conceptually:

Retrieved document context

+

User question

↓

Qwen 2.5

↓

Answer

The retrieval stage therefore happens before the generation stage.

This is different from directly sending the question to a language model without searching the uploaded documents.

---

# 24. Complete Question-Answering Pipeline

The complete question flow is:

User enters question

→ React frontend

→ FastAPI `/agent` endpoint

→ Create question embedding

→ FAISS similarity search

→ Retrieve relevant chunk IDs

→ Identify document chunks

→ Build context

→ LangGraph workflow

→ Ollama

→ Qwen 2.5

→ Generate response

→ FastAPI response

→ React frontend

→ User sees answer

This is the main flow of the application.

---

# 25. PostgreSQL and FAISS

PostgreSQL and FAISS are used for different purposes.

PostgreSQL stores structured information such as:

- Users
- Documents
- Document ownership
- Document metadata
- Chunk metadata

FAISS stores and searches:

- Document embeddings

The relationship can be represented as:

PostgreSQL
→ application records

FAISS
→ vector search

For example:

Document ID 2

→ Chunk ID 10

→ Chunk ID 11

→ Chunk ID 12

The FAISS index contains vectors corresponding to those chunks.

The metadata mapping connects the FAISS results back to the database records.

---

# 26. Document Deletion

The application supports deleting uploaded documents.

When a document is deleted, the application removes the document record and associated chunk information from the database.

The original PDF file is also removed from local storage.

Because the FAISS index contains vectors belonging to the deleted document, the vector index needs to be updated.

The current approach rebuilds the FAISS index using the remaining document chunks.

The process is:

Delete document

→ Delete database records

→ Delete PDF

→ Rebuild FAISS index

This approach keeps the implementation straightforward for the current project.

---

# 27. FastAPI API Layer

FastAPI provides the API layer between the React frontend and the backend services.

The frontend does not directly access PostgreSQL or FAISS.

Instead:

React

→ FastAPI

→ Backend services

The backend then communicates with:

- PostgreSQL
- Document processing
- FAISS
- LangGraph
- Ollama

This keeps the frontend separate from the internal processing logic.

---

# 28. Main API Operations

The backend contains APIs for authentication, document management, and question answering.

Authentication:

/register

/login

Document operations:

GET /documents

POST /documents/upload

DELETE /documents/{document_id}

Agent:

POST /agent

The exact API request and response formats can be tested using the FastAPI Swagger interface.

---

# 29. Swagger API Documentation

FastAPI automatically provides API documentation.

After starting the backend, open:

http://127.0.0.1:8000/docs

The Swagger interface can be used to test the backend independently from the React frontend.

A typical testing sequence is:

Register user

→ Login

→ Upload document

→ View documents

→ Ask question

→ Delete document

This is also useful for finding whether an issue is in the backend or frontend.

---

# 30. React Frontend

The frontend is built using React and Vite.

The frontend provides the interface for interacting with the backend.

The main functionality includes:

- Registration
- Login
- Document upload
- Document listing
- Document deletion
- Question input
- Answer display

The frontend communicates with FastAPI using HTTP requests.

The basic relationship is:

React

↓

HTTP request

↓

FastAPI

↓

Response

↓

React

---

# 31. Document Management in the Frontend

After login, the frontend can request the user's documents.

The backend provides the document list through:

GET /documents

The frontend displays the returned documents.

When the user chooses to delete a document, the frontend sends:

DELETE /documents/{document_id}

After the operation is completed, the frontend can refresh the document list.

---

# 32. Question Interface

The frontend provides an input area where the user can enter a question.

For example:

"What is process scheduling?"

The frontend sends the question to:

POST /agent

The backend performs:

Question embedding

→ FAISS retrieval

→ Context preparation

→ LangGraph workflow

→ Qwen 2.5

The resulting answer is returned to the frontend.

---

# 33. Running the Project

The local application requires four main services:

1. PostgreSQL
2. Ollama
3. FastAPI backend
4. React frontend

Each service has a separate purpose.

PostgreSQL
→ Database

Ollama
→ Local language model

FastAPI
→ Backend and RAG pipeline

React
→ User interface

---

# 34. Backend Setup

Go to the project directory:

C:\Users\91995\OneDrive\Desktop\collaborative-knowledge-agent

The Python virtual environment is:

.venv

Activate it in PowerShell:

Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Then:

.\.venv\Scripts\Activate.ps1

Move to the backend directory:

cd backend

Start FastAPI:

python -m uvicorn app.main:app --reload

The backend runs at:

http://127.0.0.1:8000

Swagger documentation is available at:

http://127.0.0.1:8000/docs

---

# 35. Frontend Setup

Open another terminal.

Go to:

C:\Users\91995\OneDrive\Desktop\collaborative-knowledge-agent\frontend

Install dependencies if required:

npm install

Start the development server:

npm run dev

The frontend normally runs at:

http://localhost:5173

Open this address in the browser.

---

# 36. PostgreSQL Setup

PostgreSQL needs to be running before the backend starts.

The database used by the application is:

knowledge_agent

The backend database configuration is located in:

backend/app/database.py

The application uses SQLAlchemy to create the database connection and sessions.

If PostgreSQL is running inside Docker, its container can be checked using:

docker ps

The exact PostgreSQL startup command depends on how PostgreSQL was configured locally.

---

# 37. Ollama Setup

Check the installed Ollama models:

ollama list

The required model for the current application is:

qwen2.5:3b

If it is not installed:

ollama pull qwen2.5:3b

Ollama should be running before the agent endpoint is used.

The backend communicates with the local Ollama service.

If Ollama is already running, starting another server can produce a port binding error because port 11434 is already being used.

---

# 38. Complete Local Startup

The complete startup process is:

Terminal 1:

Start or check PostgreSQL.

Terminal 2:

Go to the project directory.

Activate the Python environment.

Start FastAPI.

Terminal 3:

Go to the frontend directory.

Start the React development server.

Ollama should also be running.

The final setup is:

PostgreSQL
→ database

Ollama
→ Qwen 2.5

FastAPI
→ backend

React
→ frontend

Then open:

http://localhost:5173

---

# 39. Example End-to-End Usage

Suppose the user has a PDF called:

Complete_Operating_Systems_Notes.pdf

The user logs into the application and uploads the PDF.

The backend saves the file.

PyMuPDF extracts the text.

The text is divided into chunks.

The chunks are stored as document chunk records.

Sentence Transformers generates embeddings for the chunks.

FAISS stores those embeddings.

The user then asks:

"What is virtual memory?"

The question is converted into an embedding.

FAISS searches the stored document vectors.

Relevant chunks from the operating systems notes are returned.

Those chunks are combined into context.

LangGraph organizes the retrieval and generation flow.

The context and question are sent to Qwen 2.5 through Ollama.

Qwen generates the response.

The response is returned through FastAPI.

React displays the answer.

The complete flow is:

PDF

→ PyMuPDF

→ Text

→ Chunks

→ Embeddings

→ FAISS

→ User Question

→ Question Embedding

→ Similarity Search

→ Relevant Chunks

→ Context

→ Qwen 2.5

→ Answer

→ React

---

# 40. Important Design Decisions

## PostgreSQL for application data

PostgreSQL is used because the application has structured data such as users, documents, and relationships between documents and chunks.

## FAISS for vector search

FAISS is used specifically for similarity search over embeddings.

## Local embeddings

Sentence Transformers provides the embedding model locally.

## Local language model

Ollama is used so that the current application can communicate with a locally running language model.

## Separate services

The frontend, backend, database, vector search, and language model are kept as separate parts.

This makes it easier to understand the responsibilities of each component.

---

# 41. Current Limitations

The current project is a working implementation, but there are areas that can be improved.

### Document Sharing

Documents currently have an owner through owner_id.

A complete sharing system can be added later so that a user can explicitly share a document with another user.

### Permission-Aware Retrieval

The retrieval stage can be extended to filter documents according to ownership and sharing permissions before sending retrieved information to the language model.

### Chunking

The current implementation uses character-based chunking.

It can later be improved with sentence, paragraph, token, or semantic-based chunking.

### FAISS Updates

The current document deletion approach rebuilds the FAISS index.

For a larger document collection, a more efficient update strategy could be considered.

### Source References

The application stores page and chunk information.

This can later be used to display the source document and page number along with an answer.

### More File Formats

The current implementation focuses on PDF files.

Support for other document formats can be added later.

---

# 42. Possible Future Improvements

Some possible improvements are:

- Document sharing
- Document-level permissions
- Permission-aware retrieval
- Source citations
- Page-level references
- Better chunking
- More document formats
- Conversation history
- Streaming responses
- Better error handling
- Automated tests
- Improved document search
- Better frontend loading states
- More efficient vector index updates
- Support for additional local models

These are possible extensions of the current application.

---

# 43. Development Flow

The project was developed by building the application in separate stages.

The general development flow was:

Project setup

→ Python environment

→ PostgreSQL configuration

→ Database models

→ Authentication

→ PDF processing

→ Text chunking

→ Embeddings

→ FAISS

→ Retrieval

→ LLM integration

→ LangGraph workflow

→ FastAPI APIs

→ React frontend

→ Frontend/backend integration

→ End-to-end testing

This approach allows individual parts of the system to be tested before connecting the complete application.

---

# 44. Git and Repository

The project is maintained using Git.

The GitHub repository is:

https://github.com/cs25m205-coder/knowledge-intelligence-agent

The repository contains:

- Backend source code
- Frontend source code
- Configuration files
- Requirements
- Documentation

Generated files are excluded from Git.

The `.gitignore` file excludes items such as:

.venv/

__pycache__/

*.pyc

.env

node_modules/

frontend/dist/

data/documents/

data/index/

This prevents local dependencies, uploaded documents, generated vector indexes, and local configuration files from being committed to the repository.

---

# 45. Complete Architecture Summary

The complete application can be summarized as follows.

USER

↓

React Frontend

↓

FastAPI Backend

↓

Authentication / Document APIs / Agent API

↓

For document upload:

PDF

↓

PyMuPDF

↓

Extracted Text

↓

Text Chunks

↓

Sentence Transformers

↓

Embeddings

↓

FAISS

For question answering:

User Question

↓

Sentence Transformer

↓

Question Embedding

↓

FAISS Similarity Search

↓

Relevant Document Chunks

↓

Context

↓

LangGraph

↓

Ollama

↓

Qwen 2.5

↓

Generated Answer

↓

FastAPI

↓

React

↓

User

PostgreSQL works alongside this process to store:

Users

Documents

Document ownership

Document chunk metadata

---

# 46. Final Summary

The Knowledge Intelligence Agent is a document-based question answering application.

The application takes PDF documents, extracts their text, divides the text into chunks, converts the chunks into embeddings, and stores those embeddings in a FAISS vector index.

When a user asks a question, the question is converted into an embedding and compared with the stored document embeddings.

The most relevant chunks are retrieved and used as context for the language model.

LangGraph is used to organize the retrieval and generation workflow.

Qwen 2.5 is run locally using Ollama and generates the final response.

PostgreSQL stores users, documents, and document chunk metadata.

FastAPI provides the backend API.

React provides the frontend interface.

The main RAG pipeline is:

PDF

→ Text Extraction

→ Chunking

→ Embeddings

→ FAISS

→ Retrieval

→ Context

→ Qwen 2.5

→ Answer

The main application structure is:

React

→ FastAPI

→ PostgreSQL

→ Document Processing

→ FAISS

→ LangGraph

→ Ollama / Qwen 2.5

This project helped me understand how the different parts of a RAG application work together, from storing documents and processing text to retrieving relevant information and generating an answer.