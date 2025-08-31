import os
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pymongo import MongoClient
from bson import ObjectId
from typing import Dict, Any, List
import uvicorn

# MongoDB connection
MONGODB_URI = "mongodb+srv://nuwanwp:zXi15ByhNUNFEOOD@cluster0.gjas8wj.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
MONGODB_DB = "fastapi_mongo_api"

# Initialize MongoDB client
client = MongoClient(MONGODB_URI)
db = client[MONGODB_DB]

# Initialize FastAPI app
app = FastAPI(
    title="FastAPI MongoDB Dynamic API",
    description="Dynamic REST API with MongoDB backend supporting any entity/collection",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Helper function to serialize MongoDB documents
def serialize_doc(doc: Dict[str, Any]) -> Dict[str, Any]:
    """Convert MongoDB ObjectId to string for JSON serialization"""
    if doc is None:
        return None
    if "_id" in doc and isinstance(doc["_id"], ObjectId):
        doc["_id"] = str(doc["_id"])
    return doc

# Helper function to convert query parameter values to appropriate types
def convert_query_value(value: str) -> Any:
    """Convert query parameter string to appropriate type"""
    # Convert boolean strings
    if value.lower() == "true":
        return True
    elif value.lower() == "false":
        return False
    
    # Try to convert to int
    try:
        return int(value)
    except ValueError:
        pass
    
    # Try to convert to float
    try:
        return float(value)
    except ValueError:
        pass
    
    # Return as string if no conversion possible
    return value

# Middleware to add CORS headers to all responses
@app.middleware("http")
async def add_cors_headers(request: Request, call_next):
    response = await call_next(request)
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, PUT, DELETE, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Root endpoint
@app.get("/")
async def root():
    return {
        "message": "FastAPI MongoDB Dynamic API",
        "version": "1.0.0",
        "endpoints": {
            "GET_ALL": "/{entity}",
            "GET_BY_ID": "/{entity}/id/{item_id}",
            "SAVE_NEW": "/{entity}",
            "UPDATE": "/{entity}/{item_id}",
            "GET_FILTERED": "/{entity}/filter",
            "DELETE_BY_ID": "/{entity}/{item_id}"
        }
    }

# 1. GET_ALL: Fetch all documents from the specified entity/collection
@app.get("/{entity}")
async def get_all(entity: str):
    """Fetch all documents from the specified collection"""
    try:
        collection = db[entity]
        documents = list(collection.find())
        serialized_docs = [serialize_doc(doc) for doc in documents]
        return {
            "entity": entity,
            "count": len(serialized_docs),
            "data": serialized_docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching documents: {str(e)}")

# 2. GET_BY_ID: Fetch a single document by its MongoDB ObjectId
@app.get("/{entity}/id/{item_id}")
async def get_by_id(entity: str, item_id: str):
    """Fetch a single document by its ObjectId"""
    try:
        collection = db[entity]
        
        # Validate ObjectId format
        if not ObjectId.is_valid(item_id):
            raise HTTPException(status_code=400, detail="Invalid ObjectId format")
        
        document = collection.find_one({"_id": ObjectId(item_id)})
        
        if document is None:
            raise HTTPException(status_code=404, detail=f"Document with id {item_id} not found")
        
        return {
            "entity": entity,
            "data": serialize_doc(document)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching document: {str(e)}")

# 3. SAVE_NEW: Save a new JSON object exactly as received in the request body
@app.post("/{entity}")
async def save_new(entity: str, document: Dict[str, Any]):
    """Save a new document to the specified collection"""
    try:
        collection = db[entity]
        
        # Insert the document exactly as received
        result = collection.insert_one(document)
        
        # Fetch the saved document to return it with the generated _id
        saved_document = collection.find_one({"_id": result.inserted_id})
        
        return {
            "entity": entity,
            "message": "Document saved successfully",
            "data": serialize_doc(saved_document)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error saving document: {str(e)}")

# 4. UPDATE: Update an existing document by its ObjectId
@app.put("/{entity}/{item_id}")
async def update_document(entity: str, item_id: str, updates: Dict[str, Any]):
    """Update an existing document by its ObjectId"""
    try:
        collection = db[entity]
        
        # Validate ObjectId format
        if not ObjectId.is_valid(item_id):
            raise HTTPException(status_code=400, detail="Invalid ObjectId format")
        
        # Check if document exists
        existing_doc = collection.find_one({"_id": ObjectId(item_id)})
        if existing_doc is None:
            raise HTTPException(status_code=404, detail=f"Document with id {item_id} not found")
        
        # Update the document
        result = collection.update_one(
            {"_id": ObjectId(item_id)},
            {"$set": updates}
        )
        
        if result.modified_count == 0:
            raise HTTPException(status_code=400, detail="No changes were made to the document")
        
        # Fetch and return the updated document
        updated_document = collection.find_one({"_id": ObjectId(item_id)})
        
        return {
            "entity": entity,
            "message": "Document updated successfully",
            "data": serialize_doc(updated_document)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating document: {str(e)}")

# 5. GET_FILTERED: Fetch documents dynamically filtered by any query parameters
@app.get("/{entity}/filter")
async def get_filtered(entity: str, request: Request):
    """Fetch documents filtered by query parameters"""
    try:
        collection = db[entity]
        
        # Get query parameters and convert them to appropriate types
        query_params = dict(request.query_params)
        filters = {}
        
        for key, value in query_params.items():
            # Don't convert _id to ObjectId to avoid Invalid ObjectId errors
            if key == "_id":
                filters[key] = value
            else:
                filters[key] = convert_query_value(value)
        
        # Query the collection
        documents = list(collection.find(filters))
        serialized_docs = [serialize_doc(doc) for doc in documents]
        
        return {
            "entity": entity,
            "filters": filters,
            "count": len(serialized_docs),
            "data": serialized_docs
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error filtering documents: {str(e)}")

# 6. DELETE_BY_ID: Delete document by ObjectId
@app.delete("/{entity}/{item_id}")
async def delete_by_id(entity: str, item_id: str):
    """Delete a document by its ObjectId"""
    try:
        collection = db[entity]
        
        # Validate ObjectId format
        if not ObjectId.is_valid(item_id):
            raise HTTPException(status_code=400, detail="Invalid ObjectId format")
        
        # Check if document exists before deletion
        existing_doc = collection.find_one({"_id": ObjectId(item_id)})
        if existing_doc is None:
            raise HTTPException(status_code=404, detail=f"Document with id {item_id} not found")
        
        # Delete the document
        result = collection.delete_one({"_id": ObjectId(item_id)})
        
        if result.deleted_count == 0:
            raise HTTPException(status_code=500, detail="Failed to delete document")
        
        return {
            "entity": entity,
            "message": "Document deleted successfully",
            "deleted_id": item_id,
            "data": serialize_doc(existing_doc)
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error deleting document: {str(e)}")

# Health check endpoint
@app.get("/health")
async def health_check():
    """Health check endpoint"""
    try:
        # Test database connection
        client.admin.command('ping')
        return {
            "status": "healthy",
            "database": "connected",
            "message": "API is running and database is accessible"
        }
    except Exception as e:
        return JSONResponse(
            status_code=503,
            content={
                "status": "unhealthy",
                "database": "disconnected",
                "error": str(e)
            }
        )

# Startup logic for Render deployment
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
