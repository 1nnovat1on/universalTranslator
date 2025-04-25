@echo off
REM Batch script to:
REM 1. Create a Python virtual environment ('venv') if it doesn't exist.
REM 2. Activate the virtual environment.
REM 3. Install packages from 'requirements.txt'.

REM Set the names
set VENV_DIR=venv
set REQS_FILE=requirements.txt

REM === Step 1 & 2: Check and Create Virtual Environment ===

REM Check if the venv directory exists
IF NOT EXIST "%VENV_DIR%\" (
    echo Virtual environment '%VENV_DIR%' not found. Creating it now...
    REM Try to create the virtual environment using python
    python -m venv %VENV_DIR%

    REM Check if the venv creation was successful (basic check: does the activate script exist?)
    IF NOT EXIST "%VENV_DIR%\Scripts\activate.bat" (
        echo Failed to create the virtual environment. Make sure Python is installed and in your PATH.
        pause
        exit /b 1
    )
    echo Virtual environment created successfully.
) ELSE (
    echo Virtual environment '%VENV_DIR%' already exists.
)

REM === Step 3: Check for Requirements File ===

REM Check if the requirements file exists
IF NOT EXIST "%REQS_FILE%" (
    echo Error: Requirements file '%REQS_FILE%' not found in the current directory.
    echo Please ensure 'requirements.txt' is present before running this script.
    pause
    exit /b 1
)

REM === Step 4 & 5: Activate Venv and Install Requirements ===

echo Activating virtual environment and installing requirements from %REQS_FILE%...

REM Activate the venv and run pip install in the same command context using 'call'
call "%VENV_DIR%\Scripts\activate.bat" && pip install -r "%REQS_FILE%"

REM Check the error level from the pip install command
IF %ERRORLEVEL% NEQ 0 (
    echo An error occurred during pip install. Please check the output above.
) ELSE (
    echo Requirements installed successfully.
)

REM === Step 6: Pause and Exit ===

echo.
echo Script finished. Press any key to close this window.
pause > nul

REM Exit with the final error level (0 for success, non-zero for failure)
exit /b %ERRORLEVEL%
