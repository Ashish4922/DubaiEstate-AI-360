
from unittest.mock import patch

from Genai.assistant import answer_question


@patch("Genai.assistant._load_areas", return_value=["Al Hudaiba"])
@patch(
    "Genai.assistant.get_transaction_metrics",
    return_value={
        "transaction_count": 2,
        "total_value": 3000000,
        "average_value": 1500000,
    },
)
def test_answers_supported_area_question(mock_metrics, mock_areas):
    answer = answer_question(
        "What is the average transaction value in Al Hudaiba?"
    )

    assert "Al Hudaiba" in answer
    assert "Transaction count: 2" in answer
    assert "AED 3,000,000.00" in answer
    mock_metrics.assert_called_once()


def test_rejects_unsupported_question():
    answer = answer_question("Will property prices double next year?")

    assert "can't answer" in answer


def test_rejects_blank_question():
    answer = answer_question("   ")

    assert "Please enter a question" in answer


@patch("Genai.assistant._load_areas", return_value=["Al Hudaiba"])
def test_rejects_unknown_area(mock_areas):
    answer = answer_question(
        "What is the average transaction value in Downtown Dubai?"
    )

    assert "couldn't identify that area" in answer
@patch("Genai.assistant._load_areas", return_value=["Al Hudaiba"])
@patch(
    "Genai.assistant.get_transaction_metrics",
    return_value={
        "transaction_count": 3,
        "total_value": 9000000,
        "average_value": 3000000,
    },
)
def test_grounded_answer_uses_exact_retrieved_numbers(
    mock_metrics, mock_areas
):
    answer = answer_question(
        "What is the total transaction value in Al Hudaiba?"
    )

    assert "Transaction count: 3" in answer
    assert "AED 9,000,000.00" in answer
    assert "AED 3,000,000.00" in answer

    mock_metrics.assert_called_once()
@patch("Genai.assistant._load_areas", return_value=["Al Hudaiba"])
@patch(
    "Genai.assistant.get_transaction_metrics",
    return_value={
        "transaction_count": 0,
        "total_value": 0,
        "average_value": None,
    },
)
def test_handles_missing_transaction_data(mock_metrics, mock_areas):
    answer = answer_question(
        "What is the average transaction value in Al Hudaiba?"
    )

    assert "No matching transactions were found" in answer
    assert "AED" not in answer

    mock_metrics.assert_called_once()
def test_rejects_investment_guarantee_questions():
    questions = [
        "Will property prices double next year?",
        "Can you guarantee a 20% return on investment?",
        "Which Dubai property will definitely make me rich?",
    ]

    for question in questions:
        answer = answer_question(question)

        assert "can't answer" in answer.lower()
