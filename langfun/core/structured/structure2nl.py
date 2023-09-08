# Copyright 2023 The Langfun Authors
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
"""Structured value to natural language."""

import inspect
from typing import Annotated, Any

import langfun.core as lf
from langfun.core.structured import mapping
import pyglove as pg


class StructureToNaturalLanguage(mapping.Mapping):
  """LangFunc for converting a structured value to natural language.

  {{ preamble }}

  {% if examples -%}
  {% for example in examples -%}
  {%- if example.nl_context -%}
  {{ nl_context_title}}:
  {{ example.nl_context | indent(2, True)}}

  {% endif -%}
  {{ value_title}}:
  {{ object_repr(example.value) | indent(2, True) }}

  {{ nl_text_title }}:
  {{ example.nl_text | indent(2, True) }}

  {% endfor %}
  {% endif -%}
  {% if nl_context -%}
  {{ nl_context_title }}:
  {{ nl_context | indent(2, True)}}

  {% endif -%}
  {{ value_title }}:
  {{ object_repr(value) | indent(2, True) }}

  {{ nl_text_title }}:
  """

  preamble: Annotated[
      lf.LangFunc, 'Preamble used for zeroshot natural language mapping.'
  ]

  nl_context_title: Annotated[str, 'The section title for nl_context.'] = (
      'CONTEXT_FOR_DESCRIPTION'
  )

  nl_text_title: Annotated[str, 'The section title for nl_text.'] = (
      'NATURAL_LANGUAGE_TEXT'
  )

  value_title: Annotated[str, 'The section title for schema.'] = 'JSON_OBJECT'

  @property
  def value(self) -> Any:
    """Returns the structured input value."""
    return self.message.result

  @property
  def nl_context(self) -> str:
    """Returns the context information for the description."""
    return self.message.text

  def object_repr(self, value: Any) -> str:
    return pg.format(value, compact=False, python_format=True)


@pg.use_init_args(['examples'])
class DescribeStructure(StructureToNaturalLanguage):
  """Describe a structured value using natural language."""

  preamble = """
      Please help describe a JSON formatted object using natural language.

      INSTRUCTIONS:
        1. Do not add details which are not present in the object.
        2. If a field in the object has None as its value, do not mention it.
      """


def describe(
    value: Any,
    context: str | None = None,
    *,
    examples: list[mapping.MappingExample] | None = None,
    **kwargs,
) -> str:
  """Describes a structured value using natural language.

  Examples:

    ```
    class FlightDuration(pg.Object):
      hours: int
      minutes: int

    class Flight(pg.Object):
      airline: str
      flight_number: str
      departure_airport: str
      arrival_airport: str
      departure_time: str
      arrival_time: str
      duration: FlightDuration
      stops: int
      price: float

    text = lf.describe(
        Flight(
            airline='United Airlines',
            flight_number='UA2631',
            depature_airport: 'SFO',
            arrival_airport: 'JFK',
            depature_time: '2023-09-07T05:15:00',
            arrival_time: '2023-09-07T12:12:00',
            duration: FlightDuration(
                hours=7,
                minutes=57
            ),
            stops=1,
            price=227,
        ))
    print(text)

    >> The flight is operated by United Airlines, has the flight number UA2631,
    >> departs from San Francisco International Airport (SFO), arrives at John
    >> F. Kennedy International Airport (JFK), It departs at
    >> 2023-09-07T05:15:00, arrives at 2023-09-07T12:12:00, has a duration of 7
    >> hours and 57 minutes, makes 1 stop, and costs $227.
    ```

  Args:
    value: A structured value to be mapped.
    context: The context information for describing the structured value.
    examples: An optional list of fewshot examples for helping parsing. If None,
      the default one-shot example will be added.
    **kwargs: Keyword arguments passed to the `lf.structured.DescribeStructure`,
      e.g. `lm` for specifying the language model.

  Returns:
    The parsed result based on the schema.
  """
  if isinstance(value, lf.Message):
    message = value
  else:
    message = lf.UserMessage(
        context if context else '', result=value, allow_partial=True
    )

  if examples is None:
    examples = _default_describe_examples()
  return DescribeStructure(examples, **kwargs)(message=message).text


class _Country(pg.Object):
  """A example dataclass for structured mapping."""

  name: str
  continents: list[
      pg.typing.Enum[
          'Africa',
          'Asia',
          'Europe',
          'Oceania',
          'North America',
          'South America',
      ]
  ]
  num_states: int
  neighbor_countries: list[str]
  population: int
  capital: str | None
  president: str | None


def _default_describe_examples() -> list[mapping.MappingExample]:
  return [
      mapping.MappingExample(
          nl_context='Brief intro to United States',
          nl_text=inspect.cleandoc("""
              The United States of America is a country primarily located in North America
              consisting of fifty states. It shares land borders with Canada to its north
              and with Mexico to its south and has maritime borders with the Bahamas, Cuba,
              Russia, and other nations. With a population of over 333 million. The national
              capital of the United States is Washington, D.C.
              """),
          schema=None,
          value=_Country(
              name='The United States of America',
              continents=['North America'],
              num_states=50,
              neighbor_countries=[
                  'Canada',
                  'Mexico',
                  'Bahamas',
                  'Cuba',
                  'Russia',
              ],
              population=333000000,
              capital='Washington, D.C',
              president=None,
          ),
      )
  ]
