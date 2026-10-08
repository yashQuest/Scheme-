/**
 * eligibility.js
 * Interactive Multi-Step Eligibility Wizard & AI Assistant Controller
 */

document.addEventListener("DOMContentLoaded", function () {
    const model1 = document.querySelector("#popup1");
    const model2 = document.querySelector("#popup2");
    const model3 = document.querySelector("#popup3");
    const model4 = document.querySelector("#popup4");
    const model5 = document.querySelector("#popup5");

    const cancelButtons = document.querySelectorAll(".but1_1");
    const nextButtons = document.querySelectorAll(".but2_1");
    const eligibilityBtn = document.querySelector("#but_eli");
    const stepperContainer = document.querySelector("#stepper-container");

    const models = [model1, model2, model3, model4, model5];
    const stepNodes = document.querySelectorAll(".step-node");
    let currentStep = 0;

    // AI Sample Prompt Chips Insertion
    const promptChips = document.querySelectorAll(".sample-prompt-chip");
    const aiTextarea = document.querySelector("#ai-prompt-textarea");

    if (promptChips && aiTextarea) {
        promptChips.forEach(chip => {
            chip.addEventListener("click", function () {
                aiTextarea.value = this.getAttribute("data-prompt") || this.innerText;
                aiTextarea.focus();
            });
        });
    }

    function updateStepperUI(activeIndex) {
        stepNodes.forEach((node, idx) => {
            if (idx < activeIndex) {
                node.classList.add("completed");
                node.classList.remove("active");
            } else if (idx === activeIndex) {
                node.classList.add("active");
                node.classList.remove("completed");
            } else {
                node.classList.remove("active", "completed");
            }
        });
    }

    function showStep(stepIndex) {
        models.forEach((m, idx) => {
            if (m) {
                if (idx === stepIndex) {
                    m.style.display = "block";
                } else {
                    m.style.display = "none";
                }
            }
        });
        updateStepperUI(stepIndex);
        if (stepperContainer) {
            stepperContainer.style.display = "block";
            stepperContainer.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    // Launch Wizard
    if (eligibilityBtn) {
        eligibilityBtn.addEventListener("click", function (event) {
            event.preventDefault();
            currentStep = 0;
            showStep(0);
        });
    }

    // Input Validation per Step
    function validateStep(stepIndex) {
        if (!models[stepIndex]) return true;
        const inputs = models[stepIndex].querySelectorAll("input, select, textarea");
        for (let input of inputs) {
            if (!input.checkValidity()) {
                input.reportValidity();
                return false;
            }
        }
        return true;
    }

    // Handle Next Step Navigation
    nextButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();

            if (!validateStep(currentStep)) {
                return;
            }

            if (currentStep < models.length - 1) {
                currentStep++;
                showStep(currentStep);
            }
        });
    });

    // Handle Back / Cancel Navigation
    cancelButtons.forEach(button => {
        button.addEventListener("click", function (event) {
            event.preventDefault();

            if (currentStep === 0) {
                if (model1) model1.style.display = "none";
                if (stepperContainer) stepperContainer.style.display = "none";
            } else if (currentStep > 0) {
                currentStep--;
                showStep(currentStep);
            }
        });
    });
});