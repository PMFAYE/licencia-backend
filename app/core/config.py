from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    # SMTP (Gmail)
    SMTP_HOST: str = "smtp.gmail.com"
    SMTP_PORT: int = 587
    SMTP_USER: str = "morfaye15@gmail.com"
    SMTP_PASSWORD: str = ""
    SMTP_FROM: str = "morfaye15@gmail.com"

    class Config:
        env_file = ".env"

settings = Settings()