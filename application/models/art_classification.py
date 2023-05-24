# -*- coding: utf-8 -*-
"""Art Classification.ipynb

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1zS1OKM640zurBlOTM0j0FtiltKPCjbfX
"""

from google.colab import drive
drive.mount('/content/drive')

!pip install numpy
!pip install pillow
!pip install --upgrade tensorflow

"""Importing Tensorflow and testing its version"""

import tensorflow as tf
print(tf.__version__)

"""Renaming train directory"""

import os
import re

# Define the path to your dataset
base_dir = '/content/drive/MyDrive/ArtClassification/train'

# Function to clean and format the new file name
def format_file_name(file_name):
    # Remove special characters and spaces except hyphen and period
    cleaned_name = re.sub(r'[^\w\s.-]', '', file_name)
    # Replace spaces with underscores
    formatted_name = cleaned_name.replace(' ', '_')
    return formatted_name

# Iterate through the subdirectories in the train directory
for class_name in os.listdir(base_dir):
    class_dir = os.path.join(base_dir, class_name)
    if os.path.isdir(class_dir):
        # Rename the files in the subdirectory
        for i, file_name in enumerate(os.listdir(class_dir)):
            _, extension = os.path.splitext(file_name)
            new_file_name = f"{class_name}_{i}{extension}"
            new_file_name = format_file_name(new_file_name)

            # Add '.jpg' extension if the file doesn't have any extension
            if not extension:
                new_file_name += '.jpg'

            old_file_path = os.path.join(class_dir, file_name)
            new_file_path = os.path.join(class_dir, new_file_name)
            os.rename(old_file_path, new_file_path)

"""Renaming test dir"""

import os
import re

# Define the path to dataset
base_dir = '/content/drive/MyDrive/ArtClassification/test'

# Function to clean and format the new file name
def format_file_name(file_name):
    # Remove special characters and spaces
    cleaned_name = re.sub(r'[^\w\s]', '', file_name)
    # Replace spaces with underscores
    formatted_name = cleaned_name.replace(' ', '_')
    return formatted_name

# Iterate through the subdirectories in the train directory
for class_name in os.listdir(base_dir):
    class_dir = os.path.join(base_dir, class_name)
    if os.path.isdir(class_dir):
        # Rename the files in the subdirectory
        for i, file_name in enumerate(os.listdir(class_dir)):
            _, extension = os.path.splitext(file_name)
            new_file_name = f"{class_name}_{i}{extension}"
            new_file_name = format_file_name(new_file_name)
            
            # Add '.jpg' extension if the file doesn't have any extension
            if not extension:
                new_file_name += '.jpg'

            old_file_path = os.path.join(class_dir, file_name)
            new_file_path = os.path.join(class_dir, new_file_name)
            os.rename(old_file_path, new_file_path)

"""Renaming validation directory"""

import os
import re

# Define the path to dataset
base_dir = '/content/drive/MyDrive/ArtClassification/validation'

# Function to clean and format the new file name
def format_file_name(file_name):
    # Remove special characters and spaces
    cleaned_name = re.sub(r'[^\w\s]', '', file_name)
    # Replace spaces with underscores
    formatted_name = cleaned_name.replace(' ', '_')
    return formatted_name

# Iterates through the subdirectories in the train directory
for class_name in os.listdir(base_dir):
    class_dir = os.path.join(base_dir, class_name)
    if os.path.isdir(class_dir):
        # Rename the files in the subdirectory
        for i, file_name in enumerate(os.listdir(class_dir)):
            _, extension = os.path.splitext(file_name)
            new_file_name = f"{class_name}_{i}{extension}"
            new_file_name = format_file_name(new_file_name)
            
            # Add '.jpg' extension if the file doesn't have any extension
            if not extension:
                new_file_name += '.jpg'

            old_file_path = os.path.join(class_dir, file_name)
            new_file_path = os.path.join(class_dir, new_file_name)
            os.rename(old_file_path, new_file_path)

"""Pre processing and defining dir"""

import os
from keras.preprocessing.image import ImageDataGenerator

