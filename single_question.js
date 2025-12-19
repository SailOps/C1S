// Logic for single question view
const cardContainer = document.querySelector('.card-container');

function init() {
    if (!window.appData) {
        cardContainer.innerHTML = "<p class='error'>Kļūda: Dati nav atrasti.</p>";
        return;
    }

    // Get ID from URL
    const urlParams = new URLSearchParams(window.location.search);
    const queryId = urlParams.get('id');

    if (!queryId) {
        cardContainer.innerHTML = "<p class='error'>Kļūda: Nav norādīts jautājuma vai tēmas ID (piem., ?id=Q01 vai ?id=Q01.01).</p>";
        return;
    }

    const questionsToRender = findQuestions(queryId);

    if (questionsToRender.length > 0) {
        renderQuestions(questionsToRender);
    } else {
        cardContainer.innerHTML = `<p class='error'>Nekas netika atrasts ar ID "<strong>${queryId}</strong>".</p>`;
    }
}

function findQuestions(queryId) {
    let result = [];
    const topics = Object.keys(window.appData);

    // 1. Try finding exact question match
    for (const topic of topics) {
        const questions = window.appData[topic];
        const exactMatch = questions.find(q => q.id === queryId);
        if (exactMatch) {
            return [exactMatch];
        }
    }

    // 2. Try finding topic match (starts with Query ID)
    // E.g. queryId="Q03" matches topic "Q03 - Meteroloģija"
    const matchedTopicKey = topics.find(t => t.startsWith(queryId));
    if (matchedTopicKey) {
        return window.appData[matchedTopicKey];
    }

    return [];
}

function renderQuestions(questions) {
    // Clear existing static content
    cardContainer.innerHTML = '';

    questions.forEach(q => {
        const card = document.createElement('div');
        card.className = 'flashcard';
        card.style.marginBottom = '40px'; // Add spacing between cards

        card.innerHTML = `
            <div class="card-front">
                <div class="question-content">
                    <span class="section-label">JAUTĀJUMS</span>
                    <h3>${q.id} ${q.question}</h3>
                </div>

                <div class="answer-content visible">
                    <span class="section-label">ATBILDE</span>
                    <div class="answer-body">${q.answer}</div>
                </div>
            </div>
        `;

        cardContainer.appendChild(card);
    });
}

init();
