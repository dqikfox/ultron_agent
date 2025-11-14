# D&D Game Asset Sources - Production-Ready 3D & 2D Resources

## 🏰 3D Environment Assets

### Free Unity-Compatible Packs
- **Medieval Environment Pack** - Taverns, houses, interior props
  - https://assetstore.unity.com/packages/3d/environments/fantasy/medieval-environment-pack-240496
  
- **Stylized Fantasy Village** - Market/City scenes
  - https://assetstore.unity.com/packages/3d/environments/fantasy/stylized-fantasy-village-free-202091
  
- **Fantasy Dungeon (Bitgem)** - Cursed Cavern/Crystal Chamber
  - https://assetstore.unity.com/packages/3d/environments/dungeons/bitgem-s-fantasy-dungeon-186494

### General 3D Model Sources
- **Unity Asset Store** - https://assetstore.unity.com/
- **Sketchfab** (CC0/Attribution) - https://sketchfab.com/search?features=downloadable&sort_by=-likeCount&type=models&licenses=cc0
- **Kenney.nl** (Stylized packs) - https://kenney.nl/assets
- **Quaternius** (Low-poly RPG) - https://quaternius.com/
- **OpenGameArt** - https://opengameart.org/

## 🧍 Character & NPC Models

### Mixamo (Auto-Rigged Characters)
- **URL**: https://www.mixamo.com/
- **Features**: Humanoid characters with animations (idle, talk, walk)
- **Export**: FBX format for Unity
- **Use For**: Innkeeper, Merchant, Guard, Wizard NPCs

## 🧙 Character Portraits (2D Dialogue)

### AI-Generated Faces
- **Artbreeder** - https://www.artbreeder.com/
- **DALL·E** - https://openai.com/dall-e
- **OpenGameArt Portraits** - https://opengameart.org/art-search-advanced?keys=portrait

## 🛍️ Inventory Icons & UI

- **Game-Icons.net** (CC0 fantasy icons) - https://game-icons.net/
- **CraftPix** (UI buttons, item icons) - https://craftpix.net/freebies/
- **OpenGameArt Icons** - https://opengameart.org/

## 🧱 Textures & Materials (PBR)

- **AmbientCG** (Free PBR textures) - https://ambientcg.com/
- **Poly Haven** (8K textures, HDRIs) - https://polyhaven.com/
- **Texture Haven** - https://texturehaven.com/

## 🎲 Dice Models

- **Sketchfab D20 Search** - https://sketchfab.com/search?type=models&q=d20&features=downloadable

## 📋 Asset Integration Checklist

### Phase 1: Environment Setup
- [ ] Download Medieval Environment Pack for Tavern scene
- [ ] Download Stylized Fantasy Village for Market/Gate
- [ ] Download Fantasy Dungeon for Cavern/Chamber
- [ ] Import into Unity project

### Phase 2: Character Setup
- [ ] Create 5 NPC models in Mixamo (Innkeeper, Merchant, Guard, Hermit, Wizard)
- [ ] Download idle, talk, walk animations
- [ ] Export as FBX and import to Unity
- [ ] Generate 2D portraits for dialogue boxes

### Phase 3: UI & Items
- [ ] Download inventory icons from Game-Icons.net
- [ ] Create UI button sprites from CraftPix
- [ ] Import d20 dice model from Sketchfab
- [ ] Setup 3D dice rolling animation

### Phase 4: Polish
- [ ] Apply PBR textures to custom models
- [ ] Setup lighting and post-processing
- [ ] Add particle effects for magic/combat
- [ ] Optimize for web/mobile if needed

## 🚀 Quick Start for Web Version

Current web implementation uses:
- **Inline SVG** for scene backgrounds
- **CSS animations** for d20 dice rolling
- **Ollama AI** for NPC dialogue
- **Emoji indicators** for scenes

To upgrade to 3D Unity version:
1. Create Unity project with URP
2. Import assets from sources above
3. Port C# scripts from game design doc
4. Build WebGL for browser deployment
