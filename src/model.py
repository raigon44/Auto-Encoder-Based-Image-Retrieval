import tensorflow as tf
from datetime import datetime
import numpy as np
import config
from main import logger


class Model:

    def __init__(self, model_config):
        self.tensorboard_callback = tf.keras.callbacks.TensorBoard(
            log_dir=config.FileLocation.log_dir + datetime.now().strftime("%Y%m%d-%H%M%S"))
        self.model_save_path = config.FileLocation.save_dir
        self.model_checkpoint_callback = tf.keras.callbacks.ModelCheckpoint(
            filepath=self.model_save_path,
            save_weights_only=False,
            monitor='val_loss',
            mode='min',
            save_best_only=True
        )
        self.config = model_config
        self.auto_encoder_model, self.encoder_model = self.create_model()

    def create_model(self):
        input_tensor = tf.keras.Input(shape=(32, 32, 3))
        encoder_layer = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(input_tensor)
        encoder_layer = tf.keras.layers.MaxPooling2D((2, 2))(encoder_layer)
        encoder_layer = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(encoder_layer)
        encoder_layer = tf.keras.layers.MaxPooling2D((2, 2))(encoder_layer)
        encoder_layer = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(encoder_layer)
        encoder_layer = tf.keras.layers.MaxPooling2D((2, 2))(encoder_layer)
        encoder_layer = tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same')(encoder_layer)
        encoder_layer = tf.keras.layers.MaxPooling2D((2, 2))(encoder_layer)
        encoder_layer = tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same')(encoder_layer)
        encoder_layer = tf.keras.layers.MaxPooling2D((2, 2))(encoder_layer)
        encoder_layer = tf.keras.layers.Flatten()(encoder_layer)
        encoder_layer = tf.keras.layers.Dense(32, activation='relu')(encoder_layer)
        encoder_output = tf.keras.layers.Dense(self.config.latent_space_dim)(encoder_layer)

        encoder_model = tf.keras.Model(input_tensor, encoder_output)
        logger.info(f"Encoder model summary: \n {encoder_model.summary()}")

        decoder_layer = tf.keras.layers.Dense(27, activation='relu')(encoder_output)
        decoder_layer = tf.keras.layers.Reshape((3, 3, 3))(decoder_layer)
        decoder_layer = tf.keras.layers.Conv2D(8, (2, 2), activation='relu', padding='same')(decoder_layer)
        decoder_layer = tf.keras.layers.UpSampling2D((2, 2))(decoder_layer)
        decoder_layer = tf.keras.layers.Conv2D(16, (2, 2), activation='relu', padding='same')(decoder_layer)
        decoder_layer = tf.keras.layers.UpSampling2D((2, 2))(decoder_layer)
        decoder_layer = tf.keras.layers.Conv2D(32, (2, 2), activation='relu', padding='same')(decoder_layer)
        decoder_layer = tf.keras.layers.UpSampling2D((2, 2))(decoder_layer)
        decoder_layer = tf.keras.layers.Conv2D(64, (2, 2), activation='relu', padding='same')(decoder_layer)
        decoder_layer = tf.keras.layers.UpSampling2D((2, 2))(decoder_layer)
        decoder_layer = tf.keras.layers.Flatten()(decoder_layer)
        decoder_layer = tf.keras.layers.Dense(64, activation='relu')(decoder_layer)
        decoder_layer = tf.keras.layers.Dense(3072)(decoder_layer)
        decoder_output = tf.keras.layers.Reshape((32, 32, 3))(decoder_layer)

        auto_encoder = tf.keras.Model(input_tensor, decoder_output)

        logger.info(f"Auto encoder model summary: \n {auto_encoder.summary()}")

        return auto_encoder, encoder_model

    def train_model(self, x_train, x_test):
        self.auto_encoder_model.compile(optimizer=self.config.optimizer, loss=self.config.loss,
                                        metrics=[self.config.metrics])

        training_history = self.auto_encoder_model.fit(x_train, x_train,
                                                       epochs=config.ModelConfig.epochs,
                                                       batch_size=config.ModelConfig.batch_size,
                                                       shuffle=True,
                                                       callbacks=[self.tensorboard_callback,
                                                                  self.model_checkpoint_callback],
                                                       validation_data=(x_test, x_test))

        logger.info(f"Average test loss: {np.average(training_history.history['loss'])}")

        self.encoder_model.save('models/Encoder_Final.hdf5')
        self.auto_encoder_model.save('models/AutoEncoder_Final.hdf5')

        return
