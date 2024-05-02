from pydantic import BaseSettings
from typing import List

class Settings(BaseSettings):
    aws_access_key_id: str
    aws_secret_access_key: str
    aws_access_region: str
    bucket_name: str
    unoserver_url: str = "http://unoserver:2002"
    cors_origins_str: str = "http://localhost:3000" 

    @property
    def cors_origins(self) -> List[str]:
        """
        Process the cors_origins_str into a list at runtime.
        """
        return [origin.strip() for origin in self.cors_origins_str.split(",")]

    class Config:
        env_file = ".env"

settings = Settings()