import pytest
import torch # type: ignore
import io
from PIL import Image
from image_classifier.models.resnet import build_resnet50 # type: ignore
from image_classifier.models.efficientnet import build_efficientnet # type: ignore
from image_classifier.models.vgg import build_vgg16 # type: ignore
from image_classifier.training.losses import FocalLoss # type: ignore
from image_classifier.data_loading.transforms import get_training_transforms, get_validation_transforms # type: ignore
from image_classifier.inference.predict import predict_image # type: ignore
from utils.metrics import get_predictions # type: ignore

def test_model_build_resnet():
    model = build_resnet50(num_classes=2, pretrained=False)
    assert isinstance(model, torch.nn.Module)
    assert getattr(model, 'fc').out_features == 2

def test_model_build_efficientnet():
    model = build_efficientnet(num_classes=2, pretrained=False)
    assert isinstance(model, torch.nn.Module)
    assert getattr(model, 'classifier')[-1].out_features == 2

def test_model_build_vgg16():
    model = build_vgg16(num_classes=2, pretrained=False)
    assert isinstance(model, torch.nn.Module)
    assert getattr(model, 'classifier')[-1].out_features == 2

def test_focal_loss():
    loss_fn = FocalLoss(alpha=1, gamma=2)
    logits = torch.tensor([[2.0, -1.0], [-1.0, 2.0]])
    targets = torch.tensor([0, 1])
    loss = loss_fn(logits, targets)
    assert isinstance(loss, torch.Tensor)
    assert loss.item() > 0

def test_transforms_exist():
    train_transforms = get_training_transforms()
    val_transforms = get_validation_transforms()
    assert train_transforms is not None
    assert val_transforms is not None

def test_inference_predict_image():
    # Create a dummy model
    model = build_efficientnet(num_classes=2, pretrained=False)
    model.eval()
    
    # Create dummy image bytes
    img = Image.new('RGB', (224, 224), color='red')
    img_byte_arr = io.BytesIO()
    img.save(img_byte_arr, format='JPEG')
    img_bytes = img_byte_arr.getvalue()
    
    val_transforms = get_validation_transforms()
    classes = ["Cat", "Elephant"]
    
    pred_class, conf = predict_image(img_bytes, model, val_transforms, classes=classes, device="cpu")
    
    assert pred_class in classes
    assert 0.0 <= conf <= 100.0

def test_metrics_get_predictions():
    # Mock dataloader yielding 1 batch
    class MockDataloader:
        def __iter__(self):
            # Batch of 2 dummy images [B, C, H, W]
            inputs = torch.randn(2, 3, 224, 224)
            labels = torch.tensor([0, 1])
            yield inputs, labels
            
    model = build_resnet50(num_classes=2, pretrained=False)
    loader = MockDataloader()
    
    y_true, y_pred = get_predictions(model, loader, device="cpu")
    
    assert len(y_true) == 2
    assert len(y_pred) == 2
    assert y_true == [0, 1]

