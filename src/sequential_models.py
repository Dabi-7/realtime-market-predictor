import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, GRU, SimpleRNN, Dense, Dropout

def build_model(model_type, input_shape):
    model = Sequential()
    if model_type == 'RNN':
        model.add(SimpleRNN(50, input_shape=input_shape))
    elif model_type == 'LSTM':
        model.add(LSTM(50, input_shape=input_shape))
    elif model_type == 'GRU':
        model.add(GRU(50, input_shape=input_shape))
    
    model.add(Dropout(0.2))
    model.add(Dense(1, activation='sigmoid'))
    model.compile(optimizer='adam', loss='binary_crossentropy', metrics=['accuracy'])
    return model
