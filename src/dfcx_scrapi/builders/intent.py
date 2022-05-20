"""A set of builder methods to create CX proto resource objects"""

# Copyright 2022 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import logging
from typing import List, Dict, Union

from google.cloud.dialogflowcx_v3beta1 import types


def build_intent(display_name, phrases: List[str]):
    """build an intent from list of phrases plus meta"""
    tps = {
        "text": row["text"] for row in phrases
    }
    intent = {
        "display_name": display_name,
        "training_phrases": tps
    }
    logging.info("intent %s", intent)
    return intent




class IntentBuilder:
    """Base Class for CX Intent builder."""

    def __init__(self):
        pass


    def _check_intent_exist(self):
        """Check if the proto_obj exists otherwise raise an error."""

        if not self.proto_obj:
            raise ValueError(
                "There is no proto_obj! Create or load one to continue."
            )


    def _parameter_checking(self):
        """Check if the annotated parameters exist
        in the Parameter attribute of proto_obj.

        """
        tp_params_set = set()
        for tp in self.proto_obj.training_phrases:
            for part in tp.parts:
                tp_params_set.add(part.parameter_id)
        # Remove the empty string for unannotated parts
        try:
            tp_params_set.remove("")
        except KeyError:
            pass

        # Get the parameters from proto_obj
        parameters_set = {param.id for param in self.proto_obj.parameters}

        # Check for not existing annotated parameters
        for tp_param in tp_params_set:
            if tp_param not in parameters_set:
                raise Exception(
                    f"parameter_id {tp_param} does not exist in parameters."
                    "Please add it using add_parameter method to continue."
                )



    def load_intent(self, obj: types.Intent) -> types.Intent:
        """Load an existing intent to proto_obj for further changes."""
        self.proto_obj = obj

        return self.proto_obj


    def create_empty_intent(
        self,
        display_name: str,
        priority: int = 500000,
        is_fallback: bool = False,
        description: str = None
    ) -> types.Intent:
        """Create an empty intent."""
        self.proto_obj = types.Intent(
            display_name=display_name,
            priority=priority,
            is_fallback=is_fallback,
            description=description
        )

        return self.proto_obj


    def add_training_phrase(
        self,
        phrase: List[str],
        annotations: List[str],
        repeat_count: int = 1
    ) -> types.Intent:
        """Add a training phrase to proto_obj.

        Args:
          phrase (list of strings)
            A list of strings that represents a single training phrase.
          annotations (list of strings)
            A list of strings that represents
              parameter_id of each part in phrase.
            Length of annotations list should be less than or equal to
              length of phrase list.
            If the length is less than length of phrase list it propagate
              the rest of the annotations automatically with no annotation.
          repeat_count (Optional int):
            Indicates how many times this example was added to the intent.

        Example 1:
          phrase = [
              'one way', ' ticket leaving ', 'January 1',
              ' to ', 'LAX', ' from ', 'CDG'
          ]
          annotations = [
              'flight_type', '', 'departure_date',
              '', 'arrival_city', '', 'departure_city'
          ]
        Example 2:
          phrase = ["I'd like to buy a ", 'one way', ' ticket']
          annotations = ['', 'flight_type']
        """

        self._check_intent_exist()

        # Type / Error checking
        if not (
            all((isinstance(p, str) for p in phrase)) and
            all((isinstance(a, str) for a in annotations))
        ):
            raise ValueError(
                "Only strings allowed in phrase or annotations list"
            )
        if len(annotations) > len(phrase):
            raise IndexError(
                "Length of annotations list is more than phrase list!"
            )

        # Propagate the annotations list
        annotations.extend([""] * (len(phrase) - len(annotations)))
        # Creating parts for the training phrase
        parts_list = []
        for text, parameter_id in zip(phrase, annotations):
            part = types.Intent.TrainingPhrase.Part(
                text=text, parameter_id=parameter_id
            )
            parts_list.append(part)

        # Create the training phrase obj and add it to the others
        tp = types.Intent.TrainingPhrase(
            parts=parts_list, repeat_count=repeat_count
        )
        self.proto_obj.training_phrases.append(tp)

        return self.proto_obj


    def add_parameter(
        self,
        parameter_id: str,
        entity_type: str,
        is_list: bool = False,
        redact: bool = False
    ) -> types.Intent:
        """Add a parameter to Parameter attribute of proto_obj."""
        self._check_intent_exist()

        # Create the new parameter and add it to the proto_obj
        parameters = types.Intent.Parameter(
            id=parameter_id,
            entity_type=entity_type,
            is_list=is_list,
            redact=redact
        )
        self.proto_obj.parameters.append(parameters)

        return self.proto_obj


    def add_label(
        self, labels: Union[Dict[str, str], List[str]]
    ) -> types.Intent:
        """Add a label to proto_obj.

        Args:
          labels (Dict[str, str] | List[str]):

        """
        self._check_intent_exist()

        if not labels:
            pass
        elif isinstance(labels, list):
            self.proto_obj.labels.update(
                {label: label for label in labels}
            )
        elif isinstance(labels, dict):
            self.proto_obj.labels.update(labels)
        else:
            raise ValueError("labels should be either a list or a dictionary.")

        return self.proto_obj
