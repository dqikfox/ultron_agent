@echo off
title CMD Fix Utility
color 0A

echo ========================================
echo CMD Console Fix Utility
echo ========================================
echo.

echo Testing CMD functionality...
cmd /c "echo CMD is working" && echo SUCCESS || echo FAILED
echo.

echo Opening CMD with /K flag (keeps window open)...
start cmd /k "cd /d C:\Projects\ultron_agent && echo CMD Fixed - Ready to use"
