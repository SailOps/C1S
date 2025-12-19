let appData = {};
let currentTopic = null;
let currentQuestionIndex = 0;

// DOM Elements
// DOM Elements
const topicView = document.getElementById('topic-view');
const questionView = document.getElementById('question-view');
const topicGrid = document.getElementById('topic-grid');
const backBtn = document.getElementById('back-btn');
const currentTopicLabel = document.getElementById('current-topic');
const questionText = document.getElementById('question-text');
const answerContainer = document.getElementById('answer-text'); // Renamed for clarity but id remains
const answerBody = document.getElementById('answer-body'); // NEW
const showAnswerBtn = document.getElementById('show-answer-btn');
const nextQuestionBtn = document.getElementById('next-question-btn');


// Init
function init() {
    if (window.appData) {
        appData = window.appData;
        renderTopics();
    } else {
        topicGrid.innerHTML = '<p class="error">Kļūda: Dati nav atrasti (data.js neielādējās).</p>';
    }
}

function renderTopics() {
    topicGrid.innerHTML = '';
    Object.keys(appData).sort().forEach(topic => {
        const topicIdx = appData[topic].length;
        const topicPrefix = topic.split(' ')[0]; // Assumes format "Q01 - Title"

        const card = document.createElement('div');
        card.className = 'topic-card';
        card.innerHTML = `
            <div class="topic-info">
                <h3>${topic}</h3>
                <span>${topicIdx} jautājumi</span>
            </div>
            <div class="topic-actions">
                <button class="action-btn-small" onclick="selectTopic('${topic}')">JAUTĀJUMI</button>
                <a href="question.html?id=${topicPrefix}" class="action-btn-small secondary">SARAKSTS</a>
            </div>
        `;
        // card.onclick removed to avoid accidental clicks
        topicGrid.appendChild(card);
    });
}

function selectTopic(topic) {
    currentTopic = topic;
    topicView.classList.remove('active');
    topicView.classList.add('hidden');
    questionView.classList.remove('hidden');
    questionView.classList.add('active');

    currentTopicLabel.textContent = topic;
    showRandomQuestion();
}

function showRandomQuestion() {
    if (!currentTopic || !appData[currentTopic]) return;

    const questions = appData[currentTopic];
    const randomIndex = Math.floor(Math.random() * questions.length);
    const question = questions[randomIndex];

    // Reset view
    answerContainer.classList.remove('visible');
    showAnswerBtn.style.display = 'inline-block';
    nextQuestionBtn.style.display = 'inline-block';

    // Set content
    // Replace newlines with <br> for simple formatting if needed, 
    // but CSS white-space: pre-wrap handles it mostly.
    questionText.innerHTML = `${question.id} ${question.question}`;
    // Use answerBody if available, otherwise fallback (for safety, though we changed HTML)
    if (answerBody) {
        answerBody.innerHTML = question.answer;
    } else {
        answerContainer.innerHTML = question.answer;
    }
}

// Event Listeners
backBtn.addEventListener('click', () => {
    questionView.classList.remove('active');
    questionView.classList.add('hidden');
    topicView.classList.remove('hidden');
    topicView.classList.add('active');
    currentTopic = null;
});

showAnswerBtn.addEventListener('click', () => {
    answerContainer.classList.add('visible');
    showAnswerBtn.style.display = 'none';
});

nextQuestionBtn.addEventListener('click', () => {
    showRandomQuestion();
});

// Start
init();
