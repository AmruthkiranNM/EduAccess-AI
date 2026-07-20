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
            
            // Fix for mermaid rendering in hidden tabs
            if (target === 'tab-map' && window.mermaid) {
                setTimeout(() => {
                    try { window.mermaid.run(); } catch(e) {}
                }, 50);
            }
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
                
                // Update Sticky Header
                document.getElementById('header-title').innerText = topic;
                document.getElementById('badge-subject').innerText = subject;
                document.getElementById('badge-grade').innerText = grade;
                document.getElementById('badge-duration').innerText = `${duration} min`;
                document.getElementById('badge-difficulty').innerText = difficulty;
                document.getElementById('last-generated').innerText = `Generated: ${new Date().toLocaleTimeString()}`;
                
                // 1. Render Overview (Dashboard)
                let overviewHtml = `<div class="dashboard-grid">`;
                if(lessonJson.overview) {
                    const ov = lessonJson.overview;
                    overviewHtml += `
                        <div class="metric-card"><h4>Duration</h4><div class="value">${ov.estimated_teaching_time || duration + ' min'}</div></div>
                        <div class="metric-card"><h4>Difficulty</h4><div class="value">${ov.difficulty || difficulty}</div></div>
                        <div class="metric-card"><h4>Style</h4><div class="value">${ov.teaching_style || teaching_style}</div></div>
                    </div>
                    <div class="info-panel">
                        <h4>Objective</h4>
                        <p>${ov.lesson_objective || ''}</p>
                        <h4>Expected Outcome</h4>
                        <p>${ov.learning_outcome || ''}</p>
                        <h4>Quick Summary</h4>
                        <p>${ov.quick_summary || ''}</p>
                    </div>
                    
                    <div class="form-row">
                        <div>
                            <h4>Required Materials</h4>
                            <ul class="outcomes-list">
                                ${(ov.required_materials || []).map(m => `<li>${m}</li>`).join('')}
                            </ul>
                        </div>
                        <div>
                            <h4>Key Vocabulary</h4>
                            <ul class="outcomes-list">
                                ${(ov.key_vocabulary || []).map(v => `<li>${v}</li>`).join('')}
                            </ul>
                        </div>
                    </div>
                    `;
                }
                document.getElementById('tab-overview').innerHTML = overviewHtml;

                // 2. Render Lesson Plan (Collapsible sections)
                let lessonHtml = ``;
                if(lessonJson.lesson_plan) {
                    lessonJson.lesson_plan.forEach(section => {
                        lessonHtml += `
                            <details class="lesson-section" open>
                                <summary>${section.subtopic_title || 'Section'} <span style="font-weight:normal; font-size:0.9em; opacity:0.8;">⏱ ${section.estimated_time || ''}</span></summary>
                                <div class="lesson-section-content markdown-body">
                                    <p><strong>Simple:</strong> ${section.simple_explanation || ''}</p>
                                    <p><strong>Detailed:</strong> ${section.detailed_explanation || ''}</p>
                                    <div class="info-panel">
                                        <h4>Real Life & Fun Facts</h4>
                                        <p><strong>Real Life:</strong> ${section.real_life_example || ''}</p>
                                        <p><strong>Fun Fact:</strong> ${section.fun_fact || ''}</p>
                                    </div>
                                    <p><strong>Common Mistake:</strong> ${section.common_mistake || ''}</p>
                                    <p><strong>Keywords:</strong> ${(section.important_keywords||[]).join(', ')}</p>
                                    <p><strong>Q:</strong> ${section.student_question || ''} <br><strong>A:</strong> ${section.suggested_answer || ''}</p>
                                    <p><strong>Check:</strong> ${section.quick_check_question || ''}</p>
                                    ${section.teacher_tip ? `<p><strong>Teacher Tip:</strong> ${section.teacher_tip}</p>` : ''}
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
                                    <div class="timeline-time">${item.time_range}</div>
                                    <h4>${item.title}</h4>
                                    <p><strong>Teacher:</strong> ${item.teacher_script}</p>
                                    <p><strong>Students:</strong> ${item.expected_student_activity}</p>
                                </div>
                            </div>
                        `;
                    });
                }
                timelineHtml += `</div>`;
                document.getElementById('tab-timeline').innerHTML = timelineHtml;

                // 4. Render Visualizations (Backend Image Gallery)
                let mapHtml = `<div class="gallery-grid">`;
                let hasViz = false;
                if(lessonJson.visualizations && lessonJson.visualizations.length > 0) {
                    hasViz = true;
                    lessonJson.visualizations.forEach((vis, idx) => {
                        mapHtml += `
                            <div class="gallery-card viz-card">
                                <h3>${vis.title || 'Educational Diagram'}</h3>
                                <div class="viz-toolbar">
                                    <button class="viz-btn" onclick="window.openLightbox(document.getElementById('viz-img-${idx}').src)" title="Zoom"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="11" cy="11" r="8"></circle><line x1="21" y1="21" x2="16.65" y2="16.65"></line><line x1="11" y1="8" x2="11" y2="14"></line><line x1="8" y1="11" x2="14" y2="11"></line></svg></button>
                                    <button class="viz-btn" onclick="window.toggleFullscreen('viz-container-${idx}')" title="Fullscreen"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M8 3H5a2 2 0 0 0-2 2v3m18 0V5a2 2 0 0 0-2-2h-3m0 18h3a2 2 0 0 0 2-2v-3M3 16v3a2 2 0 0 0 2 2h3"></path></svg></button>
                                    <button class="viz-btn" onclick="window.downloadImage(document.getElementById('viz-img-${idx}').src, '${(vis.title||'image').replace(/'/g, "\\'")}')" title="Download"><svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"></path><polyline points="7 10 12 15 17 10"></polyline><line x1="12" y1="15" x2="12" y2="3"></line></svg></button>
                                </div>
                                <div class="gallery-img-container" id="viz-container-${idx}">
                                    <img id="viz-img-${idx}" src="${vis.url}" alt="${vis.title}">
                                </div>
                                <p class="viz-caption" style="font-size:0.9em; font-style:italic; color:var(--text-muted); margin:10px 0;">${vis.caption || ''}</p>
                                
                                <details class="lesson-section" style="margin-top:auto;">
                                    <summary>Teacher Details & Explanation</summary>
                                    <div class="lesson-section-content">
                                        <p><strong>What it shows:</strong> ${vis.what_it_shows || ''}</p>
                                        <p><strong>Explanation:</strong> ${vis.short_explanation || vis.teacher_explanation || ''}</p>
                                        <p><strong>Important Labels:</strong> ${vis.important_labels || ''}</p>
                                        <p><strong>Observations:</strong> ${vis.key_observations || ''}</p>
                                        <p><strong>Discussion:</strong> ${vis.discussion_questions || ''}</p>
                                    </div>
                                </details>
                            </div>
                        `;
                    });
                }
                mapHtml += `</div>`;
                if (!hasViz) {
                    mapHtml = `
                        <div class="info-panel" style="text-align:center; padding:3rem;">
                            <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--text-muted)" stroke-width="1.5"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><circle cx="8.5" cy="8.5" r="1.5"></circle><polyline points="21 15 16 10 5 21"></polyline></svg>
                            <h3 style="color:var(--text-muted); margin-top:1rem;">Educational Diagram Not Available</h3>
                            <p style="color:var(--text-muted);">No highly relevant image was found for this specific topic.</p>
                        </div>`;
                }
                document.getElementById('tab-map').innerHTML = mapHtml;


                // 5. Render Activities
                let activitiesHtml = ``;
                if(lessonJson.activities) {
                    lessonJson.activities.forEach(act => {
                        activitiesHtml += `
                            <details class="lesson-section activity-card">
                                <summary>${act.activity_name} <span class="badge">${act.execution_time}</span></summary>
                                <div class="lesson-section-content">
                                    <p><strong>Objective:</strong> ${act.objective}</p>
                                    <p><strong>Materials:</strong> ${(act.materials||[]).join(', ')}</p>
                                    <p><strong>Group Size:</strong> ${act.group_size}</p>
                                    <div class="info-panel">
                                        <h4>Instructions</h4>
                                        <ol>${(act.instructions||[]).map(s => `<li>${s}</li>`).join('')}</ol>
                                    </div>
                                    <p><strong>Teacher Script:</strong> "${act.teacher_script}"</p>
                                    <p><strong>Assessment:</strong> ${act.assessment}</p>
                                    <p><strong>Variations:</strong> ${act.variations}</p>
                                </div>
                            </details>
                        `;
                    });
                }
                document.getElementById('tab-activities').innerHTML = activitiesHtml;

                // 6. Render Quiz
                let quizHtml = ``;
                if (lessonJson.quiz) {
                    lessonJson.quiz.forEach((q, index) => {
                        quizHtml += `
                            <div class="quiz-card">
                                <h4>${index + 1}. ${q.question} <span class="badge" style="background:var(--text-muted)">${q.question_type}</span> <span class="badge" style="background:var(--primary-color)">${q.difficulty}</span></h4>
                                ${q.options && q.options.length ? `<ul class="options">${q.options.map(opt => `<li>${opt}</li>`).join('')}</ul>` : ''}
                                <div class="explanation">
                                    <strong>Correct Answer:</strong> ${q.correct_answer}<br><br>
                                    ${q.explanation}
                                </div>
                            </div>
                        `;
                    });
                }
                document.getElementById('tab-quiz').innerHTML = quizHtml;

                // 7. Render Homework
                let hwHtml = `<div class="dashboard-grid">`;
                if (lessonJson.homework) {
                    const renderHwCard = (hwObj, icon, typeName) => {
                        if(!hwObj || !hwObj.title) return '';
                        const diffBadgeClass = (hwObj.difficulty_badge||'').toLowerCase() === 'hard' ? 'bg-danger' : ((hwObj.difficulty_badge||'').toLowerCase() === 'medium' ? 'bg-warning' : 'bg-success');
                        return `
                            <div class="activity-card hw-card">
                                <div class="hw-header" style="display:flex; justify-content:space-between; align-items:center; margin-bottom:1rem; border-bottom:1px solid var(--border-color); padding-bottom:0.5rem;">
                                    <h4 style="margin:0;">${icon} ${typeName}</h4>
                                    <div>
                                        <span class="badge ${diffBadgeClass}" style="margin-right:5px;">${hwObj.difficulty_badge || 'Adaptive'}</span>
                                        <span class="badge" style="background:var(--bg-card); color:var(--text-color); border:1px solid var(--border-color)">⏱ ${hwObj.estimated_time || '15 mins'}</span>
                                    </div>
                                </div>
                                <h3 style="margin-bottom:0.5rem;">${hwObj.title}</h3>
                                <p><strong>Objective:</strong> ${hwObj.objective || ''}</p>
                                <p><strong>Outcome:</strong> ${hwObj.learning_outcome || ''}</p>
                                <details class="lesson-section" style="margin-top:1rem;">
                                    <summary>Instructions & Rubric</summary>
                                    <div class="lesson-section-content">
                                        <p><strong>Instructions:</strong></p>
                                        <ol style="padding-left:20px;">${(hwObj.instructions||[]).map(i => `<li>${i}</li>`).join('')}</ol>
                                        <p><strong>Format:</strong> ${hwObj.submission_format || ''}</p>
                                        <p><strong>Materials:</strong> ${(hwObj.required_materials||[]).join(', ')}</p>
                                        <div class="info-panel" style="margin-top:1rem;">
                                            <strong>Evaluation Rubric:</strong><br>${hwObj.teacher_evaluation_rubric || ''}
                                        </div>
                                    </div>
                                </details>
                            </div>
                        `;
                    };
                    
                    const hw = lessonJson.homework || {};
                    if(hw.easy) hwHtml += renderHwCard(hw.easy, '🟢', 'Easy Homework');
                    if(hw.medium) hwHtml += renderHwCard(hw.medium, '🟡', 'Medium Homework');
                    if(hw.advanced) hwHtml += renderHwCard(hw.advanced, '🔴', 'Advanced Homework');
                    if(hw.creative) hwHtml += renderHwCard(hw.creative, '🎨', 'Creative Homework');
                    if(hw.project) hwHtml += renderHwCard(hw.project, '🏗️', 'Project Work');
                    if(hw.research) hwHtml += renderHwCard(hw.research, '🔍', 'Research Activity');
                    if(hw.revision) hwHtml += renderHwCard(hw.revision, '📄', 'Revision Questions');
                    if(hw.exam) hwHtml += renderHwCard(hw.exam, '📝', 'Exam Questions');
                }
                hwHtml += `</div>`;
                document.getElementById('tab-homework').innerHTML = hwHtml;

                // 8. Render Teacher Notes
                let notesHtml = `<div class="dashboard-grid">`;
                if (lessonJson.teacher_notes) {
                    const tn = lessonJson.teacher_notes;
                    notesHtml += `
                        <div class="activity-card" style="grid-column: 1 / -1;">
                            <h3><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:8px; vertical-align:middle"><path d="M22 12h-4l-3 9L9 3l-3 9H2"></path></svg>Lesson Strategy & Flow</h3>
                            <div class="lesson-section-content markdown-body" style="margin-top:1rem;">
                                <p><strong>Strategy:</strong></p>
                                ${(tn.teaching_strategy||[]).map(s => `<p>${s}</p>`).join('')}
                                <p><strong>Flow:</strong></p>
                                ${(tn.lesson_flow||[]).map(s => `<p>${s}</p>`).join('')}
                                <p><strong>Tips:</strong></p>
                                ${(tn.teaching_tips||[]).map(s => `<p>${s}</p>`).join('')}
                            </div>
                        </div>
                        
                        <div class="metric-card">
                            <h4>Classroom Management & Assessment</h4>
                            ${(tn.classroom_management||[]).map(s => `<p>${s}</p>`).join('')}
                            <hr style="margin:1rem 0; border:none; border-top:1px solid var(--border-color)">
                            ${(tn.assessment_tips||[]).map(s => `<p>${s}</p>`).join('')}
                        </div>
                        
                        <div class="metric-card">
                            <h4>Real World Connections</h4>
                            ${(tn.real_world_connections||[]).map(s => `<p>${s}</p>`).join('')}
                            <hr style="margin:1rem 0; border:none; border-top:1px solid var(--border-color)">
                            <h4>Reflections</h4>
                            ${(tn.reflection_questions||[]).map(s => `<p>${s}</p>`).join('')}
                        </div>
                        
                        <div class="activity-card" style="grid-column: 1 / -1;">
                            <h3>Common Misconceptions & FAQ</h3>
                            <div class="lesson-section-content">
                                <p><strong>Mistakes:</strong></p>
                                <ul style="padding-left:20px;">${(tn.common_student_mistakes||[]).map(m => `<li>${m}</li>`).join('')}</ul>
                                <p style="margin-top:1rem"><strong>Suggested Responses:</strong></p>
                                <ul style="padding-left:20px;">${(tn.suggested_teacher_responses||[]).map(m => `<li>${m}</li>`).join('')}</ul>
                                
                                <details class="lesson-section" style="margin-top:1rem;">
                                    <summary>Frequently Asked Questions</summary>
                                    <div class="lesson-section-content">
                                        ${(tn.frequently_asked_questions||[]).map(q => `<p><strong>Q: ${q.question}</strong><br>A: ${q.answer}</p>`).join('')}
                                    </div>
                                </details>
                            </div>
                        </div>
                        
                        <div class="activity-card" style="grid-column: 1 / -1;">
                            <h3>Differentiation & Support</h3>
                            <div class="form-row" style="margin-top:1rem;">
                                <div class="info-panel" style="flex:1"><h4>Needs Support</h4><ul style="padding-left:20px">${((tn.differentiated_learning||{}).support||[]).map(s => `<li>${s}</li>`).join('')}</ul></div>
                                <div class="info-panel" style="flex:1"><h4>Advanced Extension</h4><ul style="padding-left:20px">${((tn.differentiated_learning||{}).advanced||[]).map(s => `<li>${s}</li>`).join('')}</ul></div>
                            </div>
                        </div>
                    `;
                }
                notesHtml += `</div>`;
                document.getElementById('tab-notes').innerHTML = notesHtml;

                // 9. Render Student Resources
                let resHtml = `<div class="dashboard-grid">`;
                if (lessonJson.student_resources) {
                    const sr = lessonJson.student_resources;
                    resHtml += `
                        <div class="activity-card" style="grid-column: 1 / -1;">
                            <h3><svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-right:8px; vertical-align:middle"><path d="M4 19.5A2.5 2.5 0 0 1 6.5 17H20"></path><path d="M6.5 2H20v20H6.5A2.5 2.5 0 0 1 4 19.5v-15A2.5 2.5 0 0 1 6.5 2z"></path></svg>Key Concepts & Quick Revision</h3>
                            <div class="lesson-section-content markdown-body" style="margin-top:1rem;">
                                <p><strong>Revision:</strong></p>
                                ${(sr.quick_revision||[]).map(s => `<p>${s}</p>`).join('')}
                                <p><strong>Key Concepts:</strong></p>
                                <ul style="padding-left:20px;">${(sr.key_concepts||[]).map(k => `<li>${k}</li>`).join('')}</ul>
                            </div>
                        </div>
                        
                        <div class="activity-card" style="grid-column: 1 / -1;">
                            <h3>Definitions & Glossary</h3>
                            <p><strong>Vocabulary:</strong> ${(sr.vocabulary||[]).join(', ')}</p>
                            <div class="form-row" style="margin-top:1rem;">
                                <div style="flex:1">
                                    <h4>Definitions</h4>
                                    ${(sr.definitions||[]).map(d => `<p><strong>${d.term}:</strong> ${d.definition}</p>`).join('')}
                                </div>
                                <div style="flex:1">
                                    <h4>Glossary</h4>
                                    ${(sr.glossary||[]).map(d => `<p><strong>${d.term}:</strong> ${d.definition}</p>`).join('')}
                                </div>
                            </div>
                        </div>
                        
                        <div class="metric-card" style="grid-column: 1 / -1;">
                            <h3>Exam Prep & Practice</h3>
                            <div class="form-row" style="margin-top:1rem;">
                                <div style="flex:1">
                                    <h4>Exam Tips</h4>
                                    <ul style="padding-left:20px">${(sr.exam_tips||[]).map(k => `<li>${k}</li>`).join('')}</ul>
                                </div>
                                <div style="flex:1">
                                    <h4>Practice Questions</h4>
                                    <ul style="padding-left:20px">${(sr.practice_questions||[]).map(k => `<li>${k}</li>`).join('')}</ul>
                                </div>
                            </div>
                        </div>
                        
                        ${sr.flashcards && sr.flashcards.length ? `
                        <div class="activity-card" style="grid-column: 1 / -1;">
                            <h3>Flashcards</h3>
                            <div class="dashboard-grid" style="grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); margin-top:1rem;">
                                ${sr.flashcards.map((f, i) => `
                                    <div class="flashcard info-panel" style="text-align:center; padding:2rem 1rem; cursor:pointer;" onclick="this.classList.toggle('flipped')">
                                        <div class="front" style="font-weight:bold; font-size:1.1em">${f.question}</div>
                                        <div class="back" style="display:none; color:var(--text-color); margin-top:1rem; border-top:1px solid var(--border-color); padding-top:1rem">${f.answer}</div>
                                    </div>
                                `).join('')}
                            </div>
                        </div>` : ''}
                        
                        <div class="activity-card" style="grid-column: 1 / -1;">
                            <h3>Further Exploration & Tricks</h3>
                            <div class="form-row" style="margin-top:1rem;">
                                <div style="flex:1">
                                    <h4>Memory Tricks</h4>
                                    <ul style="padding-left:20px">${(sr.memory_tricks||[]).map(k => `<li>${k}</li>`).join('')}</ul>
                                </div>
                                <div style="flex:1">
                                    <h4>Interesting Facts</h4>
                                    <ul style="padding-left:20px">${(sr.interesting_facts||[]).map(k => `<li>${k}</li>`).join('')}</ul>
                                </div>
                                <div style="flex:1">
                                    <h4>Additional Reading</h4>
                                    <ul style="padding-left:20px">${(sr.additional_reading||[]).map(k => `<li>${k}</li>`).join('')}</ul>
                                </div>
                            </div>
                        </div>
                    `;
                }
                resHtml += `</div>`;
                const tabRes = document.getElementById('tab-resources');
                if(tabRes) tabRes.innerHTML = resHtml;
                
                // For copy functionality
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

// Visualization Helpers
window.toggleFullscreen = function(elementId) {
    const elem = document.getElementById(elementId);
    if (!elem) return;
    if (!document.fullscreenElement) {
        if (elem.requestFullscreen) {
            elem.requestFullscreen().catch(err => console.error("Error attempting to enable fullscreen:", err));
        }
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
};

window.copyViz = function(elementId) {
    const elem = document.getElementById(elementId);
    if (!elem) return;
    // For mermaid SVG or markdown table
    const textToCopy = elem.innerText;
    navigator.clipboard.writeText(textToCopy).then(() => {
        alert("Visualization content copied!");
    }).catch(err => {
        console.error("Could not copy text: ", err);
    });
};

window.openLightbox = function(imgSrc) {
    const modal = document.getElementById('lightboxModal');
    const modalImg = document.getElementById('lightboxImg');
    if (modal && modalImg) {
        modalImg.src = imgSrc;
        modal.classList.add('show');
    }
};

window.closeLightbox = function() {
    const modal = document.getElementById('lightboxModal');
    if (modal) {
        modal.classList.remove('show');
    }
};

window.downloadImage = function(imgSrc, title) {
    // Attempt to download by fetching blob to avoid CORS if possible, or just open in new tab
    fetch(imgSrc)
        .then(res => res.blob())
        .then(blob => {
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.style.display = 'none';
            a.href = url;
            a.download = title.replace(/\s+/g, '_') + '.jpg';
            document.body.appendChild(a);
            a.click();
            window.URL.revokeObjectURL(url);
        })
        .catch(() => {
            // Fallback: open in new tab
            window.open(imgSrc, '_blank');
        });
};

window.fetchWikimediaImage = async function(query, imgElementId, attrElementId) {
    const imgElem = document.getElementById(imgElementId);
    const attrElem = document.getElementById(attrElementId);
    if (!imgElem || !attrElem) return;
    
    imgElem.style.opacity = '0.5';
    
    // Wikipedia API url to search for images in File namespace (6)
    const url = `https://commons.wikimedia.org/w/api.php?action=query&generator=search&gsrnamespace=6&gsrsearch=${encodeURIComponent(query)}&gsrlimit=1&prop=imageinfo&iiprop=url|extmetadata&format=json&origin=*`;
    
    try {
        const response = await fetch(url);
        const data = await response.json();
        
        if (data && data.query && data.query.pages) {
            const pages = data.query.pages;
            const firstPageId = Object.keys(pages)[0];
            const page = pages[firstPageId];
            
            if (page.imageinfo && page.imageinfo.length > 0) {
                const info = page.imageinfo[0];
                let artist = "Wikimedia Commons";
                if (info.extmetadata && info.extmetadata.Artist) {
                    // Artist might contain HTML, strip it roughly
                    artist = info.extmetadata.Artist.value.replace(/<[^>]*>?/gm, '');
                }
                
                imgElem.src = info.url;
                imgElem.style.opacity = '1';
                imgElem.setAttribute('data-full-src', info.url);
                attrElem.innerHTML = `Source: <i>${artist}</i>`;
                
                // Attach click to open lightbox
                imgElem.onclick = () => window.openLightbox(info.url);
                
                return info.url; // success
            }
        }
        
        // Fallback
        throw new Error("No image found");
    } catch (e) {
        imgElem.style.opacity = '1';
        imgElem.src = "https://upload.wikimedia.org/wikipedia/commons/a/ac/No_image_available.svg"; // standard no image
        attrElem.innerText = "No image found for this topic.";
        console.error("Wikimedia fetch error: ", e);
        return null;
    }
};
