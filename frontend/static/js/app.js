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

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        // Get values
        const topic = document.getElementById('topic').value.trim();
        const grade = document.getElementById('grade').value;
        const language = document.getElementById('language').value;

        if (!topic || !grade || !language) {
            showToast("Please fill out all fields.");
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
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ topic, grade, language })
            });

            const data = await response.json();

            if (response.ok && data.success) {
                const lessonJson = data.data.content;
                
                // Construct Markdown from the structured JSON
                let rawMarkdown = `# ${lessonJson.title || 'Lesson Plan'}\n\n`;
                rawMarkdown += `**Grade Level:** ${grade} | **Language:** ${language}\n\n`;
                
                rawMarkdown += `## 🎯 Objectives\n`;
                if (lessonJson.objectives && lessonJson.objectives.length > 0) {
                    lessonJson.objectives.forEach(obj => {
                        rawMarkdown += `- ${obj}\n`;
                    });
                }
                rawMarkdown += `\n`;
                
                rawMarkdown += `## 📖 Explanation\n`;
                rawMarkdown += `${lessonJson.explanation || ''}\n\n`;
                
                rawMarkdown += `## 🚀 Classroom Activity\n`;
                rawMarkdown += `${lessonJson.activity || ''}\n\n`;
                
                rawMarkdown += `## 📝 Summary\n`;
                rawMarkdown += `${lessonJson.summary || ''}\n\n`;
                
                rawMarkdown += `## ❓ Quiz (Multiple Choice)\n`;
                if (lessonJson.mcqs && lessonJson.mcqs.length > 0) {
                    lessonJson.mcqs.forEach((mcq, index) => {
                        rawMarkdown += `**${index + 1}. ${mcq.question || ''}**\n`;
                        if (mcq.options) {
                            mcq.options.forEach(opt => {
                                rawMarkdown += `   - ${opt}\n`;
                            });
                        }
                        rawMarkdown += `\n`;
                    });
                }
                
                rawMarkdown += `## ✅ Answer Key\n`;
                if (lessonJson.mcqs && lessonJson.mcqs.length > 0) {
                    lessonJson.mcqs.forEach((mcq, index) => {
                        rawMarkdown += `- **Q${index + 1}:** ${mcq.answer || ''}\n`;
                    });
                }

                // Parse markdown to HTML using marked.js
                const htmlContent = marked.parse(rawMarkdown);
                
                // Inject HTML
                contentContainer.innerHTML = htmlContent;
                
                // Show results
                loadingState.classList.add('hidden');
                resultsArea.classList.remove('hidden');
                
                // Scroll to results
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
