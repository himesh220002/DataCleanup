import torch  # type: ignore
import torch.nn as nn  # type: ignore
import torch.optim as optim  # type: ignore
from torch.amp import autocast, GradScaler # type: ignore
import time
import copy
from typing import Dict, Any

def train_one_epoch(model: nn.Module, dataloader, criterion, optimizer, scaler, device) -> float:
    model.train()
    running_loss = 0.0
    
    for inputs, labels in dataloader:
        inputs = inputs.to(device)
        labels = labels.to(device)
        
        optimizer.zero_grad()
        
        # Fixed PyTorch 2.x autocast syntax
        with autocast(device_type=device, enabled=(device == "cuda")):
            outputs = model(inputs)
            loss = criterion(outputs, labels)
            
        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()
        
        running_loss += loss.item() * inputs.size(0)
        
    epoch_loss = running_loss / len(dataloader.dataset)
    return epoch_loss

def evaluate(model: nn.Module, dataloader, criterion, device) -> float:
    model.eval()
    running_loss = 0.0
    
    with torch.no_grad():
        for inputs, labels in dataloader:
            inputs = inputs.to(device)
            labels = labels.to(device)
            
            with autocast(device_type=device, enabled=(device == "cuda")):
                outputs = model(inputs)
                loss = criterion(outputs, labels)
            
            running_loss += loss.item() * inputs.size(0)
            
    epoch_loss = running_loss / len(dataloader.dataset)
    return epoch_loss

def train_model(
    model: nn.Module, 
    train_loader, 
    val_loader, 
    num_epochs: int,
    device: str = "cpu",
    learning_rate: float = 0.001,
    patience: int = 5,
    loss_function: str = "cross_entropy"
) -> Dict[str, Any]:
    """
    Orchestrates the training process with AMP, Early Stopping and LR Scheduling.
    """
    model = model.to(device)
    
    if loss_function == "focal_loss":
        from .losses import FocalLoss
        criterion = FocalLoss()
    else:
        criterion = nn.CrossEntropyLoss()
    
    # Only train parameters that require gradients (handles transfer learning)
    optimizer = optim.Adam(filter(lambda p: p.requires_grad, model.parameters()), lr=learning_rate)
    
    # Learning Rate Scheduler & AMP Scaler
    scheduler = optim.lr_scheduler.ReduceLROnPlateau(optimizer, mode='min', factor=0.1, patience=2)
    scaler = GradScaler(device, enabled=(device == "cuda"))
    
    history = {"train_loss": [], "val_loss": [], "learning_rates": []}
    
    best_val_loss = float('inf')
    best_model_wts = copy.deepcopy(model.state_dict())
    epochs_no_improve = 0
    
    for epoch in range(num_epochs):
        start_time = time.time()
        
        train_loss = train_one_epoch(model, train_loader, criterion, optimizer, scaler, device)
        val_loss = evaluate(model, val_loader, criterion, device)
        
        current_lr = optimizer.param_groups[0]['lr']
        history["train_loss"].append(train_loss)
        history["val_loss"].append(val_loss)
        history["learning_rates"].append(current_lr)
        
        print(f"Epoch {epoch+1}/{num_epochs} - Time: {time.time()-start_time:.2f}s")
        print(f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | LR: {current_lr:.6f}")
        
        # Scheduler step
        scheduler.step(val_loss)
        
        # Early Stopping
        if val_loss < best_val_loss:
            best_val_loss = val_loss
            best_model_wts = copy.deepcopy(model.state_dict())
            epochs_no_improve = 0
        else:
            epochs_no_improve += 1
            if epochs_no_improve >= patience:
                print(f"Early stopping triggered after {epoch+1} epochs.")
                break
                
    # Load best model weights
    model.load_state_dict(best_model_wts)
    return history
