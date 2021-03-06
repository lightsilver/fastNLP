import unittest

import numpy as np
import torch

from fastNLP.core.callback import EchoCallback, EarlyStopCallback, GradientClipCallback, LRScheduler, ControlC, \
    LRFinder, \
    TensorboardCallback
from fastNLP.core.dataset import DataSet
from fastNLP.core.instance import Instance
from fastNLP.core.losses import BCELoss
from fastNLP.core.metrics import AccuracyMetric
from fastNLP.core.optimizer import SGD
from fastNLP.core.trainer import Trainer
from fastNLP.models.base_model import NaiveClassifier


def prepare_env():
    def prepare_fake_dataset():
        mean = np.array([-3, -3])
        cov = np.array([[1, 0], [0, 1]])
        class_A = np.random.multivariate_normal(mean, cov, size=(1000,))

        mean = np.array([3, 3])
        cov = np.array([[1, 0], [0, 1]])
        class_B = np.random.multivariate_normal(mean, cov, size=(1000,))

        data_set = DataSet([Instance(x=[float(item[0]), float(item[1])], y=[0.0]) for item in class_A] +
                           [Instance(x=[float(item[0]), float(item[1])], y=[1.0]) for item in class_B])
        return data_set

    data_set = prepare_fake_dataset()
    data_set.set_input("x")
    data_set.set_target("y")
    model = NaiveClassifier(2, 1)
    return data_set, model


class TestCallback(unittest.TestCase):
    def test_echo_callback(self):
        data_set, model = prepare_env()
        trainer = Trainer(data_set, model,
                          loss=BCELoss(pred="predict", target="y"),
                          n_epochs=2,
                          batch_size=32,
                          print_every=50,
                          optimizer=SGD(lr=0.1),
                          check_code_level=2,
                          use_tqdm=False,
                          callbacks=[EchoCallback()])
        trainer.train()

    def test_gradient_clip(self):
        data_set, model = prepare_env()
        trainer = Trainer(data_set, model,
                          loss=BCELoss(pred="predict", target="y"),
                          n_epochs=20,
                          batch_size=32,
                          print_every=50,
                          optimizer=SGD(lr=0.1),
                          check_code_level=2,
                          use_tqdm=False,
                          dev_data=data_set,
                          metrics=AccuracyMetric(pred="predict", target="y"),
                          callbacks=[GradientClipCallback(model.parameters(), clip_value=2)])
        trainer.train()

    def test_early_stop(self):
        data_set, model = prepare_env()
        trainer = Trainer(data_set, model,
                          loss=BCELoss(pred="predict", target="y"),
                          n_epochs=20,
                          batch_size=32,
                          print_every=50,
                          optimizer=SGD(lr=0.01),
                          check_code_level=2,
                          use_tqdm=False,
                          dev_data=data_set,
                          metrics=AccuracyMetric(pred="predict", target="y"),
                          callbacks=[EarlyStopCallback(5)])
        trainer.train()

    def test_lr_scheduler(self):
        data_set, model = prepare_env()
        optimizer = torch.optim.SGD(model.parameters(), lr=0.01)
        trainer = Trainer(data_set, model,
                          loss=BCELoss(pred="predict", target="y"),
                          n_epochs=5,
                          batch_size=32,
                          print_every=50,
                          optimizer=optimizer,
                          check_code_level=2,
                          use_tqdm=False,
                          dev_data=data_set,
                          metrics=AccuracyMetric(pred="predict", target="y"),
                          callbacks=[LRScheduler(torch.optim.lr_scheduler.StepLR(optimizer, step_size=10, gamma=0.1))])
        trainer.train()

    def test_KeyBoardInterrupt(self):
        data_set, model = prepare_env()
        trainer = Trainer(data_set, model,
                          loss=BCELoss(pred="predict", target="y"),
                          n_epochs=5,
                          batch_size=32,
                          print_every=50,
                          optimizer=SGD(lr=0.1),
                          check_code_level=2,
                          use_tqdm=False,
                          callbacks=[ControlC(False)])
        trainer.train()

    def test_LRFinder(self):
        data_set, model = prepare_env()
        trainer = Trainer(data_set, model,
                          loss=BCELoss(pred="predict", target="y"),
                          n_epochs=5,
                          batch_size=32,
                          print_every=50,
                          optimizer=SGD(lr=0.1),
                          check_code_level=2,
                          use_tqdm=False,
                          callbacks=[LRFinder(len(data_set) // 32)])
        trainer.train()

    def test_TensorboardCallback(self):
        data_set, model = prepare_env()
        trainer = Trainer(data_set, model,
                          loss=BCELoss(pred="predict", target="y"),
                          n_epochs=5,
                          batch_size=32,
                          print_every=50,
                          optimizer=SGD(lr=0.1),
                          check_code_level=2,
                          use_tqdm=False,
                          dev_data=data_set,
                          metrics=AccuracyMetric(pred="predict", target="y"),
                          callbacks=[TensorboardCallback("loss", "metric")])
        trainer.train()
