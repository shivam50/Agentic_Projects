#!/usr/bin/env python
import sys
import warnings

from datetime import datetime

from coder.crew import Coder

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

assignment = "Write a python program to calculate the first 10000 terms of this series, multiplying the total by 3: 1 - 1/2 + 1/5 - 1/7 + ..."

def run():
    inputs = {"assignment": assignment}

    result = Coder().crew().kickoff(inputs=inputs)
    print(result.raw)