# Define the paths to your dataset
base_dir = '/content/drive/MyDrive/ArtClassification'
train_dir = os.path.join(base_dir, 'train')
validation_dir = os.path.join(base_dir, 'validation')
test_dir = os.path.join(base_dir, 'test')

# Define the image size for resizing
target_size = (224, 224)

# Define the batch size for training and testing
batch_size = 32

# Data augmentation and normalization
datagen = ImageDataGenerator(
    rescale=1./255,  # Normalize pixel values to [0, 1]
    rotation_range=20,  # Randomly rotate images
    width_shift_range=0.2,  # Randomly shift images horizontally
    height_shift_range=0.2,  # Randomly shift images vertically
    shear_range=0.2,  # Randomly apply shearing transformation
    zoom_range=0.2,  # Randomly zoom in and out
    horizontal_flip=True  # Randomly flip images horizontally
)

# Load and preprocess the training data with data augmentation
train_generator = datagen.flow_from_directory(
    train_dir,
    target_size=target_size,
    batch_size=batch_size,
    class_mode='categorical',
    shuffle=True,  # Shuffle the training data
    subset='training'  # Specify subset as training data
)

# Load and preprocess the validation data
validation_generator = datagen.flow_from_directory(
    validation_dir,
    target_size=target_size,
    batch_size=batch_size,
    class_mode='categorical',
    shuffle=False  # Do not shuffle the validation data
)

# Load and preprocess the testing data
test_datagen = ImageDataGenerator(rescale=1./255)  # Only rescale pixel values for testing
test_generator = test_datagen.flow_from_directory(
    test_dir,
    target_size=target_size,
    batch_size=batch_size,
    class_mode='categorical',
    shuffle=False  # Do not shuffle the testing data
)

# Confirm the number of classes and number of images for each set
num_classes = len(train_generator.class_indices)
print("Number of classes:", num_classes)
print("Number of training images:", train_generator.samples)
print("Number of validation images:", validation_generator.samples)
print("Number of testing images:", test_generator.samples)

"""creating the layers"""

import tensorflow as tf
from tensorflow import keras
from keras.applications import ResNet50
from keras.layers import Dense, GlobalAveragePooling2D
from keras.models import Model
from sklearn.metrics import confusion_matrix, accuracy_score
import os

# Create an instance of the ResNet model
base_model = ResNet50(weights='imagenet', include_top=False, input_shape=(224, 224, 3))

# Freeze the layers of the base model
for layer in base_model.layers:
    layer.trainable = False

# Add a custom classification head
x = base_model.output
x = GlobalAveragePooling2D()(x)
x = Dense(128, activation='relu')(x)
predictions = Dense(num_classes, activation='softmax')(x)

# Create the final model
model = Model(inputs=base_model.input, outputs=predictions)

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Fit the model to the training data
epochs = 15
history = model.fit(
    train_generator,
    epochs=epochs,
    validation_data=validation_generator,
    batch_size=batch_size
)

# Evaluate the trained model on the test data
test_loss, test_accuracy = model.evaluate(test_generator)
print(f'Test Loss: {test_loss:.4f}')
print(f'Test Accuracy: {test_accuracy:.4f}')

# Perform predictions on the test data
y_true = test_generator.classes
y_pred = model.predict(test_generator)
y_pred = tf.argmax(y_pred, axis=1)

# Check if each prediction was correct
correct_predictions = (y_true == y_pred)

# Print the correct predictions
for i in range(len(correct_predictions)):
    print(f"Sample {i+1}: {'Correct' if correct_predictions[i] else 'Incorrect'}")

# Compute confusion matrix
cm = confusion_matrix(y_true, y_pred)
print("Confusion Matrix:")
print(cm)

# Compute accuracy
accuracy = accuracy_score(y_true, y_pred)
print("Accuracy:", accuracy)

"""Visualing the evaluation"""

import matplotlib.pyplot as plt

# Get the history of training/validation accuracy and loss
train_acc = history.history['accuracy']
val_acc = history.history['val_accuracy']
train_loss = history.history['loss']
val_loss = history.history['val_loss']

