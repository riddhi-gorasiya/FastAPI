from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    model_config =SettingsConfigDict(env_file=".env", extra="ignore")

    DB_CONNECTION:str
    SECRET_KEY:str
    ALGORITHM:str
    EXP_TIME:int
    REFRESH_EXP_TIME:int = 7  # refresh token expiry in days

    # Mail (Gmail requires a 16-char App Password, not your normal password)
    MAIL_USERNAME:str = ""
    MAIL_PASSWORD:str = ""
    MAIL_FROM:str = ""
    MAIL_PORT:int = 587
    MAIL_SERVER:str = "smtp.gmail.com"
    MAIL_FROM_NAME:str = "Todo List"

settings = Settings()
