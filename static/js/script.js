// ============================================
// Global Variables
// ============================================
let currentBrochureContent = "";
let currentCompanyName = "";
let selectedAnimation = "fade";

// ============================================
// DOM Elements
// ============================================
const form = document.getElementById("brochure-form");
const generateBtn = document.getElementById("generate-btn");
const clearBtn = document.getElementById("clear-btn");
const companyNameInput = document.getElementById("company-name");
const companyUrlInput = document.getElementById("company-url");
const progressContainer = document.getElementById("progress-container");
const progressFill = document.getElementById("progress-fill");
const progressText = document.getElementById("progress-text");
const outputSection = document.getElementById("output-section");
const brochurePreview = document.getElementById("brochure-preview");
const markdownContent = document.getElementById("markdown-content");
const loadingOverlay = document.getElementById("loading-overlay");
const toast = document.getElementById("toast");
const toastMessage = document.getElementById("toast-message");

// Action buttons
const downloadPdfBtn = document.getElementById("download-pdf-btn");

// Template and animation buttons
const animationBtns = document.querySelectorAll(".animation-btn");

let currentPreviewHtml = "";

// ============================================
// Event Listeners
// ============================================

// Animation selection
animationBtns.forEach((btn) => {
  btn.addEventListener("click", () => {
    animationBtns.forEach((b) => b.classList.remove("active"));
    btn.classList.add("active");
    selectedAnimation = btn.dataset.animation;
    showToast(
      `${
        selectedAnimation.charAt(0).toUpperCase() + selectedAnimation.slice(1)
      } animation selected`,
      "success"
    );
  });
});

// Form submission
form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const companyName = companyNameInput.value.trim();
  let url = companyUrlInput.value.trim();

  // Validation
  if (!companyName || !url) {
    showToast("Please fill in all fields", "error");
    return;
  }

  // Add https:// if not present
  if (!url.startsWith("http://") && !url.startsWith("https://")) {
    url = "https://" + url;
    companyUrlInput.value = url;
  }

  currentCompanyName = companyName;

  // Always generate without streaming (direct preview)
  await generateBrochure(companyName, url);
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

