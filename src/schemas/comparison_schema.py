from pydantic import BaseModel, Field
from typing import Dict, Optional
from enum import Enum
from config import settings

class ComparisonOutcome(Enum):
    BOTH_CORRECT = "BOTH_CORRECT"
    BOTH_INCORRECT = "BOTH_INCORRECT"
    OPENAI_ONLY_CORRECT = "OPENAI_ONLY_CORRECT"
    GROQ_ONLY_CORRECT = "GROQ_ONLY_CORRECT"
    NEITHER_ANSWERED = "NEITHER_ANSWERED"

class ModelResponse(BaseModel):
    """Model response details"""
    answer: Optional[str]
    failed: bool
    model_name: str  # Add this field

class ModelDetail(BaseModel):
    is_correct: bool
    provided_answer: bool

class ComparisonResult(BaseModel):
    models_agree: bool
    outcome: ComparisonOutcome
    details: Dict[str, ModelDetail]

class TestResults(BaseModel):
    model_responses: Dict[str, ModelResponse]
    comparison_result: ComparisonResult

class QuestionPair(BaseModel):
    text: Dict[str, str]  # original, misspelled
    expected_answer: str

class SeverityLevel(str, Enum):
    LIGHT = "light"
    MEDIUM = "medium"
    SEVERE = "severe"

class MisspellingInfo(BaseModel):
    char_change_count: int
    severity: SeverityLevel  #  accepts string enum

class ComparisonRecord(BaseModel):
    """Complete comparison record"""
    timestamp: str
    row_idx: int
    question_pair: QuestionPair
    misspelling_info: MisspellingInfo
    results: Dict[str, TestResults]
    model_details: Dict[str, str] = Field(  # Add this field
        default_factory=lambda: {
            "openai": settings.OPENAI_MODEL,
            "groq": settings.GROQ_MODEL
        }
    ) 