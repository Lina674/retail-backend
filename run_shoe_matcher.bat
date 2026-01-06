@echo off
REM Shoe Matcher Agent - Batch wrapper
REM Usage: run_shoe_matcher.bat <outfit_image_path>

if "%1"=="" (
    echo Usage: run_shoe_matcher.bat ^<outfit_image_path^>
    echo Example: run_shoe_matcher.bat img\download.jpg
    exit /b 1
)

python shoe_matcher_agent.py %1
