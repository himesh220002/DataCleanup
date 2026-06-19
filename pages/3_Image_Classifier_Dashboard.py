import streamlit as st
import os
import sys

# Ensure imports work from the root directory
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'src')))

st.set_page_config(page_title="Image Classifier", layout="wide")

st.title("🖼️ Image Classifier System")
st.markdown("An automated, scalable pipeline for classifying images using state-of-the-art CNNs.")

# --- Architecture Overview ---
with st.expander("📖 System Context & Architecture"):
    st.markdown("""
    **Core Pipeline:**
    1. **Data Ingestion**: Raw images are loaded and decoded.
    2. **Preprocessing**: Images are resized, normalized, and augmented.
    3. **Inference Engine**: A Deep Learning model (e.g., PyTorch ResNet) processes the tensor.
    4. **Prediction**: The output logits are mapped to class probabilities.
    """)

# --- Main Dashboard ---
tab1, tab2, tab3 = st.tabs(["📂 Data Ingestion", "⚙️ Model Training", "🧠 Model Inference"])

with tab1:
    st.header("Data Ingestion & Augmentation")
    st.markdown("Point the pipeline to a local directory structured with `train` and `val` folders containing class subfolders.")
    
    data_dir = st.text_input("Dataset Directory Path", value="data/raw/images")
    
    if st.button("Load Dataset & Visualize Batch"):
        from src.image_classifier.data_loading import get_dataloaders  # type: ignore
        from src.image_classifier.data_loading.transforms import get_inverse_transforms  # type: ignore
        import torch  # type: ignore
        
        try:
            with st.spinner("Setting up PyTorch DataLoaders..."):
                train_loader, val_loader, classes = get_dataloaders(data_dir, batch_size=8, num_workers=0)
                st.success(f"Successfully loaded dataset with {len(classes)} classes: {', '.join(classes)}")
                
                # Fetch a single batch
                images, labels = next(iter(train_loader))
                
                st.subheader("Training Batch Preview (Augmented)")
                inv_trans = get_inverse_transforms()
                
                cols = st.columns(4)
                for idx, (img_tensor, label_idx) in enumerate(zip(images[:8], labels[:8])):
                    col = cols[idx % 4]
                    try:
                        # Un-normalize the tensor for viewing
                        display_img = inv_trans(img_tensor)
                        col.image(display_img, caption=f"Class: {classes[label_idx]}", use_container_width=True)
                    except Exception as e:
                        col.error(f"Error viewing image: {e}")
                        
        except FileNotFoundError as e:
            st.error(f"Directory Error: {e}. Please ensure the path exists and contains 'train' and 'val' subdirectories.")
        except Exception as e:
            st.error(f"Failed to load dataset: {e}")

with tab2:
    st.header("Model Training Pipeline")
    st.markdown("Kick off a training run using Transfer Learning on a pre-trained ResNet50.")
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        num_epochs = st.number_input("Number of Epochs", min_value=1, max_value=50, value=1)
        learning_rate = st.selectbox("Learning Rate", [0.001, 0.0001, 0.00001], index=0)
        patience = st.number_input("Early Stopping Patience", min_value=1, max_value=10, value=3)
    
    with col_t2:
        device_opt = st.radio("Compute Device", ["cpu", "cuda"])
        model_arch = st.selectbox("Model Architecture", ["ResNet50", "EfficientNet-B0", "VGG16"], index=0)
        loss_fn = st.selectbox("Loss Function", ["cross_entropy", "focal_loss"], index=0)
    
    if st.button("🚀 Start Training Run"):
        from src.image_classifier.models.resnet import build_resnet50  # type: ignore
        from src.image_classifier.models.efficientnet import build_efficientnet # type: ignore
        from src.image_classifier.training.engine import train_model  # type: ignore
        from src.image_classifier.data_loading import get_dataloaders  # type: ignore
        
        try:
            with st.spinner("Preparing model and dataloaders..."):
                train_loader, val_loader, classes = get_dataloaders(data_dir, batch_size=8, num_workers=0)
                
                if model_arch == "ResNet50":
                    model = build_resnet50(num_classes=len(classes), pretrained=True, freeze_backbone=True)
                elif model_arch == "VGG16":
                    from src.image_classifier.models.vgg import build_vgg16 # type: ignore
                    model = build_vgg16(num_classes=len(classes), pretrained=True, freeze_backbone=True)
                else:
                    model = build_efficientnet(num_classes=len(classes), pretrained=True, freeze_backbone=True)
                
            st.info(f"Starting training on {device_opt} for {num_epochs} epochs...")
            
            with st.spinner("Training in progress (check terminal for epoch logs)..."):
                history = train_model(
                    model=model,
                    train_loader=train_loader,
                    val_loader=val_loader,
                    num_epochs=num_epochs,
                    device=device_opt,
                    learning_rate=learning_rate,
                    patience=patience,
                    loss_function=loss_fn
                )
            
            with st.spinner("Saving model weights..."):
                import os, json
                import torch # type: ignore
                os.makedirs("models/saved", exist_ok=True)
                # Save model weights
                torch.save(model.state_dict(), "models/saved/custom_model.pth")
                # Save class list
                with open("models/saved/classes.json", "w") as f:
                    json.dump({"classes": classes, "arch": model_arch}, f)
            
            st.success("Training completed and model saved successfully!")
            
            st.subheader("Training Loss Curve")
            import pandas as pd
            chart_data = pd.DataFrame({
                "Train Loss": history["train_loss"],
                "Val Loss": history["val_loss"]
            })
            st.line_chart(chart_data)
            
            from src.utils.metrics import get_predictions, plot_confusion_matrix, generate_classification_report # type: ignore
            
            with st.spinner("Generating validation metrics using Scikit-learn & Seaborn..."):
                y_true, y_pred = get_predictions(model, val_loader, device_opt)
                
                col_m1, col_m2 = st.columns([1.5, 1])
                with col_m1:
                    st.subheader("Validation Confusion Matrix")
                    fig = plot_confusion_matrix(y_true, y_pred, classes)
                    st.pyplot(fig)
                
                with col_m2:
                    st.subheader("Classification Report")
                    report = generate_classification_report(y_true, y_pred, classes)
                    st.text(report)
            
            with st.expander("Raw History Data"):
                st.json(history)
            
        except Exception as e:
            st.error(f"Training failed: {e}")

