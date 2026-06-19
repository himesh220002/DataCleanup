import torch # pyright: ignore
import torch.nn as nn
from torchvision import models

def build_efficientnet(num_classes: int, pretrained: bool = True, freeze_backbone: bool = True) -> nn.Module:
    """
    Builds an EfficientNet-B0 model with a custom classification head.
    EfficientNet provides better accuracy and efficiency compared to ResNet.
    """
    try:
        weights = models.EfficientNet_B0_Weights.DEFAULT if pretrained else None
        model = models.efficientnet_b0(weights=weights)
    except AttributeError:
        model = models.efficientnet_b0(pretrained=pretrained)

    if freeze_backbone:
        for param in model.parameters():
            param.requires_grad = False

    if num_classes != 1000:
        # EfficientNet classifier is a Sequential block, we replace the last linear layer
        in_features = getattr(model.classifier[1], "in_features")
        model.classifier[1] = nn.Linear(in_features, num_classes)

    return model