# Plot accuracy curves
plt.figure(figsize=(8, 6))
plt.plot(train_acc, label='Training Accuracy')
plt.plot(val_acc, label='Validation Accuracy')
plt.title('Training and Validation Accuracy')
plt.xlabel('Epochs')
plt.ylabel('Accuracy')
plt.legend()
plt.show()

# Plot loss curves
plt.figure(figsize=(8, 6))
plt.plot(train_loss, label='Training Loss')
plt.plot(val_loss, label='Validation Loss')
plt.title('Training and Validation Loss')
plt.xlabel('Epochs')
plt.ylabel('Loss')
plt.legend()
plt.show()

from sklearn.metrics import classification_report

# Perform predictions on the test data
y_true = test_generator.classes
y_pred = model.predict(test_generator)
y_pred = tf.argmax(y_pred, axis=1)

# Generate classification report
class_labels = list(test_generator.class_indices.keys())
report = classification_report(y_true, y_pred, target_names=class_labels)

# Print the classification report
print("Classification Report:")
print(report)

"""Visualizing the confusion metric"""

import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix

# Get the true labels and predicted labels
y_true = test_generator.classes
y_pred = model.predict(test_generator)
y_pred = np.argmax(y_pred, axis=1)

# Compute the confusion matrix
cm = confusion_matrix(y_true, y_pred)

# Get the class labels
class_labels = list(test_generator.class_indices.keys())

# Create a heatmap of the confusion matrix
plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt="d", cmap="Blues",
            xticklabels=class_labels, yticklabels=class_labels)
plt.title('Confusion Matrix')
plt.xlabel('Predicted Labels')
plt.ylabel('True Labels')
plt.show()

"""Saving the model"""

import os
from tensorflow import keras

# Get the current working directory
current_directory = os.getcwd()

# Create a folder path for the ArtClassification folder
art_classification_folder = os.path.join(current_directory, 'ArtClassification')

# Create the ArtClassification folder if it doesn't exist
if not os.path.exists(art_classification_folder):
    os.makedirs(art_classification_folder)

# Specify the file path for saving the model
model_file_path = os.path.join(art_classification_folder, 'art_classifier_model.h5')

# Save the trained model
model.save(model_file_path)
print("Model saved successfully.")

import os
from tensorflow import keras


# Specify the directory path for saving the model
art_classification_folder = '/content/drive/MyDrive/ArtClassification'

# Create the ArtClassification folder if it doesn't exist
if not os.path.exists(art_classification_folder):
    os.makedirs(art_classification_folder)

# Specify the file path for saving the model
model_file_path = os.path.join(art_classification_folder, 'art_classifier_model.h5')

# Save the trained model
model.save(model_file_path)

# Print the directory where the model is saved
print("Model saved in directory:", art_classification_folder)

from sklearn.metrics import f1_score, precision_score, recall_score

f1_scores = f1_score(y_true, y_pred, average=None)

precision_scores = precision_score(y_true, y_pred, average=None)
recall_scores = recall_score(y_true, y_pred, average=None)


plt.figure(figsize=(8, 6))
plt.plot(class_labels, f1_scores, marker='o', label='F1 Score')
plt.plot(class_labels, precision_scores, marker='o', label='Precision')
plt.plot(class_labels, recall_scores, marker='o', label='Recall')
plt.title('F1 Score, Precision, and Recall')
plt.xlabel('Class')
plt.ylabel('Score')
plt.legend()
plt.xticks(rotation=45)
plt.show()

import os
import pickle

# Specify the directory path for saving the model
art_classification_folder = '/content/drive/MyDrive/ArtClassification'

# Create the ArtClassification folder if it doesn't exist
if not os.path.exists(art_classification_folder):
    os.makedirs(art_classification_folder)

# Specify the file path for saving the model
model_file_path = os.path.join(art_classification_folder, 'art_classifier_model.pkl')

# Save the trained model as a pkl file
with open(model_file_path, 'wb') as file:
    pickle.dump(model, file)

print("Model saved successfully as a pkl file.")

from sklearn.metrics import f1_score

# Calculate F1 score
f1 = f1_score(y_true, y_pred, average='macro')
print("F1 Score:", f1)