document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('generator-form');
    const loadingState = document.getElementById('loading-state');
    const resultsArea = document.getElementById('results-area');
    const contentContainer = document.getElementById('content-container');
    const generateBtn = document.getElementById('generate-btn');
    const copyBtn = document.getElementById('copy-btn');
    const printBtn = document.getElementById('print-btn');

    // Configure marked.js options (if needed)
    if(typeof marked !== 'undefined') {
        marked.setOptions({
            breaks: true,
            gfm: true
        });
    }

    /**
     * Display a temporary toast notification.
     * @param {string} message - The message to display.
     * @param {string} [type='error'] - Type of toast, usually determines color.
     */
    function showToast(message, type = 'error') {
        const container = document.getElementById('toast-container');
        if (!container) return;
        
        const toast = document.createElement('div');
        toast.className = 'toast';
        // Simple sanitization
        toast.textContent = message;
        
        container.appendChild(toast);
        
        // Trigger reflow for animation
        setTimeout(() => {
            toast.classList.add('show');
        }, 10);
        
        // Remove after 3.5 seconds
        setTimeout(() => {
            toast.classList.remove('show');
            setTimeout(() => {
                toast.remove();
            }, 300); // Wait for transition to finish
        }, 3500);
    }

    // Tab Navigation Logic
    const tabBtns = document.querySelectorAll('.tab-btn');
    const tabPanes = document.querySelectorAll('.tab-pane');
    
    tabBtns.forEach(btn => {
        btn.addEventListener('click', () => {
            tabBtns.forEach(b => b.classList.remove('active'));
            tabPanes.forEach(p => p.classList.remove('active'));
            
            btn.classList.add('active');
            const target = btn.getAttribute('data-tab');
            document.getElementById(target).classList.add('active');
        });
    });

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Get values
        const topic = document.getElementById('topic').value.trim();
        const subject = document.getElementById('subject').value.trim();
        const grade = document.getElementById('grade').value;
        const language = document.getElementById('language').value;
        const duration = document.getElementById('duration').value;
        const teaching_style = document.getElementById('teaching_style').value;
        const difficulty = document.getElementById('difficulty').value;

        if (!topic || !grade || !language) {
            showToast("Please fill out all required fields.");
            return;
        }

        // UI Updates: Show loading, hide results
        resultsArea.classList.add('hidden');
        loadingState.classList.remove('hidden');
        generateBtn.disabled = true;
        generateBtn.innerHTML = '<span>Generating...</span>';

        try {
            // Send request to backend
            const response = await fetch('/api/generate', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ topic, subject, grade, language, duration, teaching_style, difficulty })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                const lessonJson = data.data.content;
                
                // 1. Render Overview (Dashboard)
                let overviewHtml = `<div class="dashboard-grid">`;
                if(lessonJson.metadata) {
                    overviewHtml += `
                        <div class="metric-card"><h4>Duration</h4><div class="value">${lessonJson.metadata.duration || duration + ' min'}</div></div>
                        <div class="metric-card"><h4>Difficulty</h4><div class="value">${lessonJson.metadata.difficulty || difficulty}</div></div>
                        <div class="metric-card"><h4>Grade</h4><div class="value">${lessonJson.metadata.grade || grade}</div></div>
                        <div class="metric-card"><h4>Activities</h4><div class="value">${lessonJson.metadata.activities_count || 0}</div></div>
                        <div class="metric-card"><h4>Reading Time</h4><div class="value">${lessonJson.metadata.reading_time || '5 min'}</div></div>
                    `;
                }
                overviewHtml += `</div><h3>Learning Outcomes</h3><ul class="outcomes-list">`;
                if(lessonJson.learning_outcomes) {
                    lessonJson.learning_outcomes.forEach(outcome => {
                        overviewHtml += `<li>${outcome}</li>`;
                    });
                }
                overviewHtml += `</ul>`;
                document.getElementById('tab-overview').innerHTML = overviewHtml;

                // 2. Render Lesson Plan (Collapsible sections)
                let lessonHtml = ``;
                if(lessonJson.sections) {
                    lessonJson.sections.forEach(section => {
                        lessonHtml += `
                            <details class="lesson-section" open>
                                <summary>${section.title || 'Section'} <span style="font-weight:normal; font-size:0.9em; opacity:0.8;">⏱ ${section.estimated_time || ''}</span></summary>
                                <div class="lesson-section-content">
                                    ${section.teacher_notes ? `<strong>Teacher Notes:</strong> ${section.teacher_notes}<br><br>` : ''}
                                    ${marked.parse(section.content || '')}
                                </div>
                            </details>
                        `;
                    });
                }
                document.getElementById('tab-lesson').innerHTML = lessonHtml;

                // 3. Render Timeline
                let timelineHtml = `<div class="timeline">`;
                if(lessonJson.timeline) {
                    lessonJson.timeline.forEach(item => {
                        timelineHtml += `
                            <div class="timeline-item">
                                <div class="timeline-content">
                                    <div class="timeline-time">${item.time}</div>
                                    <h4>${item.title}</h4>
                                    <p>${item.description}</p>
                                </div>
                            </div>
                        `;
                    });
                }
                timelineHtml += `</div>`;
                document.getElementById('tab-timeline').innerHTML = timelineHtml;

                // 4. Render Topic Map
                document.getElementById('tab-map').innerHTML = `<div class="tree-map">${lessonJson.topic_map || 'No map available'}</div>`;

                // 5. Render Activities
                let activitiesHtml = ``;
                if(lessonJson.student_engagement) {
                    lessonJson.student_engagement.forEach(act => {
                        activitiesHtml += `<h3>${act.type}</h3><p>${act.prompt}</p><hr>`;
                    });
                }
                document.getElementById('tab-activities').innerHTML = marked.parse(activitiesHtml);

                // 6. Render Quiz
                let quizHtml = ``;
                if (lessonJson.quiz && lessonJson.quiz.length > 0) {
                    lessonJson.quiz.forEach((mcq, index) => {
                        quizHtml += `**${index + 1}. ${mcq.question || ''}**\n`;
                        if (mcq.options) {
                            mcq.options.forEach(opt => {
                                quizHtml += `   - ${opt}\n`;
                            });
                        }
                        quizHtml += `\n**Answer:** ${mcq.answer}\n\n`;
                    });
                }
                document.getElementById('tab-quiz').innerHTML = marked.parse(quizHtml);

                // 7. Render Homework
                document.getElementById('tab-homework').innerHTML = marked.parse(lessonJson.homework || 'No homework assigned.');

                // 8. Render Teacher Notes
                let notesHtml = `### Teacher Tips\n${lessonJson.teacher_tips || ''}\n\n### Common Misconceptions\n${lessonJson.common_misconceptions || ''}`;
                document.getElementById('tab-notes').innerHTML = marked.parse(notesHtml);
                
                // For copy functionality, we store raw JSON representation for now (or a flat text summary)
                document.getElementById('content-container').innerText = JSON.stringify(lessonJson, null, 2);
                
                // Show results and switch to Overview tab
                loadingState.classList.add('hidden');
                resultsArea.classList.remove('hidden');
                tabBtns[0].click(); // Activate first tab
                
                resultsArea.scrollIntoView({ behavior: 'smooth', block: 'start' });
            } else {
                throw new Error(data.error || 'Failed to generate content');
            }
        } catch (error) {
            console.error('Error:', error);
            showToast(error.message);
            loadingState.classList.add('hidden');
        } finally {
            // Reset button
            generateBtn.disabled = false;
            generateBtn.innerHTML = `
                <span>Generate Materials</span>
                <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M5 12h14M12 5l7 7-7 7"/></svg>
            `;
        }
    });

    // Copy to clipboard functionality
    copyBtn.addEventListener('click', async () => {
        try {
            // Get plain text or markdown (here we get the raw text content of the rendered HTML)
            const textToCopy = contentContainer.innerText;
            await navigator.clipboard.writeText(textToCopy);
            
            // Visual feedback
            const originalHtml = copyBtn.innerHTML;
            copyBtn.innerHTML = `
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="var(--success)" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="20 6 9 17 4 12"></polyline></svg>
                <span style="color: var(--success)">Copied!</span>
            `;
            
            setTimeout(() => {
                copyBtn.innerHTML = originalHtml;
            }, 2000);
        } catch (err) {
            console.error('Failed to copy text: ', err);
            showToast('Failed to copy to clipboard.');
        }
    });

    // Print functionality
    printBtn.addEventListener('click', () => {
        window.print();
    });
});
