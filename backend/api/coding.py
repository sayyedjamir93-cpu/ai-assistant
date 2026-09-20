import re
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from backend.database.database import get_db
from backend.database.models import User
from backend.api.auth import get_current_user
from backend.ai.brain import brain
from backend.config import settings

router = APIRouter(prefix="/coding", tags=["Coding Assistant"])


# ==========================================
# Pydantic Schemas
# ==========================================

class ConceptExplainRequest(BaseModel):
    concept: str = Field(..., min_length=1, json_schema_extra={"example": "Recursion"})
    language: Optional[str] = Field("python", json_schema_extra={"example": "python"})


class ErrorDiagnosticRequest(BaseModel):
    error_message: str = Field(..., min_length=1, json_schema_extra={"example": "IndexError: list index out of range"})
    language: Optional[str] = Field("python", json_schema_extra={"example": "python"})
    code_snippet: Optional[str] = Field(None, json_schema_extra={"example": "arr = [1, 2]\nprint(arr[5])"})


class CodeReviewRequest(BaseModel):
    code: str = Field(..., min_length=1, json_schema_extra={"example": "def add(a, b):\n    return a + b"})
    language: Optional[str] = Field("python", json_schema_extra={"example": "python"})


class ErrorDiagnosticResponse(BaseModel):
    error_name: str
    meaning: str
    possible_causes: List[str]
    how_to_fix: List[str]
    code_example: str
    language: str


class ConceptExplainResponse(BaseModel):
    concept: str
    language: str
    summary: str
    explanation: str
    example_code: str
    best_practices: List[str]


# ==========================================
# Diagnostic Heuristics & Knowledge Bank
# ==========================================

COMMON_ERROR_KNOWLEDGE: Dict[str, Dict[str, Any]] = {
    "indexerror": {
        "error_name": "IndexError",
        "meaning": "You tried to access an item at an index that does not exist in the collection.",
        "possible_causes": [
            "Accessing an index >= len(list).",
            "Using 1-based indexing instead of 0-based indexing.",
            "Accessing elements from an empty list."
        ],
        "how_to_fix": [
            "Check the length of the list using `len(my_list)` before indexing.",
            "Remember that Python uses 0-based indexing (first item is `[0]`, last is `[-1]`).",
            "Use exception handling or `try...except IndexError` for dynamic lookups."
        ],
        "code_example": (
            "# Incorrect:\n"
            "# items = [10, 20]\n"
            "# print(items[2]) # IndexError\n\n"
            "# Correct:\n"
            "items = [10, 20]\n"
            "if len(items) > 2:\n"
            "    print(items[2])\n"
            "else:\n"
            "    print('Index out of bounds safe fallback')"
        )
    },
    "typeerror": {
        "error_name": "TypeError",
        "meaning": "An operation or function was applied to an object of an inappropriate or incompatible data type.",
        "possible_causes": [
            "Concatenating a string and an integer (e.g., `'Age: ' + 20`).",
            "Calling an object that is not a function (e.g., `x = 5; x()`).",
            "Passing an incorrect number of arguments to a function."
        ],
        "how_to_fix": [
            "Convert data types explicitly using `str()`, `int()`, or `float()`.",
            "Use f-strings for string interpolation: `f'Age: {age}'`.",
            "Inspect variable types using `type(var)` or `isinstance(var, ExpectedType)`."
        ],
        "code_example": (
            "# Incorrect:\n"
            "# total = 'Score: ' + 100\n\n"
            "# Correct (using f-strings):\n"
            "score = 100\n"
            "total = f'Score: {score}'\n"
            "print(total)  # Output: Score: 100"
        )
    },
    "keyerror": {
        "error_name": "KeyError",
        "meaning": "You tried to access a dictionary key that does not exist.",
        "possible_causes": [
            "Typo in key name or case mismatch.",
            "Key has not been inserted into the dictionary yet.",
            "JSON response structure differs from expectation."
        ],
        "how_to_fix": [
            "Use the `.get()` method: `my_dict.get('key', default_value)`.",
            "Check existence using `if 'key' in my_dict:`.",
            "Use `collections.defaultdict` for automatic default values."
        ],
        "code_example": (
            "student = {'name': 'Alex', 'grade': 'A'}\n"
            "# Safe lookup with fallback default:\n"
            "age = student.get('age', 18)\n"
            "print(f'Age: {age}')"
        )
    },
    "recursionerror": {
        "error_name": "RecursionError",
        "meaning": "A recursive function exceeded Python's maximum recursion stack depth limit.",
        "possible_causes": [
            "Missing or unreachable base case.",
            "Recursive step does not reduce toward the base condition.",
            "Cyclic reference or cyclic graph traversal without a visited set."
        ],
        "how_to_fix": [
            "Verify that a base case exists at the very start of the function.",
            "Ensure parameters change toward the base condition in every recursive branch.",
            "Maintain a `visited = set()` when traversing graphs or trees."
        ],
        "code_example": (
            "def countdown(n):\n"
            "    # Base case\n"
            "    if n <= 0:\n"
            "        print('Liftoff!')\n"
            "        return\n"
            "    print(n)\n"
            "    # Recursive step reducing n\n"
            "    countdown(n - 1)\n\n"
            "countdown(3)"
        )
    }
}


