# FastAPI MongoDB Dynamic API

A dynamic REST API built with FastAPI and MongoDB that allows you to work with any entity/collection without predefined models. The API accepts and stores JSON objects exactly as received.

## Features

- **Dynamic Entity Support**: Work with any collection name via URL path
- **6 Core Endpoints**: GET_ALL, GET_BY_ID, SAVE_NEW, UPDATE, GET_FILTERED, DELETE_BY_ID
- **No Schema Required**: Accept any JSON object structure
- **MongoDB Integration**: Full MongoDB Atlas support with ObjectId handling
- **CORS Enabled**: Cross-origin requests supported
- **Type Conversion**: Smart query parameter type conversion for filtering
- **Health Check**: Built-in health monitoring endpoint

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/{entity}` | Fetch all documents from collection |
| GET | `/{entity}/id/{item_id}` | Fetch single document by ObjectId |
| POST | `/{entity}` | Save new JSON object to collection |
| PUT | `/{entity}/{item_id}` | Update existing document |
| GET | `/{entity}/filter` | Filter documents by query parameters |
| DELETE | `/{entity}/{item_id}` | Delete document by ObjectId |
| GET | `/health` | Health check endpoint |

## Quick Start

### Local Development

1. **Clone the repository**
   ```bash
   git clone https://github.com/bharatha-desilva/vibe-code-generic-api-rehearsal-01.git
   cd vibe-code-generic-api-rehearsal-01
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   
   # Windows
   venv\Scripts\activate
   
   # macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the API**
   ```bash
   python main.py
   ```

   The API will be available at `http://localhost:8000`

5. **View API Documentation**
   - Swagger UI: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## Usage Examples

### 1. Save a new user
```bash
curl -X POST "http://localhost:8000/users" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "age": 30,
    "active": true
  }'
```

### 2. Get all users
```bash
curl "http://localhost:8000/users"
```

### 3. Get user by ID
```bash
curl "http://localhost:8000/users/id/507f1f77bcf86cd799439011"
```

### 4. Filter users by query parameters
```bash
# Filter by age and active status
curl "http://localhost:8000/users/filter?age=30&active=true"

# Filter by name
curl "http://localhost:8000/users/filter?name=John Doe"
```

### 5. Update a user
```bash
curl -X PUT "http://localhost:8000/users/507f1f77bcf86cd799439011" \
  -H "Content-Type: application/json" \
  -d '{
    "age": 31,
    "city": "New York"
  }'
```

### 6. Delete a user
```bash
curl -X DELETE "http://localhost:8000/users/507f1f77bcf86cd799439011"
```

## Query Parameter Type Conversion

The filter endpoint automatically converts query parameters:
- `"true"` / `"false"` → boolean
- Numeric strings → int or float
- Everything else → string
- `_id` is always treated as string to avoid ObjectId errors

## Deployment

### Deploy to Render

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Initial API setup"
   git push origin main
   ```

2. **Deploy on Render**
   - Connect your GitHub repository to Render
   - Set build command: `pip install -r requirements.txt`
   - Set start command: `python main.py`
   - Environment variables are automatically handled

3. **Environment Variables**
   - `PORT`: Automatically set by Render
   - MongoDB URI is hardcoded (consider using environment variables for production)

### Deploy to Other Platforms

The API includes startup logic that reads the `PORT` environment variable, making it compatible with:
- Heroku
- Railway
- Google Cloud Run
- AWS App Runner
- Azure Container Instances

## Database Configuration

The API connects to MongoDB Atlas with the following configuration:
- **URI**: `mongodb+srv://nuwanwp:zXi15ByhNUNFEOOD@cluster0.gjas8wj.mongodb.net/`
- **Database**: `fastapi_mongo_api`
- **Collections**: Dynamic (created on first use)

## Response Format

All endpoints return JSON responses with consistent structure:

```json
{
  "entity": "collection_name",
  "message": "Operation description",
  "count": 1,
  "data": {...}
}
```

## Error Handling

The API includes comprehensive error handling:
- **400**: Bad Request (invalid ObjectId, validation errors)
- **404**: Not Found (document doesn't exist)
- **500**: Internal Server Error (database issues)

## Health Monitoring

Check API health and database connectivity:
```bash
curl "http://localhost:8000/health"
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly
5. Submit a pull request

## License

This project is open source and available under the MIT License.
