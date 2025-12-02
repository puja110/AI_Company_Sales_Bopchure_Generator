// ============================================
// Global Variables
// ============================================
let currentBrochureContent = "";
let currentCompanyName = "";

// ============================================
// DOM Elements
// ============================================
const form = document.getElementById("brochure-form");
const generateBtn = document.getElementById("generate-btn");
const clearBtn = document.getElementById("clear-btn");
const companyNameInput = document.getElementById("company-name");
const companyUrlInput = document.getElementById("company-url");
const streamModeCheckbox = document.getElementById("stream-mode");
const progressContainer = document.getElementById("progress-container");
const progressFill = document.getElementById("progress-fill");
const progressText = document.getElementById("progress-text");
const outputSection = document.getElementById("output-section");
const brochurePreview = document.getElementById("brochure-preview");
const markdownContent = document.getElementById("markdown-content");
const loadingOverlay = document.getElementById("loading-overlay");
const toast = document.getElementById("toast");
const toastMessage = document.getElementById("toast-message");

// Tab elements
const tabButtons = document.querySelectorAll(".tab-btn");
const tabPanes = document.querySelectorAll(".tab-pane");

// Action buttons
const copyBtn = document.getElementById("copy-btn");
const downloadBtn = document.getElementById("download-btn");
const downloadHtmlBtn = document.getElementById("download-html-btn");

// ============================================
// Event Listeners
// ============================================

// Form submission
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const companyName = companyNameInput.value.trim();
  let url = companyUrlInput.value.trim();
  const streamMode = streamModeCheckbox.checked;

  // Validation
  if (!companyName || !url) {
    showToast("Please fill in all fields", "error");
    return;
  }

  // Add https:// if not present
  if (!url.startsWith("http://") && !url.startsWith("https://")) {
    url = "https://" + url;
  }

  currentCompanyName = companyName;

  // Generate brochure
  if (streamMode) {
    await generateBrochureStream(companyName, url);
  } else {
    await generateBrochure(companyName, url);
  }
});

// Clear button
clearBtn.addEventListener("click", () => {
  form.reset();
  outputSection.style.display = "none";
  progressContainer.style.display = "none";
  currentBrochureContent = "";
  currentCompanyName = "";
  brochurePreview.innerHTML = "";
  markdownContent.textContent = "";
});

// Tab switching
tabButtons.forEach((button) => {
  button.addEventListener("click", () => {
    const tabName = button.dataset.tab;
    switchTab(tabName);
  });
});

// Copy to clipboard
copyBtn.addEventListener("click", () => {
  if (!currentBrochureContent) {
    showToast("No content to copy", "error");
    return;
  }

  navigator.clipboard
    .writeText(currentBrochureContent)
    .then(() => {
      showToast("Copied to clipboard!", "success");
    })
    .catch(() => {
      showToast("Failed to copy", "error");
    });
});

// Download as Markdown
downloadBtn.addEventListener("click", () => {
  if (!currentBrochureContent) {
    showToast("No content to download", "error");
    return;
  }

  downloadFile(
    currentBrochureContent,
    `${sanitizeFilename(currentCompanyName)}_brochure.md`,
    "text/markdown"
  );
  showToast("Downloaded as Markdown!", "success");
});

// Download as HTML
downloadHtmlBtn.addEventListener("click", () => {
  if (!brochurePreview.innerHTML) {
    showToast("No content to download", "error");
    return;
  }

  const htmlContent = generateFullHTML(
    brochurePreview.innerHTML,
    currentCompanyName
  );
  downloadFile(
    htmlContent,
    `${sanitizeFilename(currentCompanyName)}_brochure.html`,
    "text/html"
  );
  showToast("Downloaded as HTML!", "success");
});

// ============================================
// Main Functions
// ============================================

/**
 * Generate brochure without streaming
 */
async function generateBrochure(companyName, url) {
  console.log("Generating brochure for:", companyName, url);

  try {
    // Show loading
    showLoading(true);
    showProgress(true, "Analyzing website...");
    setProgress(30);

    // Make API request
    const response = await fetch("/generate", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        company_name: companyName,
        url: url,
      }),
    });

    setProgress(70);
    progressText.textContent = "Generating brochure...";

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Server error");
    }

    const data = await response.json();
    console.log("Response received:", data);

    if (data.success) {
      setProgress(100);
      progressText.textContent = "Complete!";

      // Display results
      currentBrochureContent = data.markdown;
      displayBrochure(data.html, data.markdown);

      showToast("Brochure generated successfully!", "success");
    } else {
      throw new Error(data.error || "Failed to generate brochure");
    }
  } catch (error) {
    console.error("Error:", error);
    showToast(error.message || "An error occurred", "error");
  } finally {
    showLoading(false);
    setTimeout(() => showProgress(false), 1000);
  }
}

/**
 * Generate brochure with streaming
 */