# Initialize monitoring session state
if 'total_inferences' not in st.session_state:
    st.session_state.total_inferences = 0

with tab3:
    col1, col2 = st.columns([1, 2])
    with col1:
        st.header("Upload Data")
        uploaded_file = st.file_uploader("Upload an Image to Classify", type=["jpg", "png", "jpeg"])
        
        if uploaded_file is not None:
            st.success("Image uploaded successfully!")
            st.image(uploaded_file, caption="Input Image", use_container_width=True)
        else:
            st.info("Awaiting image upload...")

    with col2:
        st.header("Classification Results")
        if uploaded_file is not None:
            from src.image_classifier.inference import predict_image  # type: ignore
            from src.image_classifier.models.resnet import build_resnet50  # type: ignore
            from src.image_classifier.data_loading.transforms import get_validation_transforms  # type: ignore
            import torch  # type: ignore
            
            with st.spinner("Running Inference Pipeline..."):
                try:
                    import os, json
                    val_transforms = get_validation_transforms()
                    
                    # Check if custom trained model exists
                    if os.path.exists("models/saved/custom_model.pth") and os.path.exists("models/saved/classes.json"):
                        with open("models/saved/classes.json", "r") as f:
                            saved_data = json.load(f)
                            
                        # Handle new dictionary format or old list format
                        if isinstance(saved_data, dict):
                            custom_classes = saved_data.get("classes", [])
                            arch = saved_data.get("arch", "ResNet50")
                        else:
                            custom_classes = saved_data
                            arch = "ResNet50"
                        
                        if arch == "ResNet50":
                            model = build_resnet50(num_classes=len(custom_classes), pretrained=False, freeze_backbone=False)
                        elif arch == "VGG16":
                            from src.image_classifier.models.vgg import build_vgg16 # type: ignore
                            model = build_vgg16(num_classes=len(custom_classes), pretrained=False, freeze_backbone=False)
                        else:
                            from src.image_classifier.models.efficientnet import build_efficientnet # type: ignore
                            model = build_efficientnet(num_classes=len(custom_classes), pretrained=False, freeze_backbone=False)
                            
                        model.load_state_dict(torch.load("models/saved/custom_model.pth", map_location="cpu", weights_only=True))
                        classes = custom_classes
                        st.info(f"Using custom trained {arch} model!")
                    else:
                        # Fallback to base ImageNet model
                        model = build_resnet50(num_classes=1000, pretrained=True, freeze_backbone=True)
                        classes = None
                        st.info("Using base ImageNet model (no custom training found).")
                    
                    image_bytes = uploaded_file.getvalue()
                    
                    # Run inference
                    pred_class, conf = predict_image(image_bytes, model, val_transforms, classes=classes, device="cpu")
                    
                    # Update monitoring metric
                    st.session_state.total_inferences += 1
                    
                    st.metric(label="Predicted Class", value=str(pred_class).capitalize())
                    st.metric(label="Confidence", value=f"{conf:.2f}%")
                    
                    if conf > 80:
                        st.success("High confidence prediction!")
                    elif conf > 50:
                        st.warning("Medium confidence prediction.")
                    else:
                        st.error("Low confidence. Model is uncertain.")
                        
                except Exception as e:
                    st.error(f"Inference Error: {e}")
        else:
            st.write("Upload an image on the left to see predictions here.")

# --- Monitoring Placeholder ---
st.divider()
st.header("📊 Model Monitoring")
col_m1, col_m2, col_m3 = st.columns(3)
col_m1.metric(label="Total Inferences", value=str(st.session_state.total_inferences), delta="Tracking current session")
col_m2.metric(label="Average Latency", value="-- ms")
col_m3.metric(label="Model Accuracy (Val)", value="-- %")