# ==========================================
# Coding Assistant Endpoints
# ==========================================

@router.post("/explain-concept", response_model=ConceptExplainResponse)
def explain_concept(
    payload: ConceptExplainRequest,
    current_user: User = Depends(get_current_user)
):
    """Provide a structured explanation of a programming concept with code examples and best practices."""
    concept_lower = payload.concept.lower().strip()
    lang = payload.language.lower().strip()

    # Query AI Brain for deep reasoning
    prompt = f"Explain the programming concept '{payload.concept}' in {payload.language}. Include core principles, worked examples, and best practices."
    ai_result = brain.process_message(user_message=prompt, mode="coding")

    summary = f"Understanding {payload.concept.title()} in {lang.title()}"
    best_practices = [
        "Write clean, self-documenting code with meaningful names.",
        "Add unit tests for edge cases and boundary conditions.",
        "Keep functions focused on a single responsibility (SRP)."
    ]

    example_code = "# Example Demonstration\n"
    if "recursion" in concept_lower:
        example_code = (
            "def factorial(n):\n"
            "    if n <= 1:\n"
            "        return 1\n"
            "    return n * factorial(n - 1)\n\n"
            "print(factorial(5)) # 120"
        )
    elif "pointer" in concept_lower:
        example_code = (
            "#include <iostream>\n"
            "using namespace std;\n\n"
            "int main() {\n"
            "    int var = 42;\n"
            "    int* ptr = &var;\n"
            "    cout << \"Value: \" << *ptr << endl;\n"
            "    return 0;\n"
            "}"
        )
    else:
        example_code = (
            "// Clean implementation example\n"
            "function processData(items) {\n"
            "    return items.filter(x => x > 0).map(x => x * 2);\n"
            "}"
        )

    return ConceptExplainResponse(
        concept=payload.concept,
        language=lang,
        summary=summary,
        explanation=ai_result["response_text"],
        example_code=example_code,
        best_practices=best_practices
    )


@router.post("/diagnose-error", response_model=ErrorDiagnosticResponse)
def diagnose_error(
    payload: ErrorDiagnosticRequest,
    current_user: User = Depends(get_current_user)
):
    """Diagnose a programming error message or stack trace with root cause and fix."""
    err_text = payload.error_message.lower()

    # Check known error patterns
    matched_key = None
    for k in COMMON_ERROR_KNOWLEDGE.keys():
        if k in err_text:
            matched_key = k
            break

    if matched_key:
        info = COMMON_ERROR_KNOWLEDGE[matched_key]
        return ErrorDiagnosticResponse(
            error_name=info["error_name"],
            meaning=info["meaning"],
            possible_causes=info["possible_causes"],
            how_to_fix=info["how_to_fix"],
            code_example=info["code_example"],
            language=payload.language or "python"
        )

    # General diagnostic fallback
    err_name = payload.error_message.split(":")[0] if ":" in payload.error_message else "Runtime Error"
    return ErrorDiagnosticResponse(
        error_name=err_name.strip(),
        meaning=f"The program encountered an exception: '{payload.error_message}'.",
        possible_causes=[
            "Invalid variable state, null reference, or unexpected data type.",
            "Missing imported module or missing library dependency.",
            "Boundary condition violation or network/file I/O failure."
        ],
        how_to_fix=[
            "Inspect the stack trace line numbers to locate the failing line.",
            "Verify inputs and add print/debug statements around the invocation.",
            "Wrap risky blocks in exception handlers with descriptive logs."
        ],
        code_example=(
            "try:\n"
            "    # Risky operation\n"
            "    pass\n"
            "except Exception as e:\n"
            "    print(f'Handled error safely: {e}')"
        ),
        language=payload.language or "python"
    )


@router.post("/review-code")
def review_code(
    payload: CodeReviewRequest,
    current_user: User = Depends(get_current_user)
):
    """Review user-supplied code for syntax, logic, security, and optimization."""
    code_len = len(payload.code.splitlines())
    prompt = f"Review this {payload.language} code:\n```{payload.language}\n{payload.code}\n```"
    ai_result = brain.process_message(user_message=prompt, mode="coding")

    return {
        "language": payload.language,
        "lines_analyzed": code_len,
        "feedback": ai_result["response_text"],
        "recommendations": [
            "Ensure all edge cases and null checks are handled.",
            "Follow language-specific style standards (e.g., PEP 8 for Python).",
            "Include descriptive docstrings or comments for complex algorithms."
        ]
    }


@router.get("/languages")
def get_supported_languages():
    """Retrieve list of supported programming languages and available reference cheatsheets."""
    return {
        "supported_languages": [
            {"id": "python", "name": "Python", "version": "3.10+"},
            {"id": "c", "name": "C", "standard": "C11/C17"},
            {"id": "cpp", "name": "C++", "standard": "C++20"},
            {"id": "javascript", "name": "JavaScript", "standard": "ES6+"},
            {"id": "html_css", "name": "HTML5 & CSS3", "standard": "W3C"}
        ]
    }
