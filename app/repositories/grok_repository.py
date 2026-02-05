"""
Grok Prediction Repository

Handles database operations for match predictions.
"""

import asyncpg
import os
from typing import Optional, Dict, List


class GrokPredictionRepository:
    """Repository for match predictions"""

    def __init__(self):
        self.pool = None
        # Get database URL from environment
        self.database_url = os.getenv('DATABASE_URL')

    async def init_pool(self):
        """Initialize connection pool"""
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not set")
        self.pool = await asyncpg.create_pool(self.database_url)

    async def close(self):
        """Close connection pool"""
        if self.pool:
            await self.pool.close()

    async def get_pending_matches(self, limit: int = None) -> List[Dict]:
        """
        Get matches that need predictions

        Returns matches from sporttery_matches that don't have predictions yet
        """
        query = """
            SELECT
                sm.id as match_id,
                sm.league,
                sm.home_team,
                sm.away_team,
                sm.match_time,
                sm.status
            FROM sporttery_matches sm
            LEFT JOIN match_predictions mp ON sm.id = mp.match_id
            WHERE sm.status = 'pending'
              AND mp.id IS NULL
            ORDER BY sm.match_time
        """

        if limit:
            query += f" LIMIT {limit}"

        rows = await self.pool.fetch(query)

        return [dict(row) for row in rows]

    async def is_predicted(self, match_id: int) -> bool:
        """Check if match already has a prediction"""
        query = "SELECT 1 FROM match_predictions WHERE match_id = $1"
        result = await self.pool.fetchval(query, match_id)
        return result is not None

    async def save_prediction(
        self,
        match_id: int,
        league: str,
        home_team: str,
        away_team: str,
        match_time: str,
        prediction_data: str
    ) -> bool:
        """
        Save prediction to database

        Uses UPSERT to handle both new and existing predictions
        """
        query = """
            INSERT INTO match_predictions (
                match_id,
                league,
                home_team,
                away_team,
                match_time,
                prediction_data,
                prediction_date,
                updated_at
            ) VALUES ($1, $2, $3, $4, $5, $6, NOW(), NOW())
            ON CONFLICT (match_id)
            DO UPDATE SET
                prediction_data = EXCLUDED.prediction_data,
                prediction_date = EXCLUDED.prediction_date,
                updated_at = NOW()
        """

        try:
            await self.pool.execute(
                query,
                match_id,
                league,
                home_team,
                away_team,
                match_time,
                prediction_data
            )
            return True
        except Exception as e:
            print(f"Error saving prediction for match {match_id}: {e}")
            return False

    async def get_prediction(self, match_id: int) -> Optional[Dict]:
        """Get prediction for a specific match"""
        query = """
            SELECT
                id,
                match_id,
                league,
                home_team,
                away_team,
                match_time,
                prediction_data,
                prediction_date,
                created_at
            FROM match_predictions
            WHERE match_id = $1
        """

        row = await self.pool.fetchrow(query, match_id)
        return dict(row) if row else None

    async def get_all_predictions(self, limit: int = 50) -> List[Dict]:
        """Get all predictions"""
        query = """
            SELECT
                id,
                match_id,
                league,
                home_team,
                away_team,
                match_time,
                prediction_data,
                prediction_date,
                created_at
            FROM match_predictions
            ORDER BY prediction_date DESC
            LIMIT $1
        """

        rows = await self.pool.fetch(query, limit)
        return [dict(row) for row in rows]
