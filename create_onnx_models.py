"""Create simple ONNX models for Unity Sentis"""

import torch
import torch.nn as nn
from pathlib import Path


class SimpleAI(nn.Module):
    def __init__(self):
        super().__init__()
        self.fc1 = nn.Linear(8, 16)
        self.fc2 = nn.Linear(16, 8)
        self.fc3 = nn.Linear(8, 3)
    
    def forward(self, x):
        x = torch.relu(self.fc1(x))
        x = torch.relu(self.fc2(x))
        return torch.softmax(self.fc3(x), dim=1)


def main():
    print("Creating ONNX models for Unity Sentis...\n")
    
    models_dir = Path("UnityGame/Assets/Models")
    models_dir.mkdir(parents=True, exist_ok=True)
    
    # Enemy AI model
    print("1. Creating EnemyAI.onnx...")
    model = SimpleAI()
    dummy_input = torch.randn(1, 8)
    torch.onnx.export(
        model, dummy_input,
        models_dir / "EnemyAI.onnx",
        input_names=['input'],
        output_names=['output'],
        dynamic_axes={'input': {0: 'batch'}, 'output': {0: 'batch'}}
    )
    print(f"   Saved: {models_dir / 'EnemyAI.onnx'}\n")
    
    # Difficulty AI model
    print("2. Creating DifficultyAI.onnx...")
    diff_model = nn.Sequential(
        nn.Linear(4, 8),
        nn.ReLU(),
        nn.Linear(8, 1),
        nn.Sigmoid()
    )
    dummy_input = torch.randn(1, 4)
    torch.onnx.export(
        diff_model, dummy_input,
        models_dir / "DifficultyAI.onnx",
        input_names=['metrics'],
        output_names=['difficulty']
    )
    print(f"   Saved: {models_dir / 'DifficultyAI.onnx'}\n")
    
    print("Done! Import these .onnx files to Unity as ModelAssets")


if __name__ == '__main__':
    main()
