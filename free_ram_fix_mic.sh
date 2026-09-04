#!/bin/bash
# Quick RAM cleanup to fix microphone detection

echo "🧹 Freeing RAM for microphone access..."

# Stop memory hogs
pkill -f android-studio
docker stop supabase-kong autogpt_platform-cla oasis 2>/dev/null

# Clear cache
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches > /dev/null

# Restart audio
systemctl --user restart pipewire pipewire-pulse 2>/dev/null

# Check result
free -h | grep Mem
echo ""
echo "✅ RAM freed. Now:"
echo "1. Close ALL Chrome windows"
echo "2. Restart Chrome"
echo "3. Go to chrome://settings/content/microphone"
echo "4. Microphone should now appear in the list"
