import torch  # type: ignore
import torch.nn.functional as F  # type: ignore
from PIL import Image
import io
from torchvision import models  # type: ignore

def get_imagenet_classes():
    """Fallback utility to load standard ImageNet class names if needed."""
    try:
        from torchvision.models import ResNet50_Weights
        return ResNet50_Weights.DEFAULT.meta["categories"]
    except Exception:
        return [f"Class_{i}" for i in range(1000)]

def predict_image(image_bytes: bytes, model: torch.nn.Module, transforms, classes: list = None, device: str = "cpu"):
    """
    Runs an inference prediction on a single image.
    
    Args:
        image_bytes: Raw bytes of the uploaded image.
        model: The trained PyTorch model.
        transforms: The validation transforms pipeline.
        classes: List of class names. If None, uses ImageNet defaults.
        device: 'cpu' or 'cuda'.
        
    Returns:
        tuple: (predicted_class_name, confidence_percentage)
    """
    if classes is None:
        classes = get_imagenet_classes()

    # Load image
    image = Image.open(io.BytesIO(image_bytes)).convert('RGB')
    
    # Preprocess image
    tensor = transforms(image).unsqueeze(0).to(device)
    
    model = model.to(device)
    model.eval()
    
    with torch.no_grad():
        outputs = model(tensor)
        probabilities = F.softmax(outputs, dim=1)
        
        # Get top prediction
        top_prob, top_class_idx = torch.max(probabilities, 1)
        
        confidence = top_prob.item() * 100
        predicted_class = classes[top_class_idx.item()]
        
    return predicted_class, confidence
