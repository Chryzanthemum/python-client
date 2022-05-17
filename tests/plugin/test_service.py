from typing import Union, Type

import pytest

from steamship.app.response import Response
from steamship.base import Client
from steamship.plugin.inputs.train_plugin_input import TrainPluginInput
from steamship.plugin.inputs.training_parameter_plugin_input import TrainingParameterPluginInput
from steamship.plugin.outputs.train_plugin_output import TrainPluginOutput
from steamship.plugin.outputs.training_parameter_plugin_output import TrainingParameterPluginOutput
from steamship.plugin.service import PluginRequest, PluginService
from steamship.plugin.tagger import TrainableTagger
from tests.demo_apps.plugins.taggers.plugin_trainable_tagger import TrainableModel


class ValidStringToStringPlugin(PluginService):
    def run(self, request: PluginRequest[str]) -> Union[str, Response[str]]:
        pass


class ValidTrainableStringToStringPlugin(TrainableTagger):
    def get_model_class(self) -> Type[TrainableModel]:
        return TrainableModel

    def get_steamship_client(self) -> Client:
        return self.client

    def run_with_model(self, request: PluginRequest[str], model: TrainableModel) -> Union[str, Response[str]]:
        pass

    def get_training_parameters(self, request: PluginRequest[TrainingParameterPluginInput]) -> Response[
        TrainingParameterPluginOutput]:
        return Response(data=TrainingParameterPluginOutput())

    def train(self, request: PluginRequest[TrainPluginInput]) -> Response[TrainPluginOutput]:
        return Response(data=TrainPluginOutput())


#
# Tests plugin initialization
# --------------------------------------------

def test_plugin_service_is_abstract():
    with pytest.raises(Exception):
        service = PluginService()


def test_plugin_service_must_implement_run_and_subclass_request_from_dict():
    with pytest.raises(Exception):
        class BadPlugin(PluginService):
            pass

        BadPlugin()

    ValidStringToStringPlugin()


#
# Tests for the `run` method
# --------------------------------------------

def test_run_succeeds():
    plugin = ValidStringToStringPlugin()
    plugin.run(PluginRequest(data=""))
    # Note: there is no run endpoint implemented automatically, since the path depends on the plugin type.
    # TODO: Should we standardize all plugins to use /run?


#
# Tests for the `get_training_params` method
# --------------------------------------------

def test_plugin_does_not_have_training_param_endpoint():
    plugin = ValidStringToStringPlugin()
    # It has it from the base class
    assert (hasattr(plugin, "get_training_parameters") == False)


def test_with_override_get_training_params_succeeds():
    trainable_plugin = ValidTrainableStringToStringPlugin()
    trainable_plugin.get_training_parameters(PluginRequest(data=TrainingParameterPluginInput()))
    trainable_plugin.get_training_parameters_endpoint()


#
# Tests for the `train` method
# --------------------------------------------

def test_non_trainable_plugin_lacks_train():
    plugin = ValidStringToStringPlugin()
    # It has it from the base class
    assert (hasattr(plugin, "train") == False)


def test_with_override_train_succeeds():
    trainable_plugin = ValidTrainableStringToStringPlugin()
    trainable_plugin.train(PluginRequest(data=TrainPluginInput()))
    trainable_plugin.train_endpoint()