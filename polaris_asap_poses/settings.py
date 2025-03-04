import tomllib
from pathlib import Path

from dynaconf import Dynaconf, LazySettings
from pydantic import AnyUrl, BaseModel, Field, FilePath, ValidationError
from typeguard import typechecked


class SettingsSchema(BaseModel):
    log_level: str = Field(default="INFO")
    log_to_file: bool = Field(default=False)
    log_file: str = Field(default="./log/polaris-asap-poses.log")
    notebook_port: int = Field(..., ge=1024, le=49151)


@typechecked
def load_settings() -> LazySettings:
    """
    Load settings from settings.toml and .secrets.toml - without validating.
    """
    # Initialize settings
    # print("Loading settings...")
    settings = Dynaconf(
        settings_files=["settings.toml", ".secrets.toml"],  # Load from multiple files
        environments=True,  # Enable environments
    )
    # print("Done.")
    return settings


@typechecked
def validate_settings(settings_obj: LazySettings):
    """
    Validate the entire settings object against the schema.
    """
    # Use the pydantic model for schema validation
    # settings_obj represents the current settings object.
    # .dict() extracts all current settings as a dictionary for validation.
    try:
        # Convert settings to a dictionary and normalize keys to lowercase
        # Note that if you don't do this, you'll get errors like:
        #   database_url
        #       Field required [type=missing, input_value={
        # ...which is baffling b/c the field is clearly there.
        normalized_settings = {k.lower(): v for k, v in settings_obj.to_dict().items()}
        SettingsSchema.model_validate(normalized_settings)
        # print("Settings validated successfully.")
    except ValidationError as e:
        # print("Settings validation failed!")
        # print(e)
        raise e


@typechecked
def get_settings() -> LazySettings:
    """
    Get the settings object and validate it before returning.
    """
    s = load_settings()
    validate_settings(s)
    return s
