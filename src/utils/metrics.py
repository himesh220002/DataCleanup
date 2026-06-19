import torch # type: ignore
import numpy as np # type: ignore
from sklearn.metrics import classification_report, confusion_matrix # type: ignore
import matplotlib.pyplot as plt # type: ignore
import seaborn as sns # type: ignore
from typing import List, Tuple

def get_predictions(model: torch.nn.Module, dataloader, device: str) -> Tuple[List[int], List[int]]:
    """Runs inference on a dataloader to collect true and predicted labels."""
    model.eval()
    y_true = []
    y_pred = []
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            outputs = model(inputs)
            _, preds = torch.max(outputs, 1)
            y_true.extend(labels.cpu().numpy())
            y_pred.extend(preds.cpu().numpy())
    return y_true, y_pred

def plot_confusion_matrix(y_true: List[int], y_pred: List[int], classes: List[str]):
    """Plots a confusion matrix using Seaborn heatmap."""
    cm = confusion_matrix(y_true, y_pred)
    fig, ax = plt.subplots(figsize=(8, 6))
    # Make background transparent for better UI integration
    fig.patch.set_alpha(0.0)
    ax.patch.set_alpha(0.0)
    
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=classes, yticklabels=classes, ax=ax) # type: ignore
    plt.ylabel('True Label', color='white')
    plt.xlabel('Predicted Label', color='white')
    plt.title('Validation Confusion Matrix', color='white')
    
    # Change tick colors for dark mode
    ax.tick_params(colors='white')
    return fig

def generate_classification_report(y_true: List[int], y_pred: List[int], classes: List[str]) -> str:
    """Generates a text classification report using Scikit-Learn."""
    return str(classification_report(y_true, y_pred, target_names=classes))
