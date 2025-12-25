"""Application-level settings for the dcv CLI."""

from pydantic import Field
from pydantic_settings import BaseSettings


class AppSettings(BaseSettings):
    """Settings exposed to the dependency container."""

    app_name: str = Field(
        default="dcv",
        alias="DCV_APP_NAME",
        description="Public-facing application name reported in outputs and logs.",
    )
    default_output_dir: str = Field(
        default="dcv_output",
        alias="DCV_OUTPUT_DIR",
        description="Default output directory for converted files.",
    )


settings = AppSettings()
