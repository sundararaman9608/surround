import unittest
import os
from surround import Assembler, Estimator, State, Config, Validator, Filter


test_text = "hello"


class HelloStage(Estimator):
    def estimate(self, state, config):
        state.text = test_text
        if "helloStage" in config:
            state.config_value = config["helloStage"]["suffix"]

    def fit(self, state, config):
        print("No training implemented")


class AssemblerState(State):
    text = None
    config_value = None
    stage1 = None
    stage2 = None
    final_ran = False


class InputValidator(Validator):
    def validate(self, state, config):
        if state.text:
            raise ValueError("'text' is not None")

        if state.config_value:
            raise ValueError("'config_value' is not None")

        if state.stage1:
            raise ValueError("'stage1' is not None")

        if state.stage2:
            raise ValueError("'stage2' is not None")


class TestFinalStage(Filter):
    def operate(self, state, config):
        state.final_ran = True

class TestSurround(unittest.TestCase):

    def test_happy_path(self):
        data = AssemblerState()
        assembler = Assembler("Happy path", InputValidator(), HelloStage(), Config())
        assembler.init_assembler()
        assembler.run(data)
        self.assertEqual(data.text, test_text)

    def test_rejecting_attributes(self):
        data = AssemblerState()
        assembler = Assembler("Reject attribute", InputValidator(), HelloStage(), Config())
        assembler.init_assembler()
        assembler.run(data)
        self.assertRaises(AttributeError, getattr, data, "no_text")

    def test_surround_config(self):
        path = os.path.dirname(__file__)
        config = Config()
        config.read_config_files([os.path.join(path, "config.yaml")])
        data = AssemblerState()
        assembler = Assembler("Surround config", InputValidator(), HelloStage(), config)
        assembler.run(data)
        self.assertEqual(data.config_value, "Scott")

    def test_finaliser_successful_pipeline(self):
        data = AssemblerState()
        assembler = Assembler("Finalizer test", InputValidator(), HelloStage(), Config())
        assembler.set_finaliser(TestFinalStage())
        assembler.init_assembler()

        # Run assembler which will succeed
        assembler.run(data)

        # Finalizer should be executed
        self.assertTrue(data.final_ran)

    def test_finaliser_fail_pipeline(self):
        # Ensure pipeline will crash
        data = AssemblerState()
        data.text = ""

        assembler = Assembler("Finalizer test", InputValidator(), HelloStage(), Config())
        assembler.set_finaliser(TestFinalStage())
        assembler.init_assembler()

        # Run assembler which will fail
        assembler.run(data)

        # Finalizer should still be executed
        self.assertTrue(data.final_ran)
