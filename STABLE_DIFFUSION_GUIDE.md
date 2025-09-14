# 🎨 ULTRON Agent - Stable Diffusion Integration Guide

## 📋 Overview

This integration adds comprehensive Stable Diffusion support to the ULTRON Agent, allowing users to generate high-quality AI images through multiple interfaces:

1. **🤖 Text Commands** - Natural language commands through the main ULTRON interface
2. **🎮 Dedicated GUI** - Advanced Stable Diffusion Studio interface
3. **📓 Colab Notebook** - Cloud-based GPU processing via Google Colab
4. **🌐 API Endpoints** - RESTful API for external integrations

## 🚀 Quick Start

### Method 1: Text Commands (Easiest)
Simply type commands in the ULTRON Agent interface:
```
"generate image of a cyberpunk robot"
"create realistic portrait width:1024 height:1024"
"stable diffusion fantasy castle anime style"
```

### Method 2: GUI Interface
1. Click the **🎨 Stable Diffusion Studio** button in the main ULTRON interface
2. Enter your prompt in the text area
3. Adjust parameters as needed
4. Click **Generate Images**

### Method 3: Colab Notebook (Recommended for Best Quality)
1. Upload `stable_diffusion_colab.ipynb` to Google Colab
2. Run all cells to start the server
3. Copy the provided URL (e.g., `https://abc123.ngrok.io`)
4. Add the URL as an endpoint in the GUI Settings tab

## 📁 Files Included

| File | Description | Size |
|------|-------------|------|
| `stable_diffusion_colab.ipynb` | Complete Colab notebook with Stable Diffusion server | 34.3 KB |
| `stable_diffusion_gui.py` | Advanced GUI interface for image generation | 43.3 KB |
| `tools/image_generation_tool.py` | Enhanced image generation tool | 16.1 KB |
| `pokedex_ultron_gui.py` | Updated main GUI with SD button | Updated |

## 🛠️ Features

### Enhanced Image Generation Tool
- **Multiple Backends**: Supports Colab, local servers, and fallback APIs
- **Smart Parameter Parsing**: Extract settings from natural language
- **Style Presets**: Realistic, Anime, Cyberpunk, Fantasy styles
- **Quality Control**: Fast, Balanced, High Quality presets
- **History Tracking**: Automatic generation history and management

### Advanced GUI Interface
- **Real-time Parameter Controls**: Sliders for all generation settings
- **Image Gallery**: View, save, and manage generated images
- **History Management**: Browse and reuse previous prompts
- **Endpoint Management**: Add and test multiple Stable Diffusion servers
- **Batch Operations**: Export images, import prompts, clear history

### Colab Notebook
- **Professional Setup**: Automated environment configuration
- **Multiple Models**: Support for various Stable Diffusion models
- **API Server**: Flask-based REST API for integration
- **Gradio Interface**: Interactive web interface
- **Memory Optimization**: GPU memory management and caching

## 💬 Command Examples

### Basic Generation
```
"generate image of a sunset over mountains"
"create picture of a cat in a garden"
"make image cyberpunk city at night"
```

### With Parameters
```
"generate image of a robot width:1024 height:768 steps:30"
"create realistic portrait guidance:8.5 style:realistic"
"stable diffusion fantasy dragon high quality"
```

### Style-Specific
```
"generate anime style character with blue hair"
"create cyberpunk robot with neon lights"
"make realistic landscape photograph"
```

## ⚙️ Configuration

### Local Setup (Advanced Users)
1. Install dependencies:
   ```bash
   pip install diffusers torch transformers pillow
   ```
2. Start a local Stable Diffusion server on port 8000
3. The tool will automatically detect and use it

### Colab Setup (Recommended)
1. Open Google Colab
2. Upload the `stable_diffusion_colab.ipynb` file
3. Run all cells (may take 5-10 minutes for first setup)
4. Copy the provided ngrok URL
5. In ULTRON GUI: Settings → Endpoints → Add Colab URL

### API Endpoints
When using the Colab notebook or local server:

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/health` | GET | Server health check |
| `/generate` | POST | Generate images |
| `/history` | GET | Get generation history |
| `/models` | GET | List available models |
| `/switch_model` | POST | Switch Stable Diffusion model |
| `/image/<filename>` | GET | Retrieve generated image |

## 🎯 Tips for Best Results

### Prompt Writing
- **Be Specific**: "A detailed portrait of a woman with curly red hair" vs "a woman"
- **Add Quality Tags**: "high quality", "detailed", "professional"
- **Style References**: "in the style of...", "digital art", "photorealistic"
- **Composition**: "close-up", "wide shot", "from above"

### Parameter Settings
- **Steps**: 15-20 for speed, 25-35 for quality
- **Guidance Scale**: 7-8 for balanced, 10+ for strict adherence
- **Size**: 512x512 for speed, 768x768+ for detail
- **Negative Prompts**: Always include quality negatives

### Style Presets
- **Realistic**: For photographic results
- **Anime**: For Japanese animation style
- **Cyberpunk**: For futuristic sci-fi aesthetics
- **Fantasy**: For magical and mystical themes

## 🔧 Troubleshooting

### Common Issues

**"No Stable Diffusion server available"**
- Check if Colab notebook is running
- Verify endpoint URL is correct
- Try refreshing endpoints in GUI

**"Generation timeout"**
- Reduce image size or steps
- Check internet connection
- Try a different endpoint

**"Import error" when launching GUI**
- Install missing dependencies: `pip install pillow tkinter`
- Use text commands as alternative

### Getting Help
1. Check the status indicator in the GUI
2. Use the **Setup Guide** in the Help menu
3. Review generation history for working parameters
4. Test with simple prompts first

## 📊 Performance Tips

### For Speed
- Use 512x512 resolution
- Set steps to 15-20
- Use "Fast" quality preset
- Enable auto-save to avoid GUI lag

### For Quality
- Use 768x768 or higher resolution
- Set steps to 25-35
- Use "High Quality" preset
- Add detailed prompts and negative prompts

### For Colab
- Keep the notebook active to avoid disconnection
- Use GPU runtime for best performance
- Monitor memory usage in the notebook

## 🎉 Success Metrics

After setup, you should be able to:
- ✅ Generate images through text commands
- ✅ Launch the Stable Diffusion Studio GUI
- ✅ Connect to Colab notebook endpoints
- ✅ View and manage generation history
- ✅ Export and save generated images

## 🔮 Future Enhancements

Planned features for future updates:
- **Image-to-Image**: Upload and modify existing images
- **Inpainting**: Edit specific parts of images
- **ControlNet**: Guided generation with pose/depth maps
- **Model Management**: Download and switch between models
- **Batch Processing**: Generate multiple variations
- **Integration**: Direct sharing with social media

---

**Version**: 1.0  
**Compatible with**: ULTRON Agent 3.0+  
**Last Updated**: January 2025

For technical support or feature requests, please refer to the main ULTRON Agent documentation or repository issues.