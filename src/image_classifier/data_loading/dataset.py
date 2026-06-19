import os
import torch  # type: ignore
from torchvision import datasets  # type: ignore
from torch.utils.data import DataLoader, Dataset  # type: ignore
from typing import Tuple, Optional, Dict
from .transforms import get_training_transforms, get_validation_transforms  # type: ignore

class ImageClassifierDataset:
    """
    Wrapper class to manage PyTorch ImageFolder datasets and DataLoaders.
    It expects the data directory to be structured like:
    root_dir/
      train/
        class_1/
        class_2/
      val/
        class_1/
        class_2/
    """
    def __init__(self, data_dir: str, image_size: int = 224):
        self.data_dir = data_dir
        self.image_size = image_size
        self.train_dir = os.path.join(data_dir, 'train')
        self.val_dir = os.path.join(data_dir, 'val')
        
        # We will initialize these lazily or via setup()
        self.train_dataset: Optional[Dataset] = None
        self.val_dataset: Optional[Dataset] = None
        self.class_to_idx: Dict[str, int] = {}
        self.classes: list[str] = []

    def setup(self):
        """Initializes datasets and checks paths."""
        if not os.path.exists(self.train_dir):
            raise FileNotFoundError(f"Training directory not found at {self.train_dir}")
        if not os.path.exists(self.val_dir):
            raise FileNotFoundError(f"Validation directory not found at {self.val_dir}")

        train_transforms = get_training_transforms(self.image_size)
        val_transforms = get_validation_transforms(self.image_size)

        self.train_dataset = datasets.ImageFolder(self.train_dir, transform=train_transforms)
        self.val_dataset = datasets.ImageFolder(self.val_dir, transform=val_transforms)
        
        self.class_to_idx = self.train_dataset.class_to_idx
        self.classes = self.train_dataset.classes

    def get_dataloaders(self, batch_size: int = 32, num_workers: int = 4) -> Tuple[DataLoader, DataLoader]:
        """
        Returns (train_loader, val_loader).
        Ensures datasets are setup before creating loaders.
        """
        if self.train_dataset is None or self.val_dataset is None:
            self.setup()

        # Disable multiprocessing (num_workers=0) on windows or standard streamlit environments
        # unless specifically needed, to prevent pickling issues. We'll default to 0 for safety in Streamlit.
        safe_workers = 0 if os.name == 'nt' or os.getenv('STREAMLIT_RUNTIME') else num_workers

        train_loader = DataLoader(
            self.train_dataset,
            batch_size=batch_size,
            shuffle=True,
            num_workers=safe_workers,
            pin_memory=True if torch.cuda.is_available() else False
        )
        
        val_loader = DataLoader(
            self.val_dataset,
            batch_size=batch_size,
            shuffle=False, # No need to shuffle validation
            num_workers=safe_workers,
            pin_memory=True if torch.cuda.is_available() else False
        )
        
        return train_loader, val_loader

def get_dataloaders(data_dir: str, batch_size: int = 32, image_size: int = 224, num_workers: int = 0) -> Tuple[DataLoader, DataLoader, list[str]]:
    """
    Convenience function to quickly get dataloaders and class names.
    """
    dataset_manager = ImageClassifierDataset(data_dir, image_size)
    train_loader, val_loader = dataset_manager.get_dataloaders(batch_size, num_workers)
    return train_loader, val_loader, dataset_manager.classes