// Download as PDF
// Download as PDF - Client-side generation
// Download as PDF - Best Quality (Browser Print)
// Download as PDF - High Quality Version
downloadPdfBtn.addEventListener("click", async () => {
  if (!brochurePreview.innerHTML) {
    showToast("No content to download", "error");
    return;
  }

  try {
    showLoading(true);
    showToast("Generating high-quality PDF...", "warning");

    // Get the iframe
    const iframe = brochurePreview.querySelector("iframe");

    if (!iframe || !iframe.contentDocument) {
      throw new Error("Brochure content not found");
    }

    // Get the content from iframe
    const iframeBody = iframe.contentDocument.body;
    const iframeDoc = iframe.contentDocument;

    // Create a temporary container with better styling
    const tempContainer = document.createElement("div");
    tempContainer.style.width = "210mm"; // A4 width
    tempContainer.style.background = "white";
    tempContainer.style.padding = "0";
    tempContainer.style.margin = "0";
    tempContainer.innerHTML = iframeBody.innerHTML;

    // Copy styles from iframe
    const iframeStyles = iframeDoc.querySelectorAll("style");
    iframeStyles.forEach((style) => {
      const newStyle = document.createElement("style");
      newStyle.textContent = style.textContent;
      tempContainer.appendChild(newStyle);
    });

    // Append to body (hidden but visible for rendering)
    tempContainer.style.position = "absolute";
    tempContainer.style.left = "-9999px";
    tempContainer.style.top = "0";
    document.body.appendChild(tempContainer);

    // Wait for images to load
    const images = tempContainer.querySelectorAll("img");
    await Promise.all(
      Array.from(images).map((img) => {
        if (img.complete) return Promise.resolve();
        return new Promise((resolve) => {
          img.onload = resolve;
          img.onerror = resolve;
        });
      })
    );

    // Generate canvas with higher quality
    const canvas = await html2canvas(tempContainer, {
      scale: 3, // Higher scale for better quality (was 2)
      useCORS: true,
      allowTaint: true,
      logging: false,
      backgroundColor: "#ffffff",
      windowWidth: 1200,
      windowHeight: tempContainer.scrollHeight,
      imageTimeout: 15000,
      removeContainer: false,
    });

    // Remove temporary container
    document.body.removeChild(tempContainer);

    // Create PDF with better settings
    const { jsPDF } = window.jspdf;
    const imgWidth = 210; // A4 width in mm
    const pageHeight = 297; // A4 height in mm
    const imgHeight = (canvas.height * imgWidth) / canvas.width;
    let heightLeft = imgHeight;
    let position = 0;

    const pdf = new jsPDF("p", "mm", "a4", true); // true for better compression

    // Use better quality image
    const imgData = canvas.toDataURL("image/jpeg", 0.95); // Higher quality (was 1.0)

    // Add first page
    pdf.addImage(imgData, "JPEG", 0, position, imgWidth, imgHeight, "", "FAST");
    heightLeft -= pageHeight;

    // Add additional pages if needed
    while (heightLeft > 0) {
      position = heightLeft - imgHeight;
      pdf.addPage();
      pdf.addImage(
        imgData,
        "JPEG",
        0,
        position,
        imgWidth,
        imgHeight,
        "",
        "FAST"
      );
      heightLeft -= pageHeight;
    }

    // Download PDF
    const filename = `${sanitizeFilename(currentCompanyName)}_brochure.pdf`;
    pdf.save(filename);

    showToast("High-quality PDF downloaded! ✓", "success");
  } catch (error) {
    console.error("Error generating PDF:", error);
    showToast("Failed to generate PDF: " + error.message, "error");
  } finally {
    showLoading(false);
  }
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
    showProgress(true, "Analyzing website and extracting colors...");
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
    progressText.textContent = "Generating brochure content...";

    if (!response.ok) {
      const errorData = await response.json();
      throw new Error(errorData.error || "Server error");
    }

    const data = await response.json();
    console.log("Response received:", data);

    if (data.success) {
      setProgress(90);
      progressText.textContent = "Creating interactive brochure...";

      // Save the markdown content
      currentBrochureContent = data.markdown;

      // Generate interactive HTML
      await generateAndDisplayInteractive(companyName, url, data.markdown);

      setProgress(100);
      progressText.textContent = "Complete!";

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
 * Generate interactive HTML and display it
 */
async function generateAndDisplayInteractive(
  companyName,
  companyUrl,
  markdownContent
) {
  try {
    // Generate interactive HTML
    const response = await fetch("/generate-interactive-html", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        markdown: markdownContent,
        company_name: companyName,
        company_url: companyUrl,
        animation_style: "none",
        template_style: "professional",
      }),
    });

    if (!response.ok) {
      throw new Error("Failed to generate interactive brochure");
    }

    const data = await response.json();

    if (data.success) {
      // Display the interactive HTML directly in an iframe
      displayInteractiveBrochure(data.html, markdownContent);
    } else {
      throw new Error(data.error || "Failed to generate");
    }
  } catch (error) {
    console.error("Error generating interactive HTML:", error);
    // Fallback to simple HTML preview
    const simpleHtml = markdownToHTML(markdownContent);
    displayBrochure(simpleHtml, markdownContent);
  }
}

/**
 * Display the interactive brochure in an iframe
 */
function displayInteractiveBrochure(htmlContent, markdown) {
  console.log("Displaying interactive brochure");

  // Store markdown content for downloads
  markdownContent.textContent = markdown;

  // Create an iframe to display the interactive brochure
  const iframe = document.createElement("iframe");
  iframe.style.width = "100%";
  iframe.style.height = "800px";
  iframe.style.border = "none";
  iframe.style.borderRadius = "15px";
  iframe.style.boxShadow = "0 10px 30px rgba(0,0,0,0.1)";

  // Clear previous content
  brochurePreview.innerHTML = "";
  brochurePreview.appendChild(iframe);

  // Write the HTML content to the iframe
  iframe.contentDocument.open();
  iframe.contentDocument.write(htmlContent);
  iframe.contentDocument.close();

  // Show the output section
  outputSection.style.display = "block";

  // Scroll to output section
  setTimeout(() => {
    outputSection.scrollIntoView({ behavior: "smooth", block: "start" });
  }, 100);
}

// ============================================
// Display Functions
// ============================================

/**
 * Display the generated brochure (fallback)
 */
function displayBrochure(html, markdown) {
  console.log("Displaying brochure (fallback)");
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
});