async function generateBrochureStream(companyName, url) {
  console.log("Generating brochure with streaming for:", companyName, url);

  try {
    // Show progress
    showProgress(true, "Connecting to AI...");
    setProgress(20);

    // Clear previous content
    brochurePreview.innerHTML =
      '<div style="padding: 20px; text-align: center; color: #64748b;">Generating brochure...</div>';
    markdownContent.textContent = "";
    currentBrochureContent = "";

    // Show output section immediately
    outputSection.style.display = "block";
    outputSection.scrollIntoView({ behavior: "smooth", block: "nearest" });

    setProgress(40);
    progressText.textContent = "Generating brochure...";

    // Make streaming request
    const response = await fetch("/generate-stream", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        company_name: companyName,
        url: url,
      }),
    });

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Failed to connect to server");
    }

    setProgress(60);

    const reader = response.body.getReader();
    const decoder = new TextDecoder();
    let buffer = "";

    // Clear the loading message
    brochurePreview.innerHTML = "";

    while (true) {
      const { done, value } = await reader.read();

      if (done) break;

      buffer += decoder.decode(value, { stream: true });
      const lines = buffer.split("\n");
      buffer = lines.pop() || ""; // Keep incomplete line in buffer

      for (const line of lines) {
        if (line.startsWith("data: ")) {
          try {
            const data = JSON.parse(line.slice(6));

            if (data.error) {
              throw new Error(data.error);
            }

            if (data.chunk) {
              currentBrochureContent += data.chunk;
              updateStreamingDisplay(currentBrochureContent);
            }

            if (data.done) {
              setProgress(100);
              progressText.textContent = "Complete!";
              showToast("Brochure generated successfully!", "success");
              setTimeout(() => showProgress(false), 1000);
            }
          } catch (parseError) {
            console.error("Error parsing SSE data:", parseError);
          }
        }
      }
    }
  } catch (error) {
    console.error("Error:", error);
    showToast(error.message || "An error occurred", "error");
    showProgress(false);

    // Show error in preview
    brochurePreview.innerHTML = `
            <div style="padding: 40px; text-align: center; color: #ef4444;">
                <i class="fas fa-exclamation-circle" style="font-size: 48px; margin-bottom: 20px;"></i>
                <h3>Error Generating Brochure</h3>
                <p>${error.message}</p>
            </div>
        `;
  }
}

// ============================================
// Display Functions
// ============================================

/**
 * Display the generated brochure
 */
function displayBrochure(html, markdown) {
  console.log("Displaying brochure");
  brochurePreview.innerHTML = html;
  markdownContent.textContent = markdown;
  outputSection.style.display = "block";

  // Scroll to output section
  setTimeout(() => {
    outputSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }, 100);
}

/**
 * Update streaming display
 */
function updateStreamingDisplay(markdown) {
  // Convert markdown to HTML for preview
  const html = markdownToHTML(markdown);
  brochurePreview.innerHTML = html;
  markdownContent.textContent = markdown;
}

/**
 * Simple markdown to HTML converter
 */
