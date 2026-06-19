import torch # type: ignore
import torch.nn as nn # type: ignore
from torchvision import models # type: ignore

def build_vgg16(num_classes: int, pretrained: bool = True, freeze_backbone: bool = True) -> nn.Module:
    """
    Builds a VGG16 model with a custom classification head.
    """
    try:
        weights = models.VGG16_Weights.DEFAULT if pretrained else None
        model = models.vgg16(weights=weights)
    except AttributeError:
        model = models.vgg16(pretrained=pretrained)

    if freeze_backbone:
        for param in model.features.parameters():
            param.requires_grad = False

    if num_classes != 1000:
        # VGG's classifier is a Sequential block. The final layer is index 6.
        num_ftrs = getattr(model.classifier[6], 'in_features')
        model.classifier[6] = nn.Linear(num_ftrs, num_classes)

    return model
