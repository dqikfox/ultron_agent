# Unity Cloud Code Setup for ULTRON

## Quick Setup

### 1. Dashboard Setup (5 minutes)
1. Go to [Unity Dashboard](https://dashboard.unity3d.com/)
2. Select Organization: **dqikst**
3. Select Project: **My project (1)**
4. Navigate to **Cloud Code** section
5. Click **Create Script**
6. Name: `hello-world`
7. Add parameter: `name` (type: string)
8. Copy code from `hello-world.js`
9. Click **Save** then **Publish**

### 2. Unity Editor Setup (2 minutes)
1. Open Unity project
2. Go to **Edit > Project Settings**
3. Select **Services** tab
4. Link to:
   - Organization: **dqikst**
   - Project: **My project (1)**

### 3. Add Script to Unity (1 minute)
1. Copy `CloudCodeExample.cs` to your Unity project's `Assets/Scripts/` folder
2. Attach script to a GameObject
3. Test by clicking the GameObject

## Files Created
- `hello-world.js` - Cloud Code script
- `CloudCodeExample.cs` - Unity client code
- `SETUP.md` - This file

## Test
Run Unity project and check Debug.Log for: "Hello, ULTRON. Welcome to ULTRON Cloud Code!"
