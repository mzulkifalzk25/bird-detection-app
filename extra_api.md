# Bird App Backend: Extra API Endpoints

## 3. Bird Identification & Information Module
---
**Base URL:** `/api/birds/`

### a) Bird Identification

#### **POST /api/birds/identify/**
- **Purpose:** Identify a bird from an image or sound (audio) file.
- **Request:** `multipart/form-data`
  - For image:
    - `image` (file, required)
    - `latitude` (float, optional)
    - `longitude` (float, optional)
    - `location_name` (string, optional)
  - For sound:
    - `sound` (file, required)
    - `latitude` (float, optional)
    - `longitude` (float, optional)
    - `week` (int, optional, 1-48)
- **Response:**
  ```json
  {
    "predicted_species": "Common Raven",
    "confidence": 0.92,
    "image_url": "/media/bird_identifications/yourfile.jpg",
    "sound_url": "/media/bird_sounds/yourfile.mp3",
    "identification": { ... }
  }
  ```
- **Notes:**
  - For images, uses a HuggingFace image classifier.
  - For sound, uses BirdNET TFLite model for inference.

---

### b) Image Enhancement

#### **POST /api/birds/enhance/**
- **Purpose:** Enhance a bird image using AI.
- **Request:** `multipart/form-data`
  - `image` (file, required)
- **Response:**
  ```json
  {
    "enhanced_image_url": "https://example.com/enhanced_image.jpg"
  }
  ```

---

### c) Bird Information

#### **GET /api/birds/details/<id>/**
- **Purpose:** Get detailed information about a specific bird.
- **Response:**
  ```json
  {
    "id": 1,
    "name": "CROW",
    "scientific_name": "CROW",
    "description": "Automatically identified bird",
    "image_url": "",
    "rarity": "",
    ...
  }
  ```

#### **GET /api/birds/list/**
- **Purpose:** List all birds, with optional search and filter.
- **Query Params:**
  - `search` (string, optional)
  - `rarity` (string, optional)
- **Response:** List of birds.

#### **GET /api/birds/identifications/**
- **Purpose:** Get all identifications made by the user.
- **Response:** List of identification records.

---

### d) Bird Category & Feeder APIs

#### **GET /api/birds/common-feeder/**
- **Purpose:** Get a list of common feeder birds.
- **Response:** List of birds with feeder behavior.

#### **GET /api/birds/by-category/?category=Songbirds**
- **Purpose:** Get birds filtered by category.
- **Query Params:**
  - `category` (string, required)
- **Response:** List of birds in the specified category.

---

### e) Bird Brain AI (Conversational & Location)

#### **POST /api/birds/birdbrain/ask/**
- **Purpose:** Ask the AI assistant about bird identification.
- **Request:** `application/json`
  - `date` (string, optional)
  - `location` (string, optional)
  - `color` (string, optional)
  - `size` (string, optional)
  - `behavior` (string, optional)
- **Response:** AI-generated identification and details.

#### **GET /api/birds/birdbrain/search-location/?location=New York**
- **Purpose:** Search for birds by location.
- **Query Params:**
  - `location` (string, required)
- **Response:** List of locations and coordinates.

#### **POST /api/birds/birdbrain/chat/**
- **Purpose:** Chat with the AI about birds.
- **Request:** `application/json`
  - `message` (string, required)
- **Response:** AI chat response.

---

## 4. User-Specific Bird Data

### a) User Bird Identifications

#### **GET /api/birds/identifications/**
- **Purpose:** Get all bird identifications made by the user.
- **Response:** List of identification records.

---

## 5. Summary Table

| Endpoint                                      | Method | Purpose/Description                                 | Payload/Params                | Response Example/Notes         |
|------------------------------------------------|--------|-----------------------------------------------------|-------------------------------|-------------------------------|
| /api/birds/identify/                           | POST   | Identify bird from image or sound                   | image/sound, lat, lon, week   | predicted_species, confidence |
| /api/birds/enhance/                            | POST   | Enhance bird image                                  | image                         | enhanced_image_url            |
| /api/birds/details/<id>/                       | GET    | Get bird details                                    | -                             | bird details                  |
| /api/birds/list/                               | GET    | List/search/filter birds                            | search, rarity                | list of birds                 |
| /api/birds/identifications/                    | GET    | User's bird identifications                         | -                             | list of identifications       |
| /api/birds/common-feeder/                      | GET    | List of common feeder birds                         | -                             | list of birds                 |
| /api/birds/by-category/?category=Songbirds     | GET    | Birds by category                                   | category                      | list of birds                 |
| /api/birds/birdbrain/ask/                      | POST   | Ask AI for bird identification                      | date, location, color, etc.   | AI response                   |
| /api/birds/birdbrain/search-location/          | GET    | Search birds by location                            | location                      | locations                     |
| /api/birds/birdbrain/chat/                     | POST   | Chat with AI about birds                            | message                       | AI chat response              |

---

## 6. Why Were These APIs Created?

- **Bird Identification (image/sound):** To allow users to identify birds using photos or audio recordings, leveraging state-of-the-art ML models.
- **Image Enhancement:** To improve the quality of bird images before identification or sharing.
- **Bird Information & Search:** To provide users with a searchable, filterable database of birds.
- **Category & Feeder APIs:** To support birdwatchers and enthusiasts in finding birds by category or feeder behavior.
- **Bird Brain AI:** To offer conversational and location-based birding assistance using AI.
- **User Identifications:** To let users track and review their own bird identifications.