function markdownToHTML(markdown) {
  let html = markdown;

  // Escape HTML
  html = html
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;");

  // Headers
  html = html.replace(/^#### (.*$)/gim, "<h4>$1</h4>");
  html = html.replace(/^### (.*$)/gim, "<h3>$1</h3>");
  html = html.replace(/^## (.*$)/gim, "<h2>$1</h2>");
  html = html.replace(/^# (.*$)/gim, "<h1>$1</h1>");

  // Bold
  html = html.replace(/\*\*(.*?)\*\*/g, "<strong>$1</strong>");
  html = html.replace(/__(.*?)__/g, "<strong>$1</strong>");

  // Italic
  html = html.replace(/\*(.*?)\*/g, "<em>$1</em>");
  html = html.replace(/_(.*?)_/g, "<em>$1</em>");

  // Code blocks
  html = html.replace(/```(.*?)```/gs, "<pre><code>$1</code></pre>");

  // Inline code
  html = html.replace(/`(.*?)`/g, "<code>$1</code>");

  // Links
  html = html.replace(
    /\[(.*?)\]\((.*?)\)/g,
    '<a href="$2" target="_blank">$1</a>'
  );

  // Horizontal rules
  html = html.replace(/^---$/gm, "<hr>");
  html = html.replace(/^\*\*\*$/gm, "<hr>");

  // Lists
  const lines = html.split("\n");
  let inList = false;
  let listType = null;
  let result = [];

  for (let i = 0; i < lines.length; i++) {
    const line = lines[i];

    // Unordered list
    if (line.match(/^[\-\*\+] /)) {
      if (!inList || listType !== "ul") {
        if (inList) result.push(`</${listType}>`);
        result.push("<ul>");
        inList = true;
        listType = "ul";
      }
      result.push("<li>" + line.replace(/^[\-\*\+] /, "") + "</li>");
    }
    // Ordered list
    else if (line.match(/^\d+\. /)) {
      if (!inList || listType !== "ol") {
        if (inList) result.push(`</${listType}>`);
        result.push("<ol>");
        inList = true;
        listType = "ol";
      }
      result.push("<li>" + line.replace(/^\d+\. /, "") + "</li>");
    } else {
      if (inList) {
        result.push(`</${listType}>`);
        inList = false;
        listType = null;
      }
      result.push(line);
    }
  }

  if (inList) {
    result.push(`</${listType}>`);
  }

  html = result.join("\n");

  // Paragraphs
  html = html.replace(/\n\n+/g, "</p><p>");
  html = html.replace(/\n/g, "<br>");

  // Wrap in paragraphs if not already wrapped
  if (!html.startsWith("<")) {
    html = "<p>" + html + "</p>";
  }

  return html;
}

// ============================================
// UI Helper Functions
// ============================================

/**
 * Switch between tabs
 */
function switchTab(tabName) {
  tabButtons.forEach((btn) => {
    btn.classList.remove("active");
    if (btn.dataset.tab === tabName) {
      btn.classList.add("active");
    }
  });

  tabPanes.forEach((pane) => {
    pane.classList.remove("active");
    if (pane.id === `${tabName}-tab`) {
      pane.classList.add("active");
    }
  });
}

/**
 * Show/hide loading overlay
 */
function showLoading(show) {
  if (show) {
    loadingOverlay.classList.add("active");
    generateBtn.disabled = true;
    generateBtn.innerHTML =
      '<i class="fas fa-spinner fa-spin"></i> Generating...';
  } else {
    loadingOverlay.classList.remove("active");
    generateBtn.disabled = false;
    generateBtn.innerHTML = '<i class="fas fa-rocket"></i> Generate Brochure';
  }
}

/**
 * Show/hide progress bar
 */
function showProgress(show, text = "") {
  if (show) {
    progressContainer.style.display = "block";
    progressText.textContent = text;
    setProgress(0);
  } else {
    progressContainer.style.display = "none";
  }
}

/**
 * Set progress bar percentage
 */
function setProgress(percent) {
  progressFill.style.width = `${percent}%`;
}

/**
 * Show toast notification
 */
function showToast(message, type = "success") {
  toastMessage.textContent = message;

  // Set color based on type
  if (type === "error") {
    toast.style.background = "#ef4444";
    toast.innerHTML =
      '<i class="fas fa-exclamation-circle"></i><span id="toast-message">' +
      message +
      "</span>";
  } else if (type === "warning") {
    toast.style.background = "#f59e0b";
    toast.innerHTML =
      '<i class="fas fa-exclamation-triangle"></i><span id="toast-message">' +
      message +
      "</span>";
  } else {
    toast.style.background = "#10b981";
    toast.innerHTML =
      '<i class="fas fa-check-circle"></i><span id="toast-message">' +
      message +
      "</span>";
  }

  toast.classList.add("show");

  setTimeout(() => {
    toast.classList.remove("show");
  }, 3000);
}

// ============================================
// Utility Functions
// ============================================

/**
 * Sanitize filename
 */
function sanitizeFilename(name) {
  return name.replace(/[^a-z0-9]/gi, "_").toLowerCase();
}

/**
 * Download file
 */
function downloadFile(content, filename, mimeType) {
  const blob = new Blob([content], { type: mimeType });
  const url = URL.createObjectURL(blob);
  const link = document.createElement("a");
  link.href = url;
  link.download = filename;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
  URL.revokeObjectURL(url);
}

/**
 * Generate full HTML document
 */
function generateFullHTML(content, companyName) {
  return `<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>${companyName} - Company Brochure</title>
    <style>
        body {
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            line-height: 1.8;
            max-width: 900px;
            margin: 0 auto;
            padding: 40px 20px;
            color: #333;
            background: #f8f9fa;
        }
        h1 {
            color: #6366f1;
            border-bottom: 3px solid #6366f1;
            padding-bottom: 10px;
            margin-top: 0;
        }
        h2 {
            color: #6366f1;
            margin-top: 2em;
        }
        h3 {
            color: #4f46e5;
        }
        strong {
            color: #6366f1;
            font-weight: 700;
        }
        a {
            color: #6366f1;
            text-decoration: none;
        }
        a:hover {
            text-decoration: underline;
        }
        hr {
            border: none;
            border-top: 2px solid #e5e7eb;
            margin: 2em 0;
        }
        ul, ol {
            margin-left: 2em;
        }
        li {
            margin-bottom: 0.5em;
        }
        code {
            background: #f1f5f9;
            padding: 2px 6px;
            border-radius: 3px;
            font-family: 'Courier New', monospace;
        }
        pre {
            background: #1e293b;
            color: #e2e8f0;
            padding: 15px;
            border-radius: 8px;
            overflow-x: auto;
        }
        pre code {
            background: none;
            padding: 0;
            color: inherit;
        }
    </style>
</head>
<body>
    ${content}
    <hr>
    <footer style="text-align: center; color: #64748b; margin-top: 40px;">
        <p>Generated by AI Brochure Generator</p>
    </footer>
</body>
</html>`;
}

// ============================================
// Initialize
// ============================================
document.addEventListener("DOMContentLoaded", () => {
  console.log("AI Brochure Generator initialized");

  // Test toast
  console.log("Application ready!");
});
