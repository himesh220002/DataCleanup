import torch  # type: ignore
import torch.nn as nn  # type: ignore
from torchvision import models  # type: ignore

def build_resnet50(num_classes: int, pretrained: bool = True, freeze_backbone: bool = True) -> nn.Module:
    """
    Builds a ResNet50 model with a custom classification head.
    
    Args:
        num_classes (int): Number of output classes.
        pretrained (bool): Whether to use ImageNet pre-trained weights.
        freeze_backbone (bool): Whether to freeze the feature extraction layers 
                                (Transfer Learning). Speeds up CPU training.
    """
    # Load the model
    # Using the newer weights enum if available, otherwise fallback
    try:
        weights = models.ResNet50_Weights.DEFAULT if pretrained else None
        model = models.resnet50(weights=weights)
    except AttributeError:
        model = models.resnet50(pretrained=pretrained)

    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    # Replace the final fully connected layer only if fine-tuning for custom classes
    if num_classes != 1000:
        num_ftrs = model.fc.in_features
        # The new layer will have requires_grad=True by default
        model.fc = nn.Linear(num_ftrs, num_classes)

    return model
