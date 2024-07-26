from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import pandas as pd
from scipy.sparse import csr_matrix
import implicit

# Load the parquet file and preprocess data
data = pd.read_parquet('train.parquet')
data['date'] = pd.to_datetime(data['date'])
user_item_interaction = data.groupby(['userId', 'itemId']).size().reset_index(name='interaction')

# Create a user-item interaction sparse matrix
row = user_item_interaction['userId'].astype('category').cat.codes
col = user_item_interaction['itemId'].astype('category').cat.codes
interaction_sparse = csr_matrix((user_item_interaction['interaction'], (row, col)), dtype=float)

# Mapping back to original IDs
user_mapping = dict(enumerate(user_item_interaction['userId'].astype('category').cat.categories))
item_mapping = dict(enumerate(user_item_interaction['itemId'].astype('category').cat.categories))

# Initialize and train the ALS model
model = implicit.als.AlternatingLeastSquares(factors=50, regularization=0.1, iterations=20)
model.fit(interaction_sparse)

# FastAPI app initialization
app = FastAPI()

# Pydantic models
class UserRequest(BaseModel):
    user_id: str
    num_recommendations: int = 5

class ItemRecommendation(BaseModel):
    item_id: str
    category: str

class RecommendationsResponse(BaseModel):
    user_id: str
    recommendations: List[ItemRecommendation]

# Helper function to get recommendations
def recommend_items_with_descriptions(user_id, model, interaction_sparse, data, num_recommendations=5):
    try:
        user_index = list(user_mapping.keys())[list(user_mapping.values()).index(user_id)]
    except ValueError:
        raise HTTPException(status_code=404, detail="User ID not found")

    item_indices, scores = model.recommend(user_index, interaction_sparse[user_index], N=num_recommendations)
    recommended_item_ids = [item_mapping[i] for i in item_indices]

    recommended_items = data[data['itemId'].isin(recommended_item_ids)][['itemId', 'category']].drop_duplicates().reset_index(drop=True)
    recommendations = [ItemRecommendation(item_id=row['itemId'], category=row['category']) for _, row in recommended_items.iterrows()]

    return RecommendationsResponse(user_id=user_id, recommendations=recommendations)

# API endpoint
@app.post("/recommendations/", response_model=RecommendationsResponse)
def get_recommendations(request: UserRequest):
    return recommend_items_with_descriptions(request.user_id, model, interaction_sparse, data, request.num_recommendations)
