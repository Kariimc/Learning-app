@echo off
title Log in to Hugging Face
echo.
echo   This signs this laptop in to your Hugging Face account (KariimC).
echo   It unlocks your PRO graphics-card allowance, so jobs stop being refused.
echo.
echo   1. Press a key. Your browser opens your Hugging Face tokens page.
echo   2. Make a token there, or copy one you already have. Give it WRITE access.
echo   3. Come back to this window, paste it, press Enter.
echo      Nothing appears on screen while you paste. That is normal.
echo.
pause
start "" https://huggingface.co/settings/tokens
python -m pip install --quiet --upgrade huggingface_hub
python -m huggingface_hub.commands.huggingface_cli login
echo.
echo   Checking it worked...
python -c "from huggingface_hub import HfApi; print('   Signed in as', HfApi().whoami()['name'])"
echo.
echo   If it printed your name, you are done. Tell Claude.
echo.
pause
