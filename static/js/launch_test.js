const quizContainer = document.querySelector(".quiz-container");
const quizId = quizContainer ? quizContainer.getAttribute("data-quiz-id") : null;
const quizDuration = parseInt(document.getElementById("timer").getAttribute("data-time")) / 60; // Convert to minutes

let timeLeft = parseInt(document.getElementById("timer").getAttribute("data-time"));
let currentQuestionIndex = 0;
let answers = {};
let totalQuestions = document.querySelectorAll(".question").length;

// Start Timer
function startTimer() {
    const timerElement = document.getElementById("timer");
    const timerInterval = setInterval(() => {
        let minutes = Math.floor(timeLeft / 60);
        let seconds = timeLeft % 60;
        timerElement.innerText = `Time Left: ${minutes}:${seconds < 10 ? '0' : ''}${seconds}`;

        if (timeLeft <= 0) {
            clearInterval(timerInterval);
            submitQuiz(); // Auto-submit when time ends
        }
        timeLeft--;
    }, 1000);
}

// Save the selected answer
function saveAnswer() {
    const currentQuestionElement = document.querySelector(".question:not([style*='display: none'])");
    if (!currentQuestionElement) return; // Prevents error if no visible question found

    const questionId = currentQuestionElement.getAttribute("data-question-id");
    if (!questionId) return; // Prevents crash if question ID is missing

    const selectedOption = document.querySelector(`input[name="option_${questionId}"]:checked`);
    const questionBtn = document.querySelector(`.question-btn[data-question-id="${questionId}"]`);

    if (selectedOption) {
        answers[questionId] = selectedOption.value;
        if (questionBtn) questionBtn.classList.add("answered");
    } else {
        answers[questionId] = null;
        if (questionBtn) questionBtn.classList.add("not-answered");
    }

    updateStatus();
}

// Update quiz status dynamically
function updateStatus() {
    let answeredCount = Object.values(answers).filter(val => val !== null).length;
    let notAnsweredCount = totalQuestions - answeredCount; // Only skipped count

    document.getElementById("answered-count").innerText = answeredCount;
    document.getElementById("not-answered-count").innerText = notAnsweredCount;
}

// Load selected question
function loadQuestion(index) {
    document.querySelectorAll(".question").forEach((q, i) => {
        q.style.display = i === index ? "block" : "none";
    });
    currentQuestionIndex = index;
    updateStatus();
}

// Handle next question
function nextQuestion() {
    saveAnswer();
    if (currentQuestionIndex < totalQuestions - 1) {
        loadQuestion(currentQuestionIndex + 1);
    }
}

// Handle previous question
function prevQuestion() {
    if (currentQuestionIndex > 0) {
        loadQuestion(currentQuestionIndex - 1);
    }
}

// Generate Question Buttons
function generateQuestionButtons() {
    let questionMenu = document.getElementById("question-menu");
    for (let i = 0; i < totalQuestions; i++) {
        let btn = document.createElement("button");
        btn.classList.add("question-btn");
        btn.innerText = i + 1;
        btn.addEventListener("click", () => loadQuestion(i));
        questionMenu.appendChild(btn);
    }
}

// Submit the quiz
function submitQuiz() {
    let timeTaken = quizDuration * 60 - timeLeft; // Corrected timeTaken calculation
    let attempts = Object.values(answers).filter(val => val !== null).length;

    fetch("/submit_quiz", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ 
            quiz_id: quizId, 
            answers: answers, 
            timeTaken: timeTaken,
            attempts: attempts
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            alert("Submission failed: " + data.error);
            return;
        }

        alert(`Quiz Submitted! Your Score: ${data.score}`);
        window.location.href = data.redirect; // Redirect to test page
    })
    .catch(error => console.error("❌ Error submitting quiz:", error));
}

// Event Listeners
document.getElementById("save-next").addEventListener("click", nextQuestion);
document.getElementById("prev-question").addEventListener("click", prevQuestion);
document.getElementById("submit-quiz").addEventListener("click", submitQuiz);

// Initialize functions
generateQuestionButtons();
startTimer();
