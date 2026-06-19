import torchvision.transforms as transforms  # type: ignore

def get_training_transforms(image_size: int = 224) -> transforms.Compose:
    """
    Returns the standard data augmentation and normalization pipeline for training.
    Uses common ImageNet standards.
    """
    return transforms.Compose([
        transforms.RandomResizedCrop(image_size),
        transforms.RandomHorizontalFlip(p=0.5),
        transforms.ColorJitter(brightness=0.2, contrast=0.2, saturation=0.2, hue=0.1),
        transforms.RandomRotation(degrees=15),
        transforms.ToTensor(),
        # Standard ImageNet Normalization
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

def get_validation_transforms(image_size: int = 224) -> transforms.Compose:
    """
    Returns the standard preprocessing pipeline for validation and inference.
    Does NOT include random augmentations, only deterministic cropping.
    """
    # Usually we resize slightly larger than crop size, e.g., 256 for a 224 crop
    resize_size = int((256 / 224) * image_size)
    return transforms.Compose([
        transforms.Resize(resize_size),
        transforms.CenterCrop(image_size),
        transforms.ToTensor(),
        # Standard ImageNet Normalization
        transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225]),
    ])

def get_inverse_transforms() -> transforms.Compose:
    """
    Returns a pipeline to un-normalize a tensor back into a displayable PIL image.
    Useful for visualizing the dataset batches in the Streamlit UI.
    """
    return transforms.Compose([
        transforms.Normalize(
            mean=[-0.485/0.229, -0.456/0.224, -0.406/0.225],
            std=[1/0.229, 1/0.224, 1/0.225]
        ),
        transforms.ToPILImage()
    ])
